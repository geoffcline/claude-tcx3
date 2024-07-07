import re
import boto3
import csv
import os
import logging
import subprocess
import json

def verify_aws_environment(config, logger):
    logger.info("Verifying AWS environment...")

    # Check AWS_PROFILE environment variable
    if 'AWS_PROFILE' in os.environ:
        logger.info(f"AWS_PROFILE is set to: {os.environ['AWS_PROFILE']}")
    else:
        logger.error("AWS_PROFILE environment variable is not set.")
        return False

    # Check AWS identity
    if check_aws_identity():
        logger.info("AWS identity check passed. 'isengard' found in the ARN.")
    else:
        logger.error("AWS identity check failed or 'isengard' not found in the ARN.")
        return False

    logger.info("All AWS environment checks passed successfully!")
    return True

def read_markdown_file(file_path):
    logger = logging.getLogger(f"FileReader-{os.path.basename(file_path)}")
    logger.info(f"Reading markdown file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    logger.info(f"Successfully read {len(content)} characters from {file_path}")
    return content


def save_to_csv(results, output_file):
    logger = logging.getLogger(f"CsvWriter")
    logger.info(f"Saving results to CSV file: {output_file}")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['File Name', 'Existing Title', 'Existing Title Length',
                      'AI Generated Abstract', 'AI Generated Title', 'AI Generated Title Length',
                      'First Paragraph']  # Added 'First Paragraph' to fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in results:
            # Ensure all fields are present in each row, with empty string as default
            row_data = {field: row.get(field, '') for field in fieldnames}
            writer.writerow(row_data)
    logger.info(f"Results saved successfully to {output_file}")


def initialize_bedrock():
    bedrock = boto3.client(service_name="bedrock-runtime")
    return bedrock


def extract_title(content):
    logger = logging.getLogger('TitleExtractor')
    logger.info("Starting title extraction")

    # Extract the first h1 title from the markdown content and remove <a> tags
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1)
        logger.debug(f"Found raw title: {title}")

        # Remove <a> tags
        title = re.sub(r'<a\s+[^>]*>|</a>', '', title)
        cleaned_title = title.strip()
        logger.info(f"Extracted and cleaned title: {cleaned_title}")
        return cleaned_title

    logger.warning("No title found in the content")
    return ""


def check_aws_identity():
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], capture_output=True, text=True)
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            return 'isengard' in identity.get('Arn', '').lower()
        else:
            logging.error(f"Error checking AWS identity: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error checking AWS identity: {e}")
        return False


def extract_first_paragraph(content):
    logger = logging.getLogger('ParagraphExtractor')
    logger.info("Starting first paragraph extraction")

    lines = content.split('\n')
    paragraph = []
    skip_mode = False
    blank_line_encountered = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if not stripped_line:
            if skip_mode:
                skip_mode = False
                logger.debug(f"Exiting skip mode at line {i}")
            elif paragraph:
                logger.debug(f"End of paragraph encountered at line {i}")
                break  # End of a non-skipped paragraph
            blank_line_encountered = True
            continue

        if stripped_line.startswith('**'):
            skip_mode = True
            paragraph = []  # Reset any collected paragraph
            logger.debug(f"Entering skip mode at line {i}")
            continue

        if not skip_mode and blank_line_encountered:
            if not stripped_line.startswith('#'):
                paragraph.append(stripped_line)
                logger.debug(f"Added line to paragraph: {stripped_line[:30]}...")

    result = ' '.join(paragraph)
    logger.info(f"Extracted first paragraph: {result[:50]}...")
    return result
