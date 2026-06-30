from fastapi import FastAPI, Header, HTTPException, Request, Response, status
import hmac
import hashlib
import time
import uuid

app = FastAPI()

# Shared configurations
SALT = "FrugalTestingSalt2026"
transaction_store = {}  # Store transactions and their challenge nonces
processed_signatures = {}  # Store processed X-Frugal-Mac signatures to detect replays
vulnerability_mode = False # If True, disables replay check to simulate vulnerability

@app.post("/transaction")
async def create_transaction(response: Response):
    tx_id = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    server_timestamp = int(time.time() * 1000000) # microsecond timestamp
    
    # Store challenge info
    transaction_store[tx_id] = {
        "nonce": nonce,
        "timestamp": server_timestamp,
        "status": "CREATED"
    }
    
    response.headers["X-Transaction-ID"] = tx_id
    return {
        "nonce": nonce,
        "server_timestamp": server_timestamp
    }

@app.post("/toggle-vulnerability")
async def toggle_vulnerability(enable: bool):
    global vulnerability_mode
    vulnerability_mode = enable
    return {"replay_vulnerability_active": vulnerability_mode}

@app.put("/transaction/{tx_id}")
async def update_transaction(
    tx_id: str,
    request: Request,
    x_frugal_mac: str = Header(None, alias="X-Frugal-Mac"),
    x_timestamp: str = Header(None, alias="X-Timestamp")
):
    if tx_id not in transaction_store:
        raise HTTPException(status_code=404, detail="Transaction not found.")
        
    if not x_frugal_mac or not x_timestamp:
        raise HTTPException(status_code=400, detail="Missing security headers X-Frugal-Mac or X-Timestamp.")
        
    # Read raw body
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8")
    
    # 1. Verify cryptographic signature (HMAC-SHA512)
    # The message is formed by: raw_body + timestamp_str + salt
    expected_msg = (body_str + x_timestamp + SALT).encode("utf-8")
    hmac_obj = hmac.new(SALT.encode("utf-8"), expected_msg, hashlib.sha512)
    expected_mac = hmac_obj.hexdigest()
    
    if not hmac.compare_digest(x_frugal_mac, expected_mac):
        raise HTTPException(status_code=401, detail="Invalid cryptographic signature.")
        
    # 2. Verify Replay Attack
    # Check if signature has already been processed (replay check)
    if not vulnerability_mode:
        if x_frugal_mac in processed_signatures:
            last_seen = processed_signatures[x_frugal_mac]
            now = time.time()
            # If request is resent within short window (e.g. 5 seconds), reject as replay
            if now - last_seen < 5.0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Replay attack detected. Request signature has already been processed."
                )
        
        # Save signature with timestamp
        processed_signatures[x_frugal_mac] = time.time()
        
    # Update transaction state
    transaction_store[tx_id]["status"] = "UPDATED"
    transaction_store[tx_id]["body"] = body_str
    
    return {
        "status": "SUCCESS",
        "detail": "Transaction updated successfully."
    }
