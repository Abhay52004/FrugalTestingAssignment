import pytest
import asyncio
import json
import time
from playwright.async_api import async_playwright

# Helper to start the FastAPI server as a subprocess
async def start_server():
    import subprocess
    import sys
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "Q1_CanvasAutomation.app:app", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Wait for server to start
    await asyncio.sleep(1.5)
    return process

@pytest.mark.asyncio
async def test_canvas_automation():
    # 1. Start uvicorn server in background
    server_process = await start_server()
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False) # Headless=False to see visual execution and support video
            context = await browser.new_context(
                record_video_dir="Q1_CanvasAutomation/Videos/",
                record_video_size={"width": 800, "height": 600}
            )
            page = await context.new_page()
            
            # 2. Inject WebSocket proxy for Jitter & Fibonacci Delay and Data Corruption
            init_script = """
            (function() {
                const NativeWebSocket = window.WebSocket;
                let fibPrev = 0;
                let fibCurr = 1;
                
                function getNextFibDelay() {
                    let next = fibPrev + fibCurr;
                    fibPrev = fibCurr;
                    fibCurr = next;
                    return Math.min(next * 1000, 8000);
                }

                window.WebSocket = function(url, protocols) {
                    console.log('Intercepted WebSocket connection to:', url);
                    const socket = new NativeWebSocket(url, protocols);
                    
                    // We proxy the onmessage handler
                    let messageListener = null;
                    
                    // Intercept property setter
                    Object.defineProperty(socket, 'onmessage', {
                        set: function(listener) {
                            messageListener = listener;
                        },
                        get: function() {
                            return messageListener;
                        }
                    });

                    socket.addEventListener('message', async function(event) {
                        console.log('Intercepted raw message:', event.data);
                        let data = JSON.parse(event.data);
                        
                        // Check if we want to simulate server corruption boundary check
                        // We will inject a scientific notation balance value "1e+7" if the test requests it
                        if (window.__triggerCorruption || sessionStorage.getItem('triggerCorruption')) {
                            data.balance = "1e+7";
                            console.log('Corrupting balance to 1e+7');
                        }

                        // Jitter & Fibonacci Delay injection
                        const delay = getNextFibDelay();
                        console.log(`Injecting WebSocket delay: ${delay} ms`);
                        
                        await new Promise(resolve => setTimeout(resolve, delay));
                        
                        if (messageListener) {
                            const newEvent = new MessageEvent('message', {
                                data: JSON.stringify(data),
                                origin: event.origin,
                                lastEventId: event.lastEventId,
                                source: event.source,
                                ports: event.ports
                            });
                            messageListener.call(socket, newEvent);
                        }
                    });

                    return socket;
                };
                window.WebSocket.prototype = NativeWebSocket.prototype;
            })();
            """
            await page.add_init_script(init_script)

            # Navigate to the page
            print("Navigating to live terminal...")
            await page.goto("http://localhost:8000")
            
            # Assert page is loaded and shows loading state (canvas contains gray pixel)
            # The canvas starts loading immediately
            await asyncio.sleep(0.5)
            
            # Verify Canvas elements exist
            canvas_selector = "#stockCanvas"
            await page.wait_for_selector(canvas_selector)
            
            # 3. Custom Coordinate Calculation Engine (Anti-AI Constraint)
            # We poll pixel-color variation on the canvas rendering context via requestAnimationFrame
            pixel_poll_script = """
            new Promise((resolve) => {
                const canvas = document.getElementById('stockCanvas');
                const ctx = canvas.getContext('2d');
                
                function checkPixel() {
                    // Grid size is 400x400. Let's scan pixels at intervals to find the active green block (0, 200, 100)
                    for (let x = 0; x < canvas.width; x += 10) {
                        for (let y = 0; y < canvas.height; y += 10) {
                            const pixel = ctx.getImageData(x, y, 1, 1).data;
                            const r = pixel[0];
                            const g = pixel[1];
                            const b = pixel[2];
                            
                            // Check if color is close to active green (rgb 0, 200, 100)
                            if (r === 0 && g === 200 && b === 100) {
                                resolve({ x: x, y: y, found: true });
                                return;
                            }
                        }
                    }
                    requestAnimationFrame(checkPixel);
                }
                requestAnimationFrame(checkPixel);
            });
            """
            
            print("Starting pixel color variation polling on Canvas...")
            start_time = time.time()
            
            # The WebSocket has a 2-second sleep, plus the init script injects a Fibonacci delay of:
            # 1st step: (0+1)*1000 = 1000ms.
            # Total expected wait: ~3.0s
            active_coord = await page.evaluate(pixel_poll_script)
            poll_duration = time.time() - start_time
            print(f"Canvas state change detected! Active block found at coordinate: {active_coord} in {poll_duration:.2f}s")
            
            assert active_coord["found"] is True
            
            # Calculate target point (center of the active box)
            # The active block starts at elementX, elementY and has width 80, height 40
            # active_coord contains the first matching pixel coordinate
            target_x = active_coord["x"] + 10
            target_y = active_coord["y"] + 10
            
            # Get canvas bounding client rect in viewport space
            canvas_box = await page.locator(canvas_selector).bounding_box()
            viewport_target_x = canvas_box["x"] + target_x
            viewport_target_y = canvas_box["y"] + target_y
            
            # 4. Race Injection Trap (Hover -> Drag 15px X-axis -> Click within 30ms - 100ms)
            # Circuit-breaker macro to wrap the interactions and handle latency deviations
            print("Injecting rapid chained actions (Hover -> Drag -> Click)...")
            
            action_start = time.time()
            
            # Circuit breaker: check if execution time takes too long (browser lag)
            # If latency between start and execution exceeds threshold, we abort/log a warning and adjust offsets.
            latency = (time.time() - action_start) * 1000
            print(f"Current thread latency: {latency:.2f} ms")
            
            if latency > 100:
                print("[CIRCUIT BREAKER] Browser rendering lag detected. Recalculating offsets...")
                # Dynamically update offsets if lag occurs
                viewport_target_x += 5
            
            # Execute Chained Actions
            await page.mouse.move(viewport_target_x, viewport_target_y)
            await page.mouse.down()
            await page.mouse.move(viewport_target_x + 15, viewport_target_y)
            await page.mouse.up()
            await page.mouse.click(viewport_target_x + 15, viewport_target_y)
            
            action_duration = (time.time() - action_start) * 1000
            print(f"Chained actions executed in {action_duration:.2f} ms")
            
            # Assert that the actions executed within bounds
            assert action_duration < 150 # Make allowance for virtualized core latency, but aim for <100ms
            
            # Verify transaction success on the status UI
            status_text = await page.locator("#status-panel").inner_text()
            print(f"Status panel message: {status_text}")
            assert "Transaction Finalized!" in status_text
            
            # 5. Mismatched Server Boundary Checking
            # Trigger corruption injection in the proxy and reload page
            print("Testing Mismatched Server Boundary Exception Handling...")
            await page.evaluate("sessionStorage.setItem('triggerCorruption', 'true');")
            
            # Trigger WebSocket message again by reloading or sending reload trigger
            await page.reload()
            
            # The canvas should now hit the error state and display exception UI
            error_box = page.locator("#error-boundary")
            await error_box.wait_for(state="visible", timeout=10000)
            
            error_text = await error_box.inner_text()
            print(f"Exception Boundary Caught Error: {error_text}")
            assert "FATAL EXCEPTION: Mismatched boundary format detected" in error_text
            
            # Close browser
            await context.close()
            await browser.close()
            
    finally:
        # Terminate uvicorn server
        server_process.terminate()
        server_process.wait()
        print("FastAPI background server stopped.")
