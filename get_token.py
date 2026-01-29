import requests
import getpass

def get_moodle_token():
    print("=== NUST Moodle Token Fetcher ===")
    print("This script will fetch your 'Moodle mobile web service' token.")
    print("Your credentials will be sent directly to NUST's server and NOT saved.")
    
    username = input("Enter your NUST Username (CMS ID): ").strip()
    password = getpass.getpass("Enter your Password: ").strip()
    
    url = "https://lms.nust.edu.pk/portal/login/token.php"
    
    params = {
        "username": username,
        "password": password,
        "service": "moodle_mobile_app"
    }
    
    print("\nConnecting to LMS...")
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        data = response.json()
        
        if "token" in data:
            print("\n" + "="*40)
            print("SUCCESS! Here is your MOODLE_TOKEN:")
            print("="*40)
            print(data["token"])
            print("="*40)
            print("\nCopy the line above and paste it into your .env file like this:")
            print(f"MOODLE_TOKEN={data['token']}")
        elif "error" in data:
            print(f"\nError from NUST: {data['error']}")
        else:
            print(f"\nUnexpected response: {data}")
            
    except Exception as e:
        print(f"\nConnection failed: {str(e)}")

if __name__ == "__main__":
    get_moodle_token()
