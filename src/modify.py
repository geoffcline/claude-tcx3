import logging
from config import get_config
import pandas as pd
import os
import re

def modify_xml_files(excel_path, xml_directory):
    logger = logging.getLogger("XMLModifier")
    logger.info(f"Modifying XML files based on Excel data from {excel_path}")

    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)

        # Remove ".md" suffix from ID column
        df['File Name'] = df['File Name'].str.replace('.md$', '', regex=True)

        # Iterate through all XML files in the directory and its subdirectories
        for root, dirs, files in os.walk(xml_directory):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Find all section tags with id attribute
                    sections = re.findall(r'<section\s+[^>]*id="([^"]+)"[^>]*>', content)

                    modified = False
                    for section_id in sections:
                        # Find matching row in Excel
                        row = df[df['File Name'] == section_id]
                        if not row.empty:
                            title = row['AI Generated Title'].values[0]
                            abstract = row['AI Generated Abstract'].values[0]

                            # Create new XML lines wrapped in a comment
                            new_lines = f'''
    <!-- Auto-generated content
    <title id="{section_id}.title">{title}</title>
    <abstract><para>{abstract}</para></abstract>
    -->
    '''

                            # Find the position to insert the new lines
                            section_start = re.search(f'<section\\s+[^>]*id="{section_id}"[^>]*>', content)
                            if section_start:
                                insert_pos = section_start.end()

                                # Check if the content already exists
                                if new_lines not in content[insert_pos:insert_pos+len(new_lines)+100]:
                                    # Insert the new lines
                                    content = content[:insert_pos] + new_lines + content[insert_pos:]
                                    modified = True

                    # Write the modified content back to the file only if changes were made
                    if modified:
                        with open(file_path, 'w') as f:
                            f.write(content)
                        logger.info(f"Modified {file_path}")
                    else:
                        logger.info(f"No changes needed for {file_path}")

        logger.info("XML modification completed successfully")
    except Exception as e:
        logger.error(f"Error in modify_xml_files: {str(e)}")