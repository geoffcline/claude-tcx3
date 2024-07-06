import os
import concurrent.futures
from tqdm import tqdm
import utils, prompts
import boto3
import time
from botocore.config import Config

MAX_FILES = 300
AWS_PROFILE = "gcline-Admin"
SERVICE_NAME = "Amazon EKS"
MARKDOWN_DIRECTORY = "../input-markdown"
OUTPUT_CSV_FILE = "../output/claude-tcx3.csv"
MAX_WORKERS = 5
MAX_RETRIES = 3
RATE_LIMIT = 10  # Adjust based on your Bedrock rate limit


def create_bedrock_client():
    retry_config = Config(
        retries={'max_attempts': MAX_RETRIES, 'mode': 'adaptive'}
    )
    session = boto3.Session(profile_name=AWS_PROFILE)
    return session.client('bedrock-runtime', config=retry_config)


bedrock_client = create_bedrock_client()


def process_single_file(file_path):
    filename = os.path.basename(file_path)
    print(f"Processing file: {filename}")

    content = utils.read_markdown_file(file_path)
    existing_title = utils.extract_title(content)
    existing_title_length = len(existing_title)
    abstract = prompts.generate_abstract(bedrock_client, content, filename)
    new_title = prompts.generate_new_title(bedrock_client, existing_title, abstract)
    new_title_length = len(new_title)
    first_paragraph = utils.extract_first_paragraph(content)

    return {
        "File Name": filename,
        "Existing Title": existing_title,
        "Existing Title Length": existing_title_length,
        "AI Generated Abstract": abstract,
        "AI Generated Title": new_title,
        "AI Generated Title Length": new_title_length,
        "First Paragraph": first_paragraph
    }


def process_markdown_files(directory):
    print(f"Processing markdown files in directory: {directory}")
    results = []

    markdown_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".md")]
    total_files = min(len(markdown_files), MAX_FILES)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {executor.submit(process_single_file, file_path): file_path
                          for file_path in markdown_files[:total_files]}

        with tqdm(total=total_files, desc="Processing files") as pbar:
            completed_tasks = 0
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'{file_path} generated an exception: {exc}')
                finally:
                    pbar.update(1)
                    completed_tasks += 1
                    if completed_tasks % RATE_LIMIT == 0:
                        time.sleep(1)  # Simple rate limiting

    print(f"Processed {len(results)} markdown files.")
    return results


# Main execution
if __name__ == "__main__":
    print("Starting concurrent markdown processing and analysis...")
    os.environ["AWS_PROFILE"] = AWS_PROFILE
    results = process_markdown_files(MARKDOWN_DIRECTORY)
    utils.save_to_csv(results, OUTPUT_CSV_FILE)
    print(f"Markdown analysis completed. Results saved to {OUTPUT_CSV_FILE}")
    print("Process completed successfully.")