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
async def get_my_files(directory: str) -> str:
    """Lists available PDF/Word reports in a specific directory."""
    return await list_lab_files(directory)

@mcp.tool()
async def check_my_deadlines() -> str:
    """Fetches active assignments and deadlines from the LMS."""
    return await check_deadlines()

@mcp.tool()
async def submit_assignment(assignment_id: str, file_path: str) -> str:
    """Uploads a specific file to a specific assignment ID."""
    return await submit_to_lms(assignment_id, file_path)

if __name__ == "__main__":
    mcp.run()
