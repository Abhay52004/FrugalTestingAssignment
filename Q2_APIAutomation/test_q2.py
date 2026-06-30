import requests
import hmac
import hashlib
import time
import json
import subprocess
import sys
import os

SALT = "FrugalTestingSalt2026"
BASE_URL = "http://localhost:8001"

def start_api_server():
    print("Starting FastAPI API server for Q2...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "Q2_APIAutomation.app_api:app", "--port", "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1.5) # Wait for server to boot
    return process

def test_replay_protection():
    server_process = start_api_server()
    
    try:
        # Step 1: Create transaction wrapper (POST)
        print("\n--- Step 1: Initiating Transaction (POST) ---")
        res_post = requests.post(f"{BASE_URL}/transaction")
        res_post.raise_for_status()
        
        tx_id = res_post.headers.get("X-Transaction-ID")
        body_post = res_post.json()
        nonce = body_post["nonce"]
        server_ts = body_post["server_timestamp"]
        
        print(f"Transaction ID: {tx_id}")
        print(f"Server Nonce: {nonce}")
        print(f"Server Timestamp: {server_ts}")
        
        # Step 2: Update transaction (PUT) with HMAC signature
        print("\n--- Step 2: Updating Transaction (PUT) ---")
        payload = {"amount": 5000, "currency": "INR", "status": "authorized"}
        payload_str = json.dumps(payload)
        
        # Generate microsecond timestamp for headers
        microsecond_ts = str(int(time.time() * 1000000))
        
        # Calculate HMAC-SHA512: message = payload_str + timestamp_str + salt
        expected_msg = (payload_str + microsecond_ts + SALT).encode("utf-8")
        hmac_obj = hmac.new(SALT.encode("utf-8"), expected_msg, hashlib.sha512)
        signature = hmac_obj.hexdigest()
        
        headers = {
            "X-Timestamp": microsecond_ts,
            "X-Frugal-Mac": signature,
            "Content-Type": "application/json"
        }
        
        # Send PUT
        start_put_time = time.time()
        res_put1 = requests.put(f"{BASE_URL}/transaction/{tx_id}", data=payload_str, headers=headers)
        put_duration = (time.time() - start_put_time) * 1000
        print(f"Initial PUT response: {res_put1.status_code} {res_put1.json()} (took {put_duration:.2f}ms)")
        assert res_put1.status_code == 200
        
        # Step 3: Duplicate and resend payload within 150ms (Replay Attack)
        print("\n--- Step 3: Executing Replay Attack (within 150ms) ---")
        time.sleep(0.05) # wait 50ms (well under 150ms)
        
        res_put2 = requests.put(f"{BASE_URL}/transaction/{tx_id}", data=payload_str, headers=headers)
        print(f"Replayed PUT response: {res_put2.status_code}")
        
        # Assert that backend correctly handles replay payload
        if res_put2.status_code == 409:
            print("[SUCCESS] Backend correctly rejected the replay attack with HTTP 409 Conflict.")
        elif res_put2.status_code in [200, 201]:
            # Throw high-risk data-mutation vulnerability alert in logs
            alert_msg = f"[CRITICAL VULNERABILITY ALERT] Replay safety boundary breached! Duplicated success code {res_put2.status_code} returned."
            print(alert_msg)
            raise ValueError(alert_msg)
        else:
            print(f"Received unexpected response code: {res_put2.status_code}")
            assert res_put2.status_code == 409
            
        # Step 4: Test Vulnerability Alert (Replay protection disabled)
        print("\n--- Step 4: Simulating Vulnerability Mode ---")
        # Toggle vulnerability on the server
        requests.post(f"{BASE_URL}/toggle-vulnerability?enable=true")
        
        # Run a new transaction
        res_post2 = requests.post(f"{BASE_URL}/transaction")
        tx_id2 = res_post2.headers.get("X-Transaction-ID")
        
        # First PUT on new transaction
        microsecond_ts2 = str(int(time.time() * 1000000))
        expected_msg2 = (payload_str + microsecond_ts2 + SALT).encode("utf-8")
        signature2 = hmac.new(SALT.encode("utf-8"), expected_msg2, hashlib.sha512).hexdigest()
        headers2 = {"X-Timestamp": microsecond_ts2, "X-Frugal-Mac": signature2, "Content-Type": "application/json"}
        
        res_put1_v = requests.put(f"{BASE_URL}/transaction/{tx_id2}", data=payload_str, headers=headers2)
        assert res_put1_v.status_code == 200
        
        # Replay PUT on new transaction
        res_put2_v = requests.put(f"{BASE_URL}/transaction/{tx_id2}", data=payload_str, headers=headers2)
        
        if res_put2_v.status_code in [200, 201]:
            # Correctly raise high-risk data-mutation vulnerability alert
            alert_msg = f"\n[CRITICAL VULNERABILITY ALERT] Replay attack succeeded on transaction {tx_id2}! The server allowed duplicate data modification."
            print(alert_msg)
        else:
            print("Server still rejected the replay, this shouldn't happen in vulnerability mode.")
            
    finally:
        server_process.terminate()
        server_process.wait()
        print("API server stopped.")

if __name__ == "__main__":
    test_replay_protection()
