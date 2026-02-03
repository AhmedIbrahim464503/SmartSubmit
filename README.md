# SmartSubmit Agent 🤖📚

**SmartSubmit** is an intelligent AI agent designed to automate the assignment submission workflow for students using **Moodle-based LMS** (specifically optimized for NUST).

It integrates directly with **Claude Desktop** to provide a seamless natural language interface for checking deadlines, searching for files, and submitting assignments.

---

## ✨ Key Features

### 1. 🧠 Intelligent File Search
- **Smart Matching**: Finds files even if you don't use the exact name (e.g., "Find BDA Lab" finds `AHMED_LAB_03_BDA.zip`).
- **Deep Search**: Scans your configured laboratory directory (e.g., Downloads, Documents) for PDF, Word, Excel, and ZIP files.
- **Absolute Paths**: Automatically resolves full system paths for tool usage.

### 2. 📅 Smart Deadline Tracking
- **Real-Time Data**: Connects to the live LMS to fetch *actually* upcoming deadlines.
- **Course Name Resolution**: Translates cryptic Course IDs (e.g., `61184`) into human-readable names (e.g., `Compiler Construction`).
- **Filtering**: Ask "What is due for Big Data?" to filter the list.

### 3. 🚀 Automated Submission Workflow
- **ID Translation**: Automatically resolves "Course Module IDs" (URLs) to "Instance IDs" (Database) to prevent "Record not found" errors.
- **Full-Cycle Handling**:
    1.  **Uploads** file to Draft Area.
    2.  **Saves** submission to the assignment.
    3.  **Finalizes** submission (clicks "Submit for Grading").
    4.  **Verifies** status: Checks if manual box-ticking is needed and honestly reports "Submitted" vs "Draft".

### 4. 🔄 Self-Healing
- **Restart Tool**: Includes a `restart_agent` command to instantly reload code updates without closing the desktop app.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- [Claude Desktop App](https://claude.ai/download)
- A NUST LMS Account

### 1. Clone & Install
```bash
git clone https://github.com/AhmedIbrahim464503/SmartSubmit.git
cd SmartSubmit
pip install -r requirements.txt
```

### 2. Configuration (.env)
Create a `.env` file in the root directory:
```ini
MOODLE_URL=https://lms.nust.edu.pk/webservice/rest/server.php
MOODLE_TOKEN=your_generated_token_here
LAB_DIRECTORY=E:\Downloads  # Or your preferred folder
```

> **Tip**: Use the included `get_token.py` script to generate your `MOODLE_TOKEN` securely using your username/password.

### 3. Connect to Claude Desktop
Edit your Claude config (typically `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "SmartSubmit": {
      "command": "python",
      "args": [
        "C:/Absolute/Path/To/SmartSubmit/server.py"
      ]
    }
  }
}
```

---

## 💡 Usage Examples

Once connected, you can simply ask Claude:

*   **"Check my deadlines."**
*   **"Check deadlines for Compiler Construction."**
*   **"Find the file for Lab 3 BDA."**
*   **"Submit that file to the Big Data assignment."**
*   **"Restart yourself."** (Refreshes the agent)

---

## 🔒 Security
- **No Password Stored**: The agent uses a Token (`MOODLE_TOKEN`) for all API calls.
- **Local Execution**: All file searching happens locally on your machine.
- **Safe SSL**: Configured to handle university SSL certificates gracefully.

---

*(c) 2026 SmartSubmit Project*
