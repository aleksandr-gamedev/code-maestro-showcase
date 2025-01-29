"""
Author: Aleksandr Podzolko in collaboration with ChatGPT
Company: iLogos
Team: Code Maestro
Email: aleksandr.podzolko@ilogos.biz
LinkedIn: https://www.linkedin.com/in/player-one/
Description:
This script reads a CSV file containing raw test cases from our internal tests, filters records for specific projects,
and saves each relevant row as a formatted text file in a structured directory named for the case category.
"""

import os
import sys
import pandas as pd

# Load CSV file
file_path = "./raw/use-cases.csv"  # Path to the file
output_base_path = "./input"  # Base path for saving files

# Category mapping
category_mapping = {
    "Asset creation and setup": "assets",
    "Navigation": "navigation",
    "Project architecture understanding": "architecture",
    "Refactoring": "refactoring",
    "Coding tasks (snippets)": "coding",
    "Bug fixing": "debug",
    "Test automation": "test"
}

df = pd.read_csv(file_path)

# Filter rows by projects
filtered_df = df[df['Project'].isin(["XS - ECS Racing", "S - Fighting game"])]

# Function to determine repository name and URL
def get_repository_info(project):
    if project == "XS - ECS Racing":
        return "ECS Racing", "https://github.com/Unity-Technologies/ECS-Network-Racing-Sample.git"
    elif project == "S - Fighting game":
        return "Darklings-FightingGame", "https://github.com/kidagine/Darklings-FightingGame.git"
    return "", ""

# Dictionary to keep track of case numbers per category
category_counters = {}

# Iterate through all rows and save files
for index, row in filtered_df.iterrows():
    category = row['Category']
    category = category_mapping.get(category, category).lower()  # Map and convert to lowercase
    project = row['Project']
    repository_name, repository_url = get_repository_info(project)

    # Increment case number for category
    category_counters[category] = category_counters.get(category, 0) + 1
    case_number = category_counters[category]

    # Create path
    category_path = os.path.join(output_base_path, category)
    try:
        os.makedirs(category_path, exist_ok=True)
    except Exception as e:
        print(f"[-] Failed to create directory {category_path}: {e}")
        sys.exit(1)

    file_path = os.path.join(category_path, f"use-case-{category}-{case_number}.ini")

    # Format file content
    content = f"""[Repository]
Name={repository_name}
URL={repository_url}

[Input]
{row['Input - First question']}
"""

    # Add additional questions
    for i in range(1, 10):  # Assume a maximum of 10 Follow-up questions
        follow_up_col = f"Input - Follow-up {i} (optional)"
        if follow_up_col in row and pd.notna(row[follow_up_col]):
            content += f"\n[Input]\n{row[follow_up_col]}"

    # Add evaluator checklist
    if 'Evaluator - checklist' in row and pd.notna(row['Evaluator - checklist']):
        content += f"\n\n[Evaluator]\n{row['Evaluator - checklist']}"

    # Save to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Successfully saved: {file_path}")
    except Exception as e:
        print(f"[-] Failed to save {file_path}: {e}")
