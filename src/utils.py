import re
import boto3
import csv


def read_markdown_file(file_path):
    print(f"Reading markdown file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    print(f"Successfully read {len(content)} characters from {file_path}")
    return content


def save_to_csv(results, output_file):
    print(f"Saving results to CSV file: {output_file}")
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
    print(f"Results saved successfully to {output_file}")


def initialize_bedrock():
    print("Initializing Bedrock client...")
    bedrock = boto3.client(service_name="bedrock-runtime")
    print("Bedrock client initialized successfully.")
    return bedrock


def extract_title(content):
    # Extract the first h1 title from the markdown content and remove <a> tags
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1)
        # Remove <a> tags
        title = re.sub(r'<a\s+[^>]*>|</a>', '', title)
        return title.strip()
    return ""


def extract_first_paragraph(content):
    """
    Extract the first paragraph from the given markdown content.

    Args:
    content (str): The full markdown content.

    Returns:
    str: The first paragraph of the content, or an empty string if no paragraph is found.
    """
    print("Extracting first paragraph from markdown content...")

    # Split the content into lines
    lines = content.split('\n')

    paragraph = []
    for line in lines:
        # Skip empty lines and lines starting with '#' (headers)
        if line.strip() and not line.strip().startswith('#'):
            paragraph.append(line.strip())
        elif paragraph:
            # If we've already started collecting a paragraph and hit an empty line, we're done
            break

    result = ' '.join(paragraph)
    print(f"Extracted first paragraph: {result[:50]}...")  # Print first 50 chars for debugging
    return result
