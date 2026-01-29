import asyncio
import os
from tools import list_lab_files, check_deadlines
from webhook import app
from fastapi.testclient import TestClient

# Setup dummy file
dummy_dir = os.path.join(os.getcwd(), "test_docs")
os.makedirs(dummy_dir, exist_ok=True)
with open(os.path.join(dummy_dir, "Lab1.pdf"), "w") as f:
    f.write("dummy content")

async def test_tools():
    print("Testing list_lab_files...")
    # Test identifying the file we just created
    res = await list_lab_files(dummy_dir)
    print(f"Result: {res}")
    assert "Lab1.pdf" in res

    print("\nTesting check_deadlines (Expect Auth Error or Mock)...")
    # This will likely return an error string because keys are dummy, which is expected behavior
    res = await check_deadlines()
    print(f"Result: {res}")

def test_webhook():
    print("\nTesting Webhook...")
    client = TestClient(app)
    
    # Test Unauthorized
    resp = client.post("/whatsapp", data={"From": "whatsapp:+00000", "Body": "status"})
    print(f"Unauthorized Test: {resp.status_code}") 
    # Note: If ALLOWED_NUMBER is set in .env as +1234567890, this should be 403.
    # If not set, it might pass depending on logic.
    
    # Test Authorized (Mocking the number from .env or just a generic one if we didn't set .env strict)
    # in tools.py I wrote: if ALLOWED_NUMBER and From != ...
    
    # Let's read what we wrote to .env
    from dotenv import load_dotenv
    load_dotenv()
    allowed = os.getenv("WHATSAPP_ALLOWED_NUMBER")
    
    resp = client.post("/whatsapp", data={"From": f"whatsapp:{allowed}", "Body": "status"})
    print(f"Authorized Status Test: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_tools())
    test_webhook()
