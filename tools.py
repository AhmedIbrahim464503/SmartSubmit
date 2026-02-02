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

async def check_deadlines(search_query: str = None) -> str:
    """
    Fetches upcoming assignments from Moodle (NUST LMS).
    search_query: Optional string to filter assignments (e.g., 'Lab 1', 'CS101').
    """
    logger.info(f"Checking Moodle deadlines... Query: {search_query}")
    if not MOODLE_TOKEN or not MOODLE_URL:
        return "Error: MOODLE_TOKEN or MOODLE_URL not set in .env"

    params = {
        "wstoken": MOODLE_TOKEN,
        "moodlewsrestformat": "json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # 1. Get User ID
            user_url = f"{MOODLE_URL}?wstoken={MOODLE_TOKEN}&moodlewsrestformat=json&wsfunction=core_webservice_get_site_info"
            resp = await client.get(MOODLE_URL, params=params)
            resp.raise_for_status()
            site_info = resp.json()
            
            if "exception" in site_info:
                return f"Moodle Error: {site_info.get('message')}"
            
            user_id = site_info["userid"]
            
            # Step 2: Get Upcoming Action Events
            # We use `timesortfrom` to get only FUTURE events.
            import time
            now_ts = int(time.time())
            
            params["wsfunction"] = "core_calendar_get_action_events_by_timesort"
            params["timesortfrom"] = now_ts
            # params["limitnum"] = 10 # Optional limit
            
            resp_events = await client.get(MOODLE_URL, params=params)
            resp_events.raise_for_status()
            events_data = resp_events.json()
            
            events = events_data.get("events", [])
            
            if not events:
                return "No upcoming deadlines found (future only)."
            
            result = []
            import re
            
            for e in events:
                name = e.get("name", "Unknown Assignment")
                course_id = e.get("course", {}).get("id", "??")
                assign_id = str(e.get("instance", "N/A"))
                time_str = e.get("formattedtime", "No date")
                
                # Filter by search_query if provided
                full_text = f"{name} {course_id}".lower()
                if search_query and search_query.lower() not in full_text:
                    continue

                # Clean cleaner output
                # Remove HTML tags from name or description if any
                clean_name = re.sub(r'<[^>]+>', '', name).strip()
                result.append(f"- {clean_name} (ID: {assign_id}, Course {course_id}): Due {time_str}")
            
            if not result:
                return f"No deadlines found matching '{search_query}'."

            header = f"Upcoming Moodle Deadlines"
            if search_query:
                header += f" (filtering for '{search_query}')"
            return f"{header}:\n" + "\n".join(result)

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
