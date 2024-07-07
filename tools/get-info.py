import os


def process_xml_file(file_path):
    filename = os.path.basename(file_path)

    if filename == 'doc-history.xml':
        return []

    output_lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
        in_target_section = False
        in_info_tag = False
        section_content = []
        section_start_line = 0
        info_processed = False
        current_tag = ''

        for line_number, line in enumerate(content, 1):
            stripped_line = line.strip()

            if stripped_line.startswith('<chapter') or (
                    stripped_line.startswith('<section') and 'role="topic"' in stripped_line):
                in_target_section = True
                info_processed = False
                section_start_line = line_number
                current_tag = 'chapter' if stripped_line.startswith('<chapter') else 'section'
                section_content = [
                    f"<!-- START: {filename}:{line_number} -->",
                    line.rstrip()
                ]
            elif in_target_section and not info_processed:
                if stripped_line.startswith('<info>'):
                    in_info_tag = True
                    section_content.append(f"<!-- INFO START: {filename}:{line_number} -->")
                    section_content.append(line.rstrip())
                elif stripped_line.startswith('</info>'):
                    in_info_tag = False
                    info_processed = True
                    section_content.append(line.rstrip())
                    section_content.append(f"<!-- INFO END: {filename}:{line_number} -->")
                elif in_info_tag:
                    section_content.append(line.rstrip())
            elif in_target_section and (
                    stripped_line.startswith('</chapter>') or stripped_line.startswith('</section>')):
                in_target_section = False
                section_content.append(f"<!-- END: {filename}:{line_number} -->")
                section_content.append(f"</{current_tag}>")
                output_lines.extend(section_content)
                output_lines.append("")  # Empty line for readability

    return output_lines


def process_directory(directory):
    all_output_lines = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                all_output_lines.extend(process_xml_file(file_path))
    return all_output_lines


# Usage
directory = os.environ.get('XML_DIR', '.')  # Use XML_DIR env var if set, else use current directory
output_lines = process_directory(directory)

# Write to output file
output_file = os.environ.get('OUTPUT_FILE', 'meta_document.xml')
with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write('<root>\n')  # Add root element to make the entire document valid XML
    outfile.write('\n'.join(output_lines))
    outfile.write('</root>\n')

print(f"Meta-document created: {output_file}")