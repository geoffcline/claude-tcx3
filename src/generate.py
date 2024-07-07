import logging
from config import get_config
import utils, prompts
import os
import concurrent.futures
import tqdm

def process_single_file(file_path, bedrock_client):
    logger = logging.getLogger(f"FileProcessor-{os.path.basename(file_path)}")
    logger.info(f"Processing file: {file_path}")

    try:
        filename = os.path.basename(file_path)

        content = utils.read_markdown_file(file_path)
        existing_title = utils.extract_title(content)
        existing_title_length = len(existing_title)
        abstract = prompts.generate_abstract(bedrock_client, content, filename)
        new_title = prompts.generate_new_title(bedrock_client, existing_title, abstract, filename)
        new_title_length = len(new_title)
        first_paragraph = utils.extract_first_paragraph(content)

        logger.info(f"Completed processing file: {file_path}")
        return {
            "File Name": filename,
            "Existing Title": existing_title,
            "Existing Title Length": existing_title_length,
            "AI Generated Abstract": abstract,
            "AI Generated Title": new_title,
            "AI Generated Title Length": new_title_length,
            "First Paragraph": first_paragraph
        }
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return None


def process_markdown_files(directory, bedrock_client):
    config = get_config()
    logger = logging.getLogger("MarkdownProcessor")
    logger.info(f"Processing markdown files in directory: {directory}")
    results = []

    try:
        markdown_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".md")]
        total_files = min(len(markdown_files), config['MAX_FILES'])

        with concurrent.futures.ThreadPoolExecutor(max_workers=config['MAX_WORKERS']) as executor:
            future_to_file = {executor.submit(process_single_file, file_path, bedrock_client): file_path
                              for file_path in markdown_files[:total_files]}

            with tqdm(total=total_files, desc="Processing files") as pbar:
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except Exception as exc:
                        logger.error(f'{file_path} generated an exception: {exc}')
                    finally:
                        pbar.update(1)

        logger.info(f"Processed {len(results)} markdown files.")
        return results
    except Exception as e:
        logger.error(f"Error in process_markdown_files: {str(e)}")
        return []



