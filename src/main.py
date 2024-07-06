import os
from tqdm import tqdm
import utils, prompts

MAX_FILES = 10
AWS_PROFILE = "gcline-Admin"
SERVICE_NAME = "AWS Batch"
MARKDOWN_DIRECTORY = "../input-markdown"
OUTPUT_CSV_FILE = "../output/claude-tcx3.csv"


def process_markdown_files(bedrock, directory):
    print(f"Processing markdown files in directory: {directory}")
    results = []
    counter = 0

    markdown_files = [f for f in os.listdir(directory) if f.endswith(".md")]
    total_files = min(len(markdown_files), MAX_FILES)

    with tqdm(total=total_files, desc="Processing files") as pbar:
        for filename in markdown_files:
            if counter < MAX_FILES:
                file_path = os.path.join(directory, filename)
                content = utils.read_markdown_file(file_path)
                existing_title = utils.extract_title(content)
                existing_title_length = len(existing_title)
                abstract = prompts.generate_abstract(bedrock, content, filename)
                new_title = prompts.generate_new_title(bedrock, existing_title, abstract)
                new_title_length = len(new_title)
                first_paragraph = utils.extract_first_paragraph(content)  # New line

                results.append({
                    "File Name": filename,
                    "Existing Title": existing_title,
                    "Existing Title Length": existing_title_length,
                    "AI Generated Abstract": abstract,
                    "AI Generated Title": new_title,
                    "AI Generated Title Length": new_title_length,
                    "First Paragraph": first_paragraph  # New line
                })
                counter += 1
                pbar.update(1)
            else:
                break

    print(f"Processed {counter} markdown files.")
    return results


# Main execution
if __name__ == "__main__":
    print("Starting markdown processing and analysis...")
    os.environ["AWS_PROFILE"] = AWS_PROFILE
    bedrock = utils.initialize_bedrock()
    results = process_markdown_files(bedrock, MARKDOWN_DIRECTORY)
    utils.save_to_csv(results, OUTPUT_CSV_FILE)
    print(f"Markdown analysis completed. Results saved to {OUTPUT_CSV_FILE}")
    print("Process completed successfully.")
