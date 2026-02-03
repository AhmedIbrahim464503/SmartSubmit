import os
import httpx
import logging
import re
import time
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Switch to Moodle Keys
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")
MOODLE_URL = os.getenv("MOODLE_URL") # e.g. https://lms.nust.edu.pk/webservice/rest/server.php

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
        "wsfunction": "core_webservice_get_site_info"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # 1. Get User ID
            resp = await client.get(MOODLE_URL, params=params)
            resp.raise_for_status()
            site_info = resp.json()
            
            if "exception" in site_info:
                return f"Moodle Error: {site_info.get('message')}"
            
            user_id = site_info["userid"]
            
            # Step 1.5: Get Enrolled Courses (to map IDs to Names)
            # This ensures we show "Compiler Construction" instead of "61184"
            params["wsfunction"] = "core_enrol_get_users_courses"
            params["userid"] = user_id
            
            course_map = {}
            try:
                resp_courses = await client.get(MOODLE_URL, params=params)
                if resp_courses.status_code == 200:
                    courses = resp_courses.json()
                    if isinstance(courses, list):
                        for c in courses:
                            c_id = c.get("id")
                            c_name = c.get("fullname")
                            if c_id and c_name:
                                course_map[c_id] = c_name
            except Exception as e:
                logger.warning(f"Failed to fetch course names: {e}")

            # Step 2: Get Upcoming Action Events
            # We use `timesortfrom` to get only FUTURE events.
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
            
            for e in events:
                name = e.get("name", "Unknown Assignment")
                course_info = e.get("course", {})
                c_id_raw = course_info.get("id", -1)
                
                # Try to get Name from Map, then from Event, then fallback to ID
                course_name = course_map.get(c_id_raw)
                if not course_name:
                    course_name = course_info.get("fullname", f"Course {c_id_raw}")

                assign_id = str(e.get("instance", "N/A"))
                time_str = e.get("formattedtime", "No date")
                
                # Filter by search_query if provided
                full_text = f"{name} {course_name}".lower()
                if search_query and search_query.lower() not in full_text:
                    continue

                # Clean cleaner output
                # Remove HTML tags from name or description if any
                clean_name = re.sub(r'<[^>]+>', '', name).strip()
                result.append(f"- {clean_name} ({course_name}) [ID: {assign_id}]: Due {time_str}")
            
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
    Submits a file to Moodle assignment using the full workflows:
    1. Upload file to Draft Area (upload.php)
    2. Save Submission (mod_assign_save_submission)
    3. Accept Statement & Finalize (mod_assign_submit_for_grading)
    """
    logger.info(f"Starting submission process for {file_path} to Assignment {assignment_id}")
    
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    
    if not MOODLE_TOKEN or not MOODLE_URL:
        return "Error: MOODLE_TOKEN or MOODLE_URL not set."

    # Derive upload URL from MOODLE_URL (replace rest/server.php with upload.php)
    # Env: https://lms.nust.edu.pk/portal/webservice/rest/server.php
    # Target: https://lms.nust.edu.pk/portal/webservice/upload.php
    upload_url = MOODLE_URL.replace("/rest/server.php", "/upload.php")
    
    try:
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            
            # --- STEP 1: UPLOAD FILE TO DRAFT AREA ---
            logger.info("Step 1: Uploading file to Draft Area...")
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                # Moodle upload params
                upload_params = {
                    'token': MOODLE_TOKEN,
                    'itemid': 0, # 0 = create new draft area
                    'filearea': 'draft'
                }
                resp_upload = await client.post(upload_url, params=upload_params, files=files)
                resp_upload.raise_for_status()
                
                # Response is a JSON list
                upload_data = resp_upload.json()
                if not upload_data or 'itemid' not in upload_data[0]:
                    logger.error(f"Upload failed. Response: {upload_data}")
                    return f"Error: File upload failed. Server responded: {upload_data}"
                
                draft_item_id = upload_data[0]['itemid']
                logger.info(f"File uploaded successfully. Draft Item ID: {draft_item_id}")

            # --- STEP 2: SAVE SUBMISSION (DRAFT) ---
            logger.info("Step 2: Saving submission to assignment...")
            # We must pass the draft_item_id to the 'files_filemanager' plugin
            save_params = {
                "wstoken": MOODLE_TOKEN,
                "moodlewsrestformat": "json",
                "wsfunction": "mod_assign_save_submission",
                "assignmentid": assignment_id,
                "plugindata[onlinetext_editor][text]": "",
                "plugindata[onlinetext_editor][format]": 1,
                "plugindata[onlinetext_editor][itemid]": 0,
                "plugindata[files_filemanager]": draft_item_id
            }
            
            resp_save = await client.post(MOODLE_URL, params=save_params)
            resp_save.raise_for_status()
            save_data = resp_save.json()
            
            # Moodle often returns null/empty list on success for this function, 
            # Or warnings list. If 'exception' key exists, it failed.
            if isinstance(save_data, dict) and "exception" in save_data:
                logger.error(f"Save Submission failed: {save_data}")
                return f"Error Saving Draft: {save_data.get('message')}"
            
            logger.info("Draft saved successfully.")

            # --- STEP 3: SUBMIT FOR GRADING (Optional/Conditional) ---
            logger.info("Step 3: Finalizing submission (Accepting Statement)...")
            final_params = {
                "wstoken": MOODLE_TOKEN,
                "moodlewsrestformat": "json",
                "wsfunction": "mod_assign_submit_for_grading",
                "assignmentid": assignment_id,
                "acceptsubmissionstatement": 1
            }
            
            resp_final = await client.post(MOODLE_URL, params=final_params)
            resp_final.raise_for_status()
            final_data = resp_final.json()
            
            # Logic: If Step 3 fails, it usually means the assignment doesn't REQUIRE explicit finalization 
            # (it uses "Direct Submission" mode) OR it is a Re-submission where draft is enough.
            if isinstance(final_data, dict) and "exception" in final_data:
                msg = final_data.get('message', '')
                logger.info(f"Auto-finalize skipped/failed: {msg}")
                return f"SUCCESS: File '{os.path.basename(file_path)}' uploaded and saved to Assignment {assignment_id}.\n(Note: 'Submit for Grading' button was not clicked automatically—this is normal for Direct Submissions or Re-submissions. Your file IS on Moodle)."

            return f"SUCCESS: '{os.path.basename(file_path)}' has been fully submitted and finalized for Assignment {assignment_id}."

    except Exception as e:
        logger.error(f"Submission Error: {repr(e)}")
        return f"Critical Error during submission process: {repr(e)}"
