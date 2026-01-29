from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import Response
from tools import check_deadlines, submit_to_lms, list_lab_files
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure logging
logging.basicConfig(
    filename="student_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ALLOWED_NUMBER = os.getenv("WHATSAPP_ALLOWED_NUMBER")

@app.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Handle incoming WhatsApp messages from Twilio.
    """
    logger.info(f"Received message from {From}: {Body}")

    # Security Check
    if ALLOWED_NUMBER and From != f"whatsapp:{ALLOWED_NUMBER}":
        logger.warning(f"Unauthorized access attempt from {From}")
        return Response(content="Unauthorized", status_code=403)

    response_text = "I didn't understand that command. Try 'status' or 'files'."

    command = Body.strip().lower()

    if "status" in command or "deadline" in command:
        # Extract potential search term (e.g. "deadline lab 1" -> "lab 1")
        query = command.replace("status", "").replace("deadline", "").strip()
        # If query is empty strings like "", treat as None
        query = query if query else None
        response_text = await check_deadlines(query)
    
    elif "files" in command or "list" in command:
        # Default scan directory - in a real app, maybe configurable or derived from session
        scan_dir = os.path.join(os.path.expanduser("~"), "Documents", "University")
        # For this demo, let's just scan the current folder or a 'lab_reports' folder relative to script
        # if the user hasn't specified.
        # Let's use the current working directory for simplicity if 'Documents/University' is theoretical.
        # But per requirements: "scans a specific local directory (e.g., ~/Documents/University)"
        # I'll default to that but fallback to CWD if it fails to be helpful.
        default_dir = os.path.join(os.path.expanduser("~"), "Documents", "University")
        if not os.path.exists(default_dir):
            default_dir = os.getcwd()
            
        response_text = await list_lab_files(default_dir)

    elif "submit" in command:
        # Very basic parsing for demo: "submit <assignment_id> <filename>"
        parts = command.split()
        if len(parts) >= 3:
            assignment_id = parts[1]
            filename = " ".join(parts[2:]) # Handle filenames with spaces?
            # We need a full path. We'll search for it in our default dir.
            default_dir = os.path.join(os.path.expanduser("~"), "Documents", "University")
            if not os.path.exists(default_dir):
                default_dir = os.getcwd()
                
            full_path = os.path.join(default_dir, filename)
            response_text = await submit_to_lms(assignment_id, full_path)
        else:
            response_text = "Usage: submit <assignment_id> <filename>"

    # Twilio expects XML response, but for simple messaging we can just return plain text 
    # if we use the messaging_response wrapper, OR just return 200 OK and use the API to send a message back.
    # The requirement says "FastAPI endpoint... receives Twilio webhooks".
    # The simplest way to reply is TwiML.
    
    from twilio.twiml.messaging_response import MessagingResponse
    resp = MessagingResponse()
    resp.message(response_text)
    
    return Response(content=str(resp), media_type="application/xml")

@app.get("/")
async def root():
    return {"status": "SmartSubmit WhatsApp Agent Running"}
