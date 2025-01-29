# Automated Comparative Tests

Automating comparative testing for Code Maestro vs. other AI assistants.

## ChatGPT Project Files

- `project.md` – Project technical description
- `raw-use-cases-example.csv` – Sample spreadsheet data for the export script
- `test-run.py` – Sample script for connecting to the Code Maestro assistant

The sample Code Maestro script demonstrates how to:

- Connect to the assistant
- Start a new chat session with a new GUID
- Run a query
- Parse the output

## Project Directory Structure

- `docs/` – Project documentation
  - `api-swagger.json` – Swagger documentation for Code Maestro API endpoints
  - `project.md` – Project technical description
  - `test-run.py` – Example script for querying the Code Maestro assistant
  - `raw-use-cases-example.csv` – Sample spreadsheet data for the export script
- `repos/` – Directory for cloning repositories
- `input/` – Default directory for storing test use case inputs
- `output/` – Default directory for storing test outputs
- `raw/` – Use case spreadsheets available for export
  - `use-cases.csv` – Initial use case spreadsheet
- `assistants/` – Scripts for interacting with AI assistants
  - `code-maestro.py` – Script for querying the Code Maestro assistant
  - `cursor.py` – Script for querying the Cursor IDE assistant
  - `github-copilot.py` – Script for querying GitHub Copilot
- `format.py` – Defines methods and data structures for input and output files
- `export.py` – Script for converting CSV spreadsheets to Markdown
- `compare.py` – Main script for running comparative tests across AI assistants
- `config.json` – Defines project name-to-git repository URL mappings

## Testing Process

1. The comparison script selects appropriate assistant scripts.
2. The comparison script reads input files from the input path one by one using methods from the format script.
3. The comparison script clones or updates the repository in the `repos/` directory.
4. For each input file, the comparison script runs assistant scripts specified by command-line arguments (or all scripts if no argument is provided):
  - The assistant script connects to the AI assistant.
  - The assistant script processes inputs sequentially, waiting for each output.
  - The assistant script returns inputs and outputs as two string buffers.
5. The comparison script saves outputs to the appropriate path.

## Command-Line Arguments

### Export Script:

- `-csv` `<csv/file/path>` (default: `./raw/use-cases.csv`)
- `-input` `<input/folder/path>` (default: `./input`)

### Comparison Script:

- `-assistant` `<assistant_name>` (default: run all assistant scripts)
- `-input` `<input/directory/path>`
- `-output` `<output/directory/path>`

## Project Data Formats

This section defines raw, input, and output data formats.

### Raw Data Export

Raw files are only used for exporting data from internal use case spreadsheets and are not a part of the AI assistant testing process.

The raw CSV data file **MUST** include the following columns:

- `Category` – The category of the task (e.g., Navigation, Refactoring)
- `Project` – The project associated with the task (e.g., XS - ECS Racing)
- `Input - First Question` – The primary prompt or input for the assistant
- `Input - Follow-up 1 (optional)` – Optional follow-up questions for additional context
- `Input - Follow-up 2 (optional)` – Optional follow-up questions for additional context
- `Evaluator - Checklist` – Instructions or criteria for evaluating the assistant's response

All directory names must be lowercase and consist of a single word. Categories in the input are mapped to directory names as follows:

- `Asset creation and setup` → `assets`
- `Navigation` → `navigation`
- `Project architecture understanding` → `architecture`
- `Refactoring` → `refactoring`
- `Coding tasks (snippets)` → `coding`
- `Bug fixing` → `debug`
- `Test automation` → `test`

Project names are mapped to repository URLs as follows:

- `XS - ECS Racing` → [Unity-Technologies/ECS-Network-Racing-Sample](https://github.com/Unity-Technologies/ECS-Network-Racing-Sample.git)
- `S - Fighting game` → [kidagine/Darklings-FightingGame](https://github.com/kidagine/Darklings-FightingGame.git)

### Comparison Input

- Comparison input files are stored in `/input/<category>/`
- File names follow the format: `use-case-<category>-<id>.ini`
- IDs are unique within each category, as defined in `export.py`, and are generated sequentially based on their entry order in the dataset.
- Any number of inputs may be included
- Evaluator sections are reserved for future use

#### Format

```ini
[Repository]
<git repository URL>

[Context]
<Context for assistants that support it>

[Input]
<User input sent to the assistant>

[Input]
<Optional follow-up question to continue the chat>

[Evaluator]
General answer illustrated.
```

#### Example

**File path:** `input/navigation/use-case-navigation-16.md`

```ini
[Repository]
https://github.com/Unity-Technologies/ECS-Network-Racing-Sample.git

[Input]
What types of image compression are used in the project?

[Input]
Can you inspect meta files for such images and list the types of image compression used in the project?

[Evaluator]
Provides concrete types of image compression used in the project.
```

### Comparison Output

Outputs from all assistants are written in a single Markdown file, separated by assistant for clarity.

- Output files are stored in `/output/<category>/`
- File names match the corresponding input file (e.g. `use-case-<category>-<id>.md`)
- The comparison output file contains user inputs and assistant responses in the order they appeared in the chat
- Both user inputs and assistant outputs can be multi-line

#### Example

```markdown
# <First Assistant Name>

> <Original user input sent to the assistant>

<Assistant response text>

> <Follow-up user input sent to the assistant>

<Assistant response text>

# <Second Assistant Name>

> <Original user input sent to the assistant>

<Assistant response text>

> <Follow-up user input sent to the assistant>

<Assistant response text>
```

