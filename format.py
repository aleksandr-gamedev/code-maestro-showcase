import os

# Define the structure for input and output data

INPUT_STRUCTURE = {
    "repository": str,
    "project_name": str,  # Name of the project
    "inputs": list,  # List of user inputs including follow-ups
    "evaluator": str,
}

OUTPUT_STRUCTURE = {
    "user_inputs": list,  # List of user inputs
    "assistant_responses": list,  # List of assistant responses
    "assistant_name": str,  # Name of the assistant
}

def read_input_file(filepath):
    """
    Reads an input file and parses its contents into a structured format.

    Args:
        filepath (str): Path to the input file.

    Returns:
        dict: Parsed input data following the INPUT_STRUCTURE.
    """
    with open(filepath, mode='r', encoding='utf-8') as file:
        lines = file.readlines()

    parsed_data = {
        "repository": None,
        "project_name": None,
        "inputs": [],
        "evaluator": None,
    }

    current_section = None
    current_content = []

    for line in lines:
        line = line.strip()
        # Detect section headers
        if line in ("[Repository]", "[Input]", "[Evaluator]"):
            # Save the previous section content if applicable
            if current_section == "[Input]" and current_content:
                parsed_data["inputs"].append("\n".join(current_content))
            current_section = line
            current_content = []
        # Extract repository information
        elif current_section == "[Repository]" and "=" in line:
            key, value = line.split("=", 1)
            if key.strip() == "Name":
                parsed_data["project_name"] = value.strip()
            elif key.strip() == "URL":
                parsed_data["repository"] = value.strip()
        # Append input or evaluator content
        elif current_section in ("[Input]", "[Evaluator]"):
            current_content.append(line)

    # Save the last section content
    if current_section == "[Input]" and current_content:
        parsed_data["inputs"].append("\n".join(current_content))
    elif current_section == "[Evaluator]":
        parsed_data["evaluator"] = "\n".join(current_content)

    return parsed_data

def write_output_file(data, filepath, append=False):
    """
    Writes output data into a markdown file.

    Args:
        data (dict): Output data following the OUTPUT_STRUCTURE.
        filepath (str): Path to save the output file.
        append (bool): If True, appends to the existing file instead of overwriting it.
    """
    mode = 'a' if append else 'w'
    with open(filepath, mode=mode, encoding='utf-8') as file:
        # Write assistant name as a header
        file.write(f"# {data['assistant_name']}\n\n")
        for user_input, assistant_response in zip(data["user_inputs"], data["assistant_responses"]):
            # Format user input with '>' prefix for readability
            formatted_input = "\n".join([f"> {line}" for line in user_input.split("\n")])
            file.write(f"{formatted_input}\n\n{assistant_response}\n\n")
