import logging
from config import get_config
import pandas as pd
import os
import re


def modify_xml_files(csv_path, xml_directory):
    logger = logging.getLogger(__name__)
    logger.info(f"Starting XML modification process")
    logger.info(f"CSV file path: {csv_path}")
    logger.info(f"XML directory: {xml_directory}")

    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        logger.info(f"Successfully read CSV file. Found {len(df)} rows.")

        # Remove ".md" suffix from ID column
        df['File Name'] = df['File Name'].str.replace('.md$', '', regex=True)
        logger.debug("Removed '.md' suffix from 'File Name' column")

        # Iterate through all XML files in the directory and its subdirectories
        for root, dirs, files in os.walk(xml_directory):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    logger.debug(f"Processing file: {file_path}")

                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()

                        # Find all section tags with id attribute
                        sections = re.findall(r'<section\s+[^>]*id="([^"]+)"[^>]*>', content)
                        logger.debug(f"Found {len(sections)} sections in {file}")

                        modified = False
                        for section_id in sections:
                            # Find matching row in CSV
                            row = df[df['File Name'] == section_id]
                            if not row.empty:
                                title = row['AI Generated Title'].values[0]
                                abstract = row['AI Generated Abstract'].values[0]
                                logger.debug(f"Found matching data for section ID: {section_id}")

                                # Create new XML lines wrapped in a comment with unique markers
                                new_lines = f'''
    <!-- START_AUTO_GENERATED_CONTENT
    <title id="{section_id}.title">{title}</title>
    <abstract><para>{abstract}</para></abstract>
    END_AUTO_GENERATED_CONTENT -->
    '''

                                # Find the position to insert the new lines
                                section_start = re.search(f'<section\\s+[^>]*id="{section_id}"[^>]*>', content)
                                if section_start:
                                    insert_pos = section_start.end()

                                    # Check if the content already exists
                                    if 'START_AUTO_GENERATED_CONTENT' not in content[insert_pos:insert_pos + 100]:
                                        # Insert the new lines
                                        content = content[:insert_pos] + new_lines + content[insert_pos:]
                                        modified = True
                                        logger.info(f"Added new content for section ID: {section_id}")
                                    else:
                                        logger.debug(f"Content already exists for section ID: {section_id}")
                                else:
                                    logger.warning(f"Could not find section start for ID: {section_id}")
                            else:
                                logger.warning(f"No matching data found for section ID: {section_id}")

                        # Write the modified content back to the file only if changes were made
                        if modified:
                            with open(file_path, 'w') as f:
                                f.write(content)
                            logger.info(f"Successfully modified {file_path}")
                        else:
                            logger.info(f"No changes needed for {file_path}")
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)

        logger.info("XML modification process completed successfully")
    except Exception as e:
        logger.error(f"Error in modify_xml_files: {str(e)}", exc_info=True)
        raise