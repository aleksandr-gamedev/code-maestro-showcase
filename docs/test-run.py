import requests
import json
import uuid
import re

# API URL
BASE_URL = "https://api.prod.code-maestro.com"
LOGIN_URL = f"{BASE_URL}/auth/login"
DIALOG_MESSAGE_URL = f"{BASE_URL}/dialogs/{{dialogId}}/messages/stream"

# Authentication credentials
EMAIL = "qqq@qqq"
PASSWORD = "qqq@qqq"
PROJECT_NAME = "Darklings-FightingGame"

def authenticate(email, password):
    """ Authenticate and retrieve an access token """
    payload = {"email": email, "password": password}
    response = requests.post(LOGIN_URL, json=payload)
    
    if response.status_code == 200:
        token = response.json().get("token")
        if token:
            print("[+] Authentication successful")
            return token
    print(f"[-] Authentication failed: {response.text}")
    return None

def create_new_dialog():
    """ Generate a new dialog ID """
    new_dialog_id = str(uuid.uuid4())
    print(f"[+] New dialog created with ID: {new_dialog_id}")
    return new_dialog_id

def send_message(token, dialog_id, message):
    """ Send a message to the AI assistant and handle streaming response """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "userMessageId": str(uuid.uuid4()),
        "responseMessageId": str(uuid.uuid4()),
        "message": message
    }
    
    response = requests.post(
        DIALOG_MESSAGE_URL.format(dialogId=dialog_id) + f"?projectName={PROJECT_NAME}",
        headers=headers, json=payload, stream=True
    )
    
    if response.status_code == 200:
        collected_response = []
        print("[+] Streaming response:")
        for line in response.iter_lines():
            if line:
                try:
                    json_data = json.loads(line.decode("utf-8").replace("data: ", ""))
                    delta = json_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        collected_response.append(delta)
                        print(delta, end="", flush=True)  # Print streaming response live
                except json.JSONDecodeError:
: {line}")
                    pass  # Skip if it's not a valid JSON
        
        full_response_text = "".join(collected_response)
        print("\n[+] Response successfully reconstructed.")
        return full_response_text
    print(f"[-] Failed to get response: {response.text}")
    return None

def save_response_to_markdown(dialog_id, user_message, ai_response):
    """ Save the parsed AI response to a markdown file """
    md_filename = f"code-maestro-{dialog_id}.md"
    with open(md_filename, "w", encoding="utf-8") as file:
        file.write(f"# CodeMaestro Dialog {dialog_id}\n\n")
        file.write(f"**User Query:**\n```\n{user_message}\n```\n\n")
        file.write(f"**[View Dialog](https://codemaestro.ai/dialog/{dialog_id})**\n\n")
        file.write("**AI Response:**\n\n")
        file.write(ai_response)
    
    print(f"[+] Response saved to {md_filename}")

if __name__ == "__main__":
    token = authenticate(EMAIL, PASSWORD)
    if token:
        dialog_id = create_new_dialog()
        user_message = "Explain the architectural design of this project. Which software design patterns are implemented explicitly, and which are implemented implicitly?"
        ai_response = send_message(token, dialog_id, user_message)
        
        if ai_response:
            save_response_to_markdown(dialog_id, user_message, ai_response)
