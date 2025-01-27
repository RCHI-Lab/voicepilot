#!/bin/bash

# Prompt the user for the foods in each bowl
echo "Enter the foods in each bowl:"
read -p "Bowl 0 (closest to Obi's arm): " bowl0
read -p "Bowl 1 (counterclockwise from Bowl 0): " bowl1
read -p "Bowl 2 (counterclockwise from Bowl 1): " bowl2
read -p "Bowl 3 (counterclockwise from Bowl 2): " bowl3
echo

# Define the path to the obi-prompt.txt file
script_dir=$(dirname "$(realpath "$0")")
prompt_file="$script_dir/obi-prompt.txt"

# Update the file with the entered bowl information
if [ -f "$prompt_file" ]; then
  # Read the file into an array
  mapfile -t file_contents < "$prompt_file"
  
  # Modify the specific lines
  file_contents[2]="Bowl 0: $bowl0"
  file_contents[3]="Bowl 1: $bowl1"
  file_contents[4]="Bowl 2: $bowl2"
  file_contents[5]="Bowl 3: $bowl3"

  # Write the modified contents back to the file
  printf "%s\n" "${file_contents[@]}" > "$prompt_file"
else
  echo "Error: File $prompt_file does not exist."
fi

python3 obi-chatgpt-voice.py &
python3 obi-main.py &
