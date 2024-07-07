import os
import subprocess
import sys
import concurrent.futures
from tqdm import tqdm
import utils, prompts, logging_config
import time
import logging
import json
import yaml
import argparse
from config import load_config, get_config


def verify_environment(config, logger):
    logger.info("Verifying environment...")

    # Check virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.error("Virtual environment is not active.")
        return False

    # Check requirements
    try:
        import yaml, tqdm, concurrent.futures
        logger.info("Required packages are installed.")
    except ImportError as e:
        logger.error(f"Not all required packages are installed: {e}")
        return False

    # Check isengardcli
    isengardcli_path = utils.check_isengardcli()
    if isengardcli_path:
        logger.info(f"isengardcli found at: {isengardcli_path}")
    else:
        logger.error("isengardcli not found. Please install it if needed.")
        return False

    # Check AWS identity
    if utils.check_aws_identity():
        logger.info("AWS identity check passed. 'isengard' found in the ARN.")
    else:
        logger.error("AWS identity check failed or 'isengard' not found in the ARN.")
        return False

    # Check markdown directory
    if not os.path.exists(config['MARKDOWN_DIRECTORY']) or not any(
            file.endswith('.md') for file in os.listdir(config['MARKDOWN_DIRECTORY'])):
        logger.error(f"Markdown directory {config['MARKDOWN_DIRECTORY']} does not exist or contains no .md files.")
        return False
    else:
        logger.info(f"Markdown directory verified: {config['MARKDOWN_DIRECTORY']}")

    logger.info("All environment checks passed successfully!")
    return True


def process_single_file(file_path, bedrock_client):
    logger = logging.getLogger(f"FileProcessor-{os.path.basename(file_path)}")
    logger.info(f"Processing file: {file_path}")

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


def process_markdown_files(directory, bedrock_client):
    config = get_config()
    logger = logging.getLogger("MarkdownProcessor")
    logger.info(f"Processing markdown files in directory: {directory}")
    results = []

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
                    results.append(result)
                except Exception as exc:
                    logger.error(f'{file_path} generated an exception: {exc}')
                finally:
                    pbar.update(1)

    logger.info(f"Processed {len(results)} markdown files.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Process markdown files with configurable settings.")
    parser.add_argument("--config", default="config.yaml", help="Path to the configuration file")
    parser.add_argument("--verify", action="store_true", help="Run verification only")
    args = parser.parse_args()

    load_config(args.config)
    config = get_config()

    logging_config.setup_logging(log_level=logging.INFO, console_output=config['CONSOLE_LOGS_ENABLED'],
                                 log_dir=config['LOGGING_DIR'])
    logger = logging.getLogger("Main")

    if not verify_environment(config, logger):
        logger.error("Environment verification failed. Please check the logs and resolve any issues.")
        return

    if args.verify:
        logger.info("Verification completed successfully.")
        return

    try:
        bedrock_client = utils.initialize_bedrock()
        logger.info("Starting concurrent markdown processing and analysis...")
        results = process_markdown_files(config['MARKDOWN_DIRECTORY'], bedrock_client)
        utils.save_to_csv(results, config['OUTPUT_CSV_FILE'])
        logger.info(f"Markdown analysis completed. Results saved to {config['OUTPUT_CSV_FILE']}")
        logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during processing: {e}")


if __name__ == "__main__":
    main()