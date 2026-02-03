import os
import logging
from fastmcp import FastMCP
from services import list_lab_files, check_deadlines, submit_to_lms

# Initialize FastMCP Server
mcp = FastMCP("SmartSubmit")

# Setup Logging (Redirect to file to avoid stdout pollution interfering with MCP)
logging.basicConfig(
    filename="student_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@mcp.tool()
async def list_documents(directory: str = None, query: str = None) -> str:
    """
    REQUIRED: Use this tool to list files on the USER'S local computer. 
    Do NOT check /mnt/ or cloud paths. 
    Lists documents (PDF, Word, Excel, ZIP) from the configured local directory.
    Use 'query' to filter by name (e.g. 'Lab 1', 'Financial Report').
    """
    target_dir = directory or os.getenv("LAB_DIRECTORY", "E:\\Downloads")
    
    if not os.path.exists(target_dir):
        # Fallback if preferred dir is missing
        fallback = os.path.expanduser("~/Downloads")
        if os.path.exists(fallback):
            return await list_lab_files(fallback, query) + f"\n(Note: Could not find {target_dir}, listing from {fallback} instead)"
        return f"Error: Could not find directory {target_dir} or {fallback}"

    return await list_lab_files(target_dir, query)

@mcp.tool()
async def check_my_deadlines(search_query: str = None) -> str:
    """REQUIRED: Connects to the User's Real LMS (Moodle) to fetch actual upcoming assignments and deadlines."""
    return await check_deadlines(search_query)

@mcp.tool()
async def submit_assignment(assignment_id: str, file_path: str) -> str:
    """Uploads a specific file to a specific assignment ID."""
    return await submit_to_lms(assignment_id, file_path)

@mcp.tool()
def restart_agent() -> str:
    """
    Restart the agent to apply code changes. 
    This will Disconnect the agent. You must click 'Retry Connection' in the Claude Desktop interface immediately after.
    """
    logging.info("Restarting agent requested by user...")
    sys.exit(0)
    return "Restarting..."

if __name__ == "__main__":
    mcp.run()
