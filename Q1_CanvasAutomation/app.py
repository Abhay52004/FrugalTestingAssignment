import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import os

app = FastAPI()

# Path to index.html
INDEX_HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Step 1: Wait 2 seconds to simulate a slow connection (loading state)
        await asyncio.sleep(2.0)
        
        # Step 2: Stream active state coordinates and balance payload
        active_payload = {
            "status": "ACTIVE",
            "x": 160,
            "y": 180,
            "balance": 500
        }
        await websocket.send_text(json.dumps(active_payload))
        
        # Keep connection open and listen for user input
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action")
            
            if action == "DRAG_COMPLETE":
                print(f"Server received DRAG_COMPLETE: newX={payload.get('newX')}")
            elif action == "CLICK_COMPLETE":
                print("Server received CLICK_COMPLETE: Transaction Finalized!")
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
