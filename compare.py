import importlib.util
import traceback
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from format import read_input_file, write_output_file
import shutil

def load_assistant_script(module_name):
    """Dynamically import an assistant script by its module name.

    Args:
        module_name (str): The name of the module to import (e.g., 'assistants.code_maestro').

    Returns:
        module: The imported module if successful, or None otherwise.
    """
    try:
        module = importlib.import_module(f"assistants.{module_name}")
        print(f"[+] Loaded assistant script: {module_name}")
        return module
    except Exception as e:
        print(f"[-] Failed to load assistant script {module_name}: {e}")
        return None

def run_assistant(assistant_module, input_data, assistant_name):
    """Run the provided assistant module with the given input data.

    Args:
        assistant_module (module): The assistant module to run.
        input_data (dict): The input data to process.
        assistant_name (str): The name of the assistant.

    Returns:
        dict: The result from the assistant, or None if an error occurred.
    """
    try:
        result = assistant_module.run(input_data)
        result["assistant_name"] = assistant_name
        print(f"[+] Assistant {assistant_name} processed input data.")
        return result
    except Exception as e:
        print(f"[-] Assistant {assistant_name} failed: {str(e)}")
        traceback.print_exc()
        return None

def group_input_files(input_dir):
    """Group input files by category.

    Args:
        input_dir (str): Path to the input directory.

    Returns:
        dict: A dictionary where keys are category names and values are lists of file paths.
    """
    categories = defaultdict(list)
    input_path = Path(input_dir)
    for category_dir in input_path.iterdir():
        if category_dir.is_dir():
            categories[category_dir.name] = list(category_dir.rglob("*.ini"))
    return categories

def preload_assistants(assistant_names):
    """Preload assistant scripts by their names.

    Args:
        assistant_names (list): List of assistant script names to load.

    Returns:
        dict: A dictionary where keys are script names and values are loaded modules.
    """
    loaded_assistants = {}
    for name in assistant_names:
        assistant_module = load_assistant_script(name)
        if assistant_module:
            loaded_assistants[name] = assistant_module
    return loaded_assistants

def process_category_files(category, input_files, loaded_assistants, output_dir):
    """Process all input files in a category with the loaded assistants.

    Args:
        category (str): The category name.
        input_files (list): List of input file paths.
        loaded_assistants (dict): Preloaded assistant modules.
        output_dir (str): Path to the directory where outputs will be saved.
    """
    for input_file in input_files:
        try:
            input_data = read_input_file(input_file)
            print(f"[+] Read input file: {input_file}")
        except Exception as e:
            print(f"[-] Failed to read input file {input_file}: {e}")
            continue

        output_file = Path(output_dir) / category / input_file.with_suffix(".md").name
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
            for name, assistant_module in loaded_assistants.items():
                output_data = run_assistant(assistant_module, input_data, name)
                if output_data is None:
                    print(f"[-] No output data from assistant {name} for input {input_file}.")
                    continue
                write_output_file(output_data, output_file, append=True)
            print(f"[+] Written output to: {output_file}")
        except Exception as e:
            print(f"[-] Failed to write output to {output_file}: {e}")

def process_inputs(input_dir, output_dir, assistant_names):
    """Process input files with the specified assistant scripts.

    Args:
        input_dir (str): Path to the directory containing input files.
        output_dir (str): Path to the directory where outputs will be saved.
        assistant_names (list): List of assistant script names to load.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(output_dir) / current_date
    if output_dir.exists():
        print(f"[-] Removing existing output directory: {output_dir}")
        shutil.rmtree(output_dir)

    categories = group_input_files(input_dir)

    # Print categories and file counts
    for category, files in categories.items():
        print(f"[+] Category: {category}, Files: {len(files)}")

    # Preload all assistant modules
    loaded_assistants = preload_assistants(assistant_names)

    if not loaded_assistants:
        print("[-] No assistants were successfully loaded. Exiting.")
        exit(1)

    # Process each category
    for category, input_files in categories.items():
        process_category_files(category, input_files, loaded_assistants, output_dir)

def get_all_assistant_names():
    """Retrieve all assistant script names from the specified directory.

    Returns:
        list: List of assistant script names (without .py extension).
    """
    scripts = [p.stem for p in Path("./assistants").rglob("*.py")]
    print(f"[+] Found assistant scripts: {scripts}")
    return scripts

if __name__ == "__main__":
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run comparative tests across AI assistants.")
    parser.add_argument("-input", type=str, default="./input", help="Path to the input directory (default: ./input).")
    parser.add_argument("-output", type=str, default="./output", help="Path to the output directory (default: ./output).")
    parser.add_argument("-assistants", type=str, nargs='+', help="Names of assistant scripts to load. If not specified, all scripts in ./assistants will be used.")

    args = parser.parse_args()

    assistant_names = args.assistants if args.assistants else get_all_assistant_names()

    # Process the inputs with the specified or detected assistant scripts
    process_inputs(args.input, args.output, assistant_names)
