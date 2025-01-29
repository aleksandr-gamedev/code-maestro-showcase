import requests
import uuid
import json

# Base URL for the CodeMaestro API
BASE_URL = "https://api.dev.code-maestro.com"
# Endpoint for authentication
LOGIN_URL = f"{BASE_URL}/auth/login"
# Endpoint for sending messages in a dialog
DIALOG_MESSAGE_URL = f"{BASE_URL}/dialogs/{{dialogId}}/messages/stream"

# Credentials for authentication (replace with secure storage in production)
EMAIL = ""
PASSWORD = ""

def authenticate():
    """Authenticate and retrieve an access token.

    Raises:
        ValueError: If authentication fails.

    Returns:
        str: Access token for API requests.
    """
    # Prepare the payload with email and password
    payload = {"email": EMAIL, "password": PASSWORD}
    # Send the authentication request
    response = requests.post(LOGIN_URL, json=payload)

    # Check if the authentication was successful
    if response.status_code == 200:
        token = response.json().get("token")
        if token:
            return token

    # Raise an error if authentication fails
    error_message = f"Authentication failed: {response.text}"
    raise ValueError(error_message)

def create_new_dialog():
    """Generate a new unique dialog ID.

    Returns:
        str: A UUID representing the dialog ID.
    """
    # Generate and return a unique UUID for the dialog
    return str(uuid.uuid4())

def send_message(token, dialog_id, message, project_name):
    """Send a message to the AI assistant and handle the streaming response.

    Args:
        token (str): Access token for API authentication.
        dialog_id (str): The unique ID of the dialog.
        message (str): The user's message to send to the assistant.
        project_name (str): The name of the project being queried.

    Raises:
        RuntimeError: If the request fails or returns a non-200 status code.

    Returns:
        str: The assistant's response as a single string.
    """
    # Prepare headers with the access token
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # Prepare the payload with message and unique IDs
    payload = {
        "userMessageId": str(uuid.uuid4()),
        "responseMessageId": str(uuid.uuid4()),
        "message": message
    }

    # Send the message request to the dialog endpoint
    response = requests.post(
        DIALOG_MESSAGE_URL.format(dialogId=dialog_id) + f"?projectName={project_name}",
        headers=headers, json=payload, stream=True
    )

    # Process the response if the status is 200 (OK)
    if response.status_code == 200:
        collected_response = []
        for line in response.iter_lines():
            if line:
                # Parse streaming response line-by-line
                try:
                    json_data = json.loads(line.decode("utf-8").replace("data: ", ""))
                    delta = json_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        collected_response.append(delta)
                        # Print streaming response live
                        # print(delta, end="", flush=True)
                except json.JSONDecodeError:
                    pass  # Skip if it's not a valid JSON

        # Combine all parts of the response and return
        return "".join(collected_response)

    # Raise an error if the request fails
    error_message = f"Request failed with status {response.status_code}: {response.text}"
    raise RuntimeError(error_message)

def run(input_data):
    """Run the assistant on provided input data.

    Args:
        input_data (dict): A dictionary containing user inputs.
            Example structure: {"inputs": ["question1", "question2"], "project_name": "MyProject"}

    Returns:
        dict: A dictionary containing the user inputs and assistant responses.
            Example structure:
            {
                "user_inputs": ["question1", "question2"],
                "assistant_responses": ["response1", "response2"]
            }
    """
    # Step 1: Authenticate and retrieve an access token
    token = authenticate()
    # Step 2: Create a new dialog for the session
    dialog_id = create_new_dialog()
    responses = []

    # Step 3: Process each user input
    for user_input in input_data["inputs"]:
        # Send the user input and collect the assistant's response
        response = send_message(token, dialog_id, user_input, input_data["project_name"])
        responses.append(response if response else "Error: No response.")

    # Step 4: Return the structured results
    return {
        "user_inputs": input_data["inputs"],
        "assistant_responses": responses
    }
