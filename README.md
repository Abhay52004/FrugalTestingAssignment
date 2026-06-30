# Frugal Testing & BuildNexTech AI-Native Software Engineer Intern Assignment

This repository contains the complete implementation and responses for the Frugal Testing & BuildNexTech AI-Native Software Engineer Intern evaluation.

---

## Repository Structure

```
aiproject/
│
├── Q1_CanvasAutomation/
│   ├── app.py              # FastAPI server + WebSocket streaming
│   ├── index.html          # HTML5 Canvas stock UI with dynamic grid rendering
│   └── test_q1.py          # Playwright test with canvas color polling & race interception
│
├── Q2_APIAutomation/
│   ├── app_api.py          # FastAPI mock API with transaction ID, nonces, & HMAC
│   └── test_q2.py          # API test verifying signature & replay protection
│
├── Q3_ShadowDOM/
│   ├── shadow_dom_piercer.js # JS snippet to pierce closed & open Shadow DOMs
│   └── cot_system_prompt.txt # Expert CoT prompt for Accessibility Tree navigation
│
├── compile_pdf.py          # Script to generate a styled HTML/PDF report of written answers
│
├── Answers.md              # Consolidated answers for Section 0, Section B (Q4-Q20), Situations A-D
│
├── Article.md              # 1000-word Markdown article for Q21 (Topic B)
│
├── Portfolio_VideoCV.md    # Portfolio links layout (Q22) & Video CV script (Q23)
│
├── FrugalTestingAssignment_AbhayKumar.html # Compiled responsive report
│
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation & execution instructions
```

---

## Installation & Setup

1. **Install Python Packages**:
   Ensure you have Python 3.8+ installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

---

## Running the Automation Suite

### Q1. Dynamic HTML5 Canvas State Drifts & Asynchronous Race Interceptions
The Q1 automation runs against a local web app rendering a Canvas and utilizing standard WebSockets. The test:
- Intercepts incoming WebSocket frames and injects a scaling Fibonacci delay model.
- Polles pixel-color updates via `requestAnimationFrame` on the canvas rendering context.
- Fires rapid chained actions (hover, drag 15px, click) within 30ms - 100ms.
- Asserts that mismatched server boundary payloads (e.g. `1e+7` float) trigger the client-side exception boundary.

To run:
```bash
pytest Q1_CanvasAutomation/test_q1.py -s
```

### Q2. Cryptographic Replay Testing, Stateful Nonces & Hash-Chain API Chaining
The Q2 automation uses a local FastAPI server to simulate transactions requiring signature verification and replay prevention. The test:
- Initiates a transaction (POST) and extracts the transaction ID wrapper from headers.
- Updates the transaction (PUT) by generating a microsecond timestamp and calculating an `X-Frugal-Mac` header (HMAC-SHA512 of `body + timestamp + salt`).
- Resends the identical payload and headers within 150ms to verify that the backend rejects it with HTTP 409 Conflict.
- Toggles the server into "vulnerability mode" (replay check disabled), replays the transaction, and throws a critical warning when the server allows the duplicate data modification.

To run:
```bash
python Q2_APIAutomation/test_q2.py
```

---

## Compiling the Written Responses

The written answers, technical article, portfolio, and Video CV script are consolidated into a single responsive HTML file. This file uses modern typography, HSL-tailored colors, and print stylesheets, making it easy to open in a browser and "Print to PDF".

To compile:
```bash
python compile_pdf.py
```
Open `FrugalTestingAssignment_AbhayKumar.html` in any web browser to view, or export to PDF via the print menu.
