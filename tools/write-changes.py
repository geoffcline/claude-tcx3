import os
import re

def parse_meta_document(file_path):
    sections = []
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().startswith('<!-- START:'):
                if current_section:
                    sections.append(current_section)
                current_section = {'content': []}
                match = re.search(r'<!-- START: (.+):(\d+) -->', line)
                if match:
                    current_section['file'] = match.group(1)
                    current_section['start'] = int(match.group(2))
            elif line.strip().startswith('<!-- END:'):
                match = re.search(r'<!-- END: .+:(\d+) -->', line)
                if match:
                    current_section['end'] = int(match.group(1))
                sections.append(current_section)
                current_section = None
            elif current_section:
                current_section['content'].append(line.rstrip())

    return sections

def update_source_files(sections, source_directory):
    for section in sections:
        file_path = os.path.join(source_directory, section['file'])
        if not os.path.exists(file_path):
            print(f"Warning: Source file not found: {file_path}")
            continue

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        # Calculate the number of lines to replace
        original_lines = section['end'] - section['start'] + 1
        new_lines = len(section['content'])

        # Replace the lines in the original content
        content[section['start']-1:section['end']] = section['content']

        # Adjust line numbers for subsequent sections in the same file
        line_diff = new_lines - original_lines
        for s in sections:
            if s['file'] == section['file'] and s['start'] > section['start']:
                s['start'] += line_diff
                s['end'] += line_diff

        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(line + '\n' for line in content)

        print(f"Updated {file_path}")

# Usage
meta_document = os.environ.get('META_DOCUMENT', 'meta_document.xml')
source_directory = os.environ.get('SOURCE_DIR', '.')

sections = parse_meta_document(meta_document)
update_source_files(sections, source_directory)

print("All source files have been updated.")