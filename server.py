from fastmcp import FastMCP
from tools import list_lab_files, check_deadlines, submit_to_lms
import logging

# Initialize FastMCP Server
mcp = FastMCP("SmartSubmit")

# Setup Logging (Redirect to file to avoid stdout pollution interfering with MCP)
logging.basicConfig(
    filename="student_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@mcp.tool()
async def list_documents(directory: str = None) -> str:
    """Lists available PDF/Word reports. Defaults to LAB_DIRECTORY env if not provided."""
    target_dir = directory or os.getenv("LAB_DIRECTORY", "E:\\Downloads")
    
    if not os.path.exists(target_dir):
        # Fallback if preferred dir is missing
        fallback = os.path.expanduser("~/Downloads")
        if os.path.exists(fallback):
            return await list_lab_files(fallback) + f"\n(Note: Could not find {target_dir}, listing from {fallback} instead)"
        return f"Error: Could not find directory {target_dir} or {fallback}"

    return await list_lab_files(target_dir)

@mcp.tool()
async def check_my_deadlines(search_query: str = None) -> str:
    """Fetches active assignments from the LMS. Optional: provide 'search_query' to filter by name."""
    return await check_deadlines(search_query)

@mcp.tool()
async def submit_assignment(assignment_id: str, file_path: str) -> str:
    """Uploads a specific file to a specific assignment ID."""
    return await submit_to_lms(assignment_id, file_path)

if __name__ == "__main__":
    mcp.run()
