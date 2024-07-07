# EKS Documentation Processing Tool

This tool processes AWS documentation, analyzing markdown files and optionally modifying XML files. It uses Claude on AWS Bedrock for text generation and analysis.

## Prerequisites

- Python 3.x 
- `mwinit` and `brazil` tools installed
- Works on Amazon Macs or Cloud Dev Desktops

## Setup

1. Clone this repository into the workspace for your guide.

   ```
   brazil ws use Claude-TCX3
   ```

2. Run the setup script:

   ```
   ./setup.sh
   ```

   This script will:
   - Check for an active `mwinit` session
   - Verify `isengardcli` is installed
   - Check and set the AWS_PROFILE
   - Verify AWS identity
   - Create and activate a Python virtual environment
   - Install required dependencies

3. If Necessary - Set up your AWS profile:

   If you haven't already set up your AWS profile, you can use the following command:

   ```
   isengardcli add-profile
   ```

   This will interactively guide you through creating a profile for your internal account.

4. Set the AWS_PROFILE environment variable:

   ```
   export AWS_PROFILE=your-profile-name
   ```

   Replace `your-profile-name` with the profile name you created or want to use. It's usually `${UserName}-Admin` like `gcline-Admin`.

5. The isengard account you use needs to have the Claude 3 sonnet model enabled. You can only do this in the console. Also you need to use us-east-1 or <<GDC: insert the other region, idk which us-west it is>>

## Create Markdown Build of Guide

1. Switch to the public version set and build your guide to markdown 

   ```shell
   # navigate to your guide package
   cd ~/workplace/eks/src/AmazonEKSDocs/
   # switch to public version set
   brazil ws use -vs AWSDevDocs/public
   # clean and sync
   brazil ws clean && brazil ws sync
   # build markdown
   brazil-build -Dtype=markdown
   ```

2. Find the paths to (1) the markdown, and (2) the directory that contains book.xml.

   Markdown path example:
   ```
   /Users/gcline/workplace/eks-fast/src/AmazonEKSDocs/build/markdown/eks/latest/userguide
   ```
   
   XML path example:
   ```
   /Users/gcline/workplace/eks-fast/src/AmazonEKSDocs/latest/ug
   ```

## Configuration

1. Open the `config.yaml` file and adjust the settings as needed:


   Must Change:
   - `SERVICE_NAME`: The service name (e.g., "Amazon EKS")
   - `MARKDOWN_DIRECTORY`: Path to the markdown build directory


   May Change:
   - `MAX_FILES`: Number of markdown files to process
     - set this to ~10 while you are testing
   - `OUTPUT_CSV_FILE`: Path for the output CSV file
   - `MAX_WORKERS`: Number of concurrent workers
   - `LOGGING_DIR`: Directory for log files
   - `CONSOLE_LOGS_ENABLED`: Enable/disable console logging
   - `BEDROCK_MODEL`: AWS Bedrock model to use
   - `REWRITE_INPUT_FILE`: Input file for XML modification
   - `XML_DIRECTORY`: Directory containing XML files to modify

## Usage - Generate Titles & Abstracts

1. Activate the Python virtual environment:

   ```
   source venv/bin/activate
   ```

2. Run the main script:

   For normal operation (generating titles/abstracts):
   ```
   python main.py
   ```

3. Check the output:
   - For normal operation, results will be saved to the CSV file specified in `OUTPUT_CSV_FILE`.

## Usage - Add Output to XML

   - Check out a new branch before doing this
   - `REWRITE_INPUT_FILE`: Input CSV file for XML modification
   - `XML_DIRECTORY`: Directory containing XML files to modify

   ```shell
   pyhton main.py --modify-xml
   ```

## Troubleshooting

- If you encounter AWS authentication issues, ensure your `mwinit` session is active and your AWS_PROFILE is correctly set.
- If you encounter issues with Bedrock, check that the Claude 3 Sonnet model is enabled.
- For any other issues, check the log files in the `LOGGING_DIR` for detailed error messages.

## Learn more about AWS CLI Environment Variables

Checking ~/.aws/config:

The `~/.aws/config` file is a crucial component of AWS CLI configuration. Here's how to check and understand it:

1. Open the file:
   You can view the contents of this file using any text editor or by running:
   ```
   cat ~/.aws/config
   ```

2. File structure:
   The file contains sections for different profiles

   ```text
   [default]
   region=us-east-1
   
   [profile gcline-Admin]
   output = json
   region = us-east-1
   credential_process = isengardcli credentials --awscli gcline@amazon.com --role Admin --region us-east-1
   ```

3. Key settings:
   Each profile section can include settings like `region`, `output` format, and role assumptions. For Isengard users, you might see entries created by `isengardcli add-profile`.

4. Selecting a profile:
   To use a specific profile, set the `AWS_PROFILE` environment variable:
   ```
   export AWS_PROFILE=gcline-Admin
   ```
   This tells AWS CLI and SDK to use the settings under the `[profile gcline-Admin]` section.

Always ensure your desired profile exists in this file and contains the correct settings before running AWS operations.

## Learn more about Python Virtual Environments (venv)

A Python virtual environment (venv) is an isolated Python environment that allows you to manage project-specific dependencies without interfering with system-wide Python installations or other projects.

Key benefits of using venvs:
- Isolation: Each project can have its own set of dependencies, regardless of what's installed globally.
- Consistency: Ensures all developers working on a project use the same versions of libraries.
- Clean testing environment: Allows testing in a clean, reproducible environment.

How to work with virtual environments:

1. Creating a venv:
   ```
   python3 -m venv venv
   ```
   This creates a new directory `venv` containing the virtual environment.

2. Activating a venv:
   - On Linux or MacOS:
     ```
     source venv/bin/activate
     ```
   When activated, your shell prompt will change to show the name of the active environment.

3. Using the venv:
   Once activated, any Python commands you run will use the Python interpreter and libraries in the virtual environment.

5. Deactivating the venv:
   When you're done working in the virtual environment, you can deactivate it:
   ```
   deactivate
   ```
   This returns you to the global Python environment.

Remember to activate the appropriate virtual environment before working on a specific project to ensure you're using the correct dependencies and Python version.