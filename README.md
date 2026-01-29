# SmartSubmit Hybrid MCP Agent

A dual-mode AI agent for University Lab submissions, powered by **FastMCP** (Claude Desktop) and **FastAPI** (WhatsApp).

## Features
- **File Listing**: Scans `~/Documents/University` (or CWD) for reports.
- **Deadline Check**: Connects to Canvas/LMS to fetch upcoming assignments.
- **Submission**: Uploads files to assignments with verification.
- **Dual Interface**:
  - **Claude Desktop**: Native MCP tool support.
  - **WhatsApp**: Interaction via Twilio Webhook.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   (Or manually: `pip install fastmcp fastapi uvicorn python-dotenv httpx python-multipart twilio`)

2. **Configuration**
   - Copy `.env.example` to `.env` and fill in your details:
     - `LMS_API_KEY`: Your Canvas Token.
     - `WHATSAPP_ALLOWED_NUMBER`: Your phone number (e.g., `+1234567890`).

3. **Running the Agent**

   ### Mode A: Claude Desktop (MCP)
   - Ensure `claude_desktop_config.json` is configured.
   - Restart Claude Desktop. The "SmartSubmit" server should appear.

   ### Mode B: WhatsApp (Webhook)
   1. Start the server:
      ```bash
      uvicorn webhook:app --reload
      ```
   2. Expose to internet (for Twilio):
      ```bash
      ngrok http 8000
      ```
   3. Configure Twilio Sandbox:
      - Set the "When a message comes in" URL to `https://<your-ngrok-url>/whatsapp`.

## Logs
Check `student_agent.log` for activity traces.
