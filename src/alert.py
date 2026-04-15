import requests
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_alert(message: str):
    """
    Sends a WhatsApp message using the CallMeBot API.
    """
    # Use credentials from environment variables or fallback to the provided ones
    phone = os.getenv("CALLMEBOT_PHONE", "85290350553")
    apikey = os.getenv("CALLMEBOT_APIKEY", "4907022")
    
    # URL encode the message so it formats correctly in the HTTP request
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={apikey}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("    [+] WhatsApp alert sent successfully!")
        else:
            print(f"    [-] Failed to send WhatsApp alert. Status code: {response.status_code}")
            print(f"        Response: {response.text}")
    except Exception as e:
        print(f"    [-] Error sending WhatsApp alert: {e}")

if __name__ == "__main__":
    # Test message
    send_whatsapp_alert("🤖 Testing WhatsApp integration for Market Alert Bot!")
