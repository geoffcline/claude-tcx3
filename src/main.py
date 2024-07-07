import os
import utils, generate, logging_config, modify, prompts
import logging
import argparse
from config import load_config, get_config
from botocore.exceptions import BotoCoreError, ClientError

def main():
    parser = argparse.ArgumentParser(description="Process markdown files and modify XML with configurable settings.")
    parser.add_argument("--config", default="config.yaml", help="Path to the configuration file")
    parser.add_argument("--verify", action="store_true", help="Run verification only")
    parser.add_argument("--modify-xml", action="store_true", help="Run XML modification")
    args = parser.parse_args()

    try:
        load_config(args.config)
        config = get_config()

        logger = logging_config.setup_logging(
            log_level=logging.DEBUG,  # Capture all log levels in the file
            log_dir=config['LOGGING_DIR']
        )

        # Run Environment Checks
        if not utils.verify_aws_environment(config):
            logger.error("AWS environment verification failed. Please check the logs and resolve any issues.")
            return

        # If `--verify` mode, exit and don't run
        if args.verify:
            logger.info("Verification completed successfully.")
            return

        # mode switch, modify xml vs regular (generate titles/abstracts)
        if args.modify_xml:
            modify.modify_xml_files(config['REWRITE_INPUT_FILE'], config['XML_DIRECTORY'])
        else:
            try:
                bedrock_client = utils.initialize_bedrock()

                prompts.validate_bedrock_connection(bedrock_client, config['BEDROCK_MODEL'])

                logger.info("Starting concurrent markdown processing and analysis...")
                results = generate.process_markdown_files(config['MARKDOWN_DIRECTORY'], bedrock_client)
                utils.save_to_csv(results, config['OUTPUT_CSV_FILE'])
                logger.info(f"Markdown analysis completed. Results saved to {config['OUTPUT_CSV_FILE']}")
            except Exception as e:
                logger.error(f"Error during markdown processing: {e}", exc_info=True)

        logger.info("Process completed successfully.")
    except Exception as e:
        if logger:
            logger.error(f"An error occurred during processing: {e}", exc_info=True)
        else:
            print(f"An error occurred during processing: {e}")


if __name__ == "__main__":
    main()