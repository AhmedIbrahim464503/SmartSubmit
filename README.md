# SmartSubmit - NUST Edition (Moodle)

A dual-mode AI agent for **NUST LMS (Moodle)** submissions, powered by **FastMCP** (Claude Desktop) and **FastAPI** (WhatsApp).

## Features
- **File Listing**: Scans `~/Documents/University` (or CWD) for reports.
- **Deadline Check**: Connects to **lms.nust.edu.pk** to fetch upcoming Moodle events.
- **Submission**: Prepares files for Moodle assignments.
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
   - Copy `.env.example` to `.env`.
   - **MOODLE_TOKEN**:
     - Go to `lms.nust.edu.pk` > Profile > Preferences > Security Keys.
     - Generate a key for "Moodle mobile web service".
   - **WHATSAPP_ALLOWED_NUMBER**: Your phone number.

3. **Running the Agent**

   ### Mode A: Claude Desktop (MCP)
   - Ensure `claude_desktop_config.json` is configured.
   - Restart Claude Desktop.

   ### Mode B: WhatsApp (Webhook)
   ```bash
   uvicorn webhook:app --reload
   ngrok http 8000
   ```
