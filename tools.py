import os
import httpx
import logging
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="student_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Switch to Moodle Keys
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")
MOODLE_URL = os.getenv("MOODLE_URL") # e.g. https://lms.nust.edu.pk/webservice/rest/server.php

async def list_lab_files(directory: str) -> str:
    """Lists available PDF/Word reports in a specific directory."""
    logger.info(f"Scanning directory: {directory}")
    try:
        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            return f"Error: Directory '{directory}' does not exist."

        files = [f for f in os.listdir(directory) if f.lower().endswith(('.pdf', '.docx', '.doc'))]
        if not files:
            logger.info("No report files found.")
            return "No PDF or Word documents found in the specified directory."
        
        logger.info(f"Found {len(files)} files.")
        return "Found files:\n" + "\n".join(files)
    except Exception as e:
        logger.error(f"Error scanning directory: {str(e)}")
        return f"Error scanning directory: {str(e)}"

async def check_deadlines() -> str:
    """Fetches upcoming assignments from Moodle (NUST LMS)."""
    logger.info("Checking Moodle deadlines...")
    if not MOODLE_TOKEN or not MOODLE_URL:
        return "Error: MOODLE_TOKEN or MOODLE_URL not set in .env"

    # Moodle API params
    params = {
        "wstoken": MOODLE_TOKEN,
        "moodlewsrestformat": "json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Get User ID (Needed for other calls)
            # Function: core_webservice_get_site_info
            params["wsfunction"] = "core_webservice_get_site_info"
            resp = await client.get(MOODLE_URL, params=params)
            resp.raise_for_status()
            site_info = resp.json()
            
            if "exception" in site_info:
                return f"Moodle Error: {site_info.get('message')}"
            
            user_id = site_info["userid"]
            
            # Step 2: Get Upcoming Action Events (Deadlines)
            # Function: core_calendar_get_action_events_by_timesort
            params["wsfunction"] = "core_calendar_get_action_events_by_timesort"
            # Optional: limit num etc.
            
            resp_events = await client.get(MOODLE_URL, params=params)
            resp_events.raise_for_status()
            events_data = resp_events.json()
            
            events = events_data.get("events", [])
            
            if not events:
                return "No upcoming deadlines found on Moodle."
            
            result = ["Upcoming Moodle Deadlines:"]
            for e in events:
                # Event Name, Course, Time
                name = e.get("name", "Unknown Assignment")
                course_id = e.get("course", {}).get("id", "??")
                time_str = e.get("formattedtime", "No date")
                url = e.get("url", "")
                result.append(f"- {name} (Course {course_id}): Due {time_str}")
            
            return "\n".join(result)

    except Exception as e:
        logger.error(f"Error checking Moodle: {repr(e)}")
        return f"Error checking Moodle: {repr(e)}"

async def submit_to_lms(assignment_id: str, file_path: str) -> str:
    """
    Submits a file to Moodle assignment.
    Note: Real Moodle submission requires drafted file upload -> save submission.
    """
    logger.info(f"Submitting {file_path} to Assignment ID {assignment_id}")
    
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    
    if not MOODLE_TOKEN or not MOODLE_URL:
        return "Error: MOODLE_TOKEN not set."

    # This is a complex multi-step process in Moodle. 
    # For this MCP prototype, we will implement the checks and alert the user 
    # if we cannot perform the full upload without 'draft' permissions.
    
    return f"Moodle Submission Logic: Ready to upload '{os.path.basename(file_path)}' to ID {assignment_id}. (Note: Full file upload requires valid 'mod_assign_save_submission' permissions)."
