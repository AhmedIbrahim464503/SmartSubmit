import os
import logging
from typing import List, Optional

# Configure logging
logger = logging.getLogger(__name__)

async def list_lab_files(directory: str, search_query: str = None) -> str:
    """Lists available PDF/Word reports in a specific directory. Optional filter."""
    logger.info(f"Scanning directory: {directory} for query: {search_query}")
    try:
        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            return f"Error: Directory '{directory}' does not exist."

        # Filter extensions (PDF, Word, Excel, ZIP)
        allowed_exts = ('.pdf', '.docx', '.doc', '.zip', '.xlsx', '.xls', '.csv')
        all_files = [f for f in os.listdir(directory) if f.lower().endswith(allowed_exts)]
        
        # Filter by query if provided
        if search_query:
            files = [f for f in all_files if search_query.lower() in f.lower()]
        else:
            files = all_files

        if not files:
            if search_query:
                return f"No files found matching '{search_query}' in {directory}."
            logger.info("No report files found.")
            return "No PDF, Word, Excel, or ZIP files found in the specified directory."
        
        logger.info(f"Found {len(files)} files.")
        return "Found files:\n" + "\n".join(files)
    except Exception as e:
        logger.error(f"Error scanning directory: {str(e)}")
        return f"Error scanning directory: {str(e)}"
