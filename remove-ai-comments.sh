#!/bin/bash

# Check if directory is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

directory="$1"

# Find all XML files in the directory and its subdirectories
find "$directory" -type f -name "*.xml" | while read -r file; do
    echo "Processing file: $file"

    # Use sed to remove the auto-generated content
    sed -i '/<!-- START_AUTO_GENERATED_CONTENT/,/END_AUTO_GENERATED_CONTENT -->/d' "$file"

    echo "Finished processing: $file"
done

echo "All XML files have been processed."