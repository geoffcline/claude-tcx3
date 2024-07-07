# Automate rewriting titles to TCX3 style with Claude

This script automatically generates a new title and abstract for each `<section role=“topic”>` in your guide. The new titles is, hopefully, more task oriented to comply with [TCX3](w.amazon.com). It uses Claude on AWS Bedrock.

For Example:
- Old Title: Workloads
- AI Title: Deploying and Scaling Containerized Workloads on Amazon EKS
- Old Title: Autoscaling
- AI Title: Auto-scaling Kubernetes Resources with Amazon EKS
- Old Title: Cluster insights
- AI Title: Preparing for Kubernetes Version Upgrades with Cluster Insights

[View sample output.](https://amazon.awsapps.com/workdocs-preview/index.html#/document/cdc3021ed6eff7973f534fb9841b3ece54bd4d23117bdb9b8a5e0cceadd74d8e)

The script is moderately complicated to setup, but it can process about ~300 pages per minute. You can view the prompts for both [title generation](https://code.amazon.com/packages/Claude-TCX3/blobs/2c4e1bae442b9a070bfa99e0241c0865b15be4f5/--/src/prompts.py#L60) and [abstract generation](https://code.amazon.com/packages/Claude-TCX3/blobs/2c4e1bae442b9a070bfa99e0241c0865b15be4f5/--/src/prompts.py#L6). Prompt suggestions welcome. I encourage you to try modifying the prompt and running it on your own guide.

## How it Works

The script has two modes:
-  generating tiles/abstracts
	-  Generate new abstract based on contents of an entire page
	-  Generate new title based on the new abstract
	-  Save results to a spreadsheet
-  Writing the titles/abstracts back to XML.
	-  Browse through XML for `<section role=“topic”>`
	-  Lookup the ID of the section in the spreadsheet, and add the new stuff *commented out*.

The script starts *a lot* of chats with Claude. It makes about ~400 per minute on my device. 

## Workflow overview
1. Setup: Create Isengard CLI profile, Python Virtual Environment, and Enable Claude on Bedrock
2. Run Markdown Build of Guide
3. Run AI Title/Abstract Generation. The output is a CSV file, you can open it in Excel. It has the IDs of sections, followed by the generated titles/abstracts. The old title is provided for context.
4. Review output. You may decide to revise the prompt for your guide and regenerate the titles. Alternatively, you may edit the titles individually. 
5. Run Modify XML script. This places the new title/abstract under the `<section>` tag, but importantly they are *commented out*. You must manually uncomment them, add entities, etc. It’s just too complicated an error-prone to overwrite the titles. 

## Prereqs
- Personal Isengard Account
- Claude 3 Sonnet enabled on Isengard Account
	- [View how to enable in Bedrock docs.](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html#:~:text=To%20request%20access%20to%20a,want%20to%20add%20access%20to.)
- MacOS or Linux device

## Create Markdown Build of Guide

Claude seems to really struggle with XML. The markdown build is also nicely formatted with a single file per public page. 

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


## Setup

1. Clone this repository into the workspace for your guide.

   ```
   cd ~/workplace/eks/
   brazil ws use Claude-TCX3
   cd Claude-TCX3
   ```

2. Run the setup script:

   ```
   ./setup.sh
   ```

   [View script source.](https://code.amazon.com/packages/Claude-TCX3/blobs/main/--/setup.sh)
   
   This script will:
   - Check for an active `mwinit` session
   - Verify `isengardcli` is installed
   - Check and set the AWS_PROFILE
   - Check AWS CLI is working and authenticated
   - Create and activate a Python virtual environment
   - Install required dependencies

3. If Necessary - Set up your Isengard profile for AWS CLI:

   The script will tell you if you don’t have an AWS CLI profile. It’s up at the start, you will need to scroll up past the python requirements installing.

   To create one, you can use the following command:

   ```
   isengardcli add-profile
   ```

   This will interactively guide you through creating a profile for your internal account. 

4. Set the AWS_PROFILE environment variable:

   ```
   export AWS_PROFILE=your-profile-name
   ```

   Replace `your-profile-name` with the profile name you created or want to use. It's usually `${UserName}-Admin` like `gcline-Admin`.
   
5. Set region to `us-east-1`

```
export AWS_REGION=us-east-1
```

## Configuration

1. Open the `config.yaml` file and adjust the settings as needed:

   [View config.yaml](https://code.amazon.com/packages/Claude-TCX3/blobs/main/--/config.yaml)

   Must Change:
   - `SERVICE_NAME`: The service name (e.g., "Amazon EKS")
   - `MARKDOWN_DIRECTORY`: Path to the markdown build output directory

   Configuration options for Title Generation:
   - `MAX_FILES`: Number of markdown files to process
     - set this to ~10 while you are testing
   - `OUTPUT_CSV_FILE`: Path for the output CSV file
   - `MAX_WORKERS`: Number of concurrent workers
	   - ~10-20. Bedrock has a max of 500 requests per minute for Claude 3 Sonnet.
   - `BEDROCK_MODEL`: AWS Bedrock model to use

	 Configuration options for XML Rewriting:
   - `REWRITE_INPUT_FILE`: Input file for XML modification
	   - You could set this to the same CSV file as the generation output. 
   - `XML_DIRECTORY`: Directory containing XML files to modify
	   - Should have “book.xml” in it. 

   Advanced Options:
   - `LOGGING_DIR`: Directory for log files
   - `CONSOLE_LOGS_ENABLED`: Enable/disable console logging
 


## Usage - Generate Titles & Abstracts

1. Double check AWS_PROFILE and AWS_REGION is set

   ```
   echo My Profile is $AWS_PROFILE and my region is $AWS_REGION
   ```

1. Activate the Python virtual environment:

   ```
   source venv/bin/activate
   ```

1. Run the main script:

   For normal operation (generating titles/abstracts):
   ```
   python main.py
   ```

1. Check the output:
   - For normal operation, results will be saved to the CSV file specified in `OUTPUT_CSV_FILE`.

1. Deactivate the python environment

   ```
   deactivate
   ```

## Usage - Modify XML

   - Check out a new branch before doing this
   - `REWRITE_INPUT_FILE`: Input CSV file for XML modification
   - `XML_DIRECTORY`: Directory containing XML files to modify
   - Note this adds the new tags as *comments*, you will need to uncomment them and add entities.
   - Look at the repo with SourceTree or another git tool to browse the changes.

   ```shell
   pyhton main.py --modify-xml
   ```

[View sample CR with comments added](https://code.amazon.com/reviews/CR-136403938/revisions/1#/diff)

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