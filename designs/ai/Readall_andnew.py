

import os
import time
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# Set your OpenAI API key

MAX_TOKENS_PER_REQUEST = 30000
MAX_TOKENS_PER_CHUNK = 25000  # Leave some buffer for system messages and overhead
RATE_LIMIT_TOKENS_PER_MINUTE = 30000  # The token limit per minute
SECONDS_PER_MINUTE = 60

def find_python_files(start_folder):
    """Recursively find all .py files starting from the given folder."""
    python_files = []
    for root, _, files in os.walk(start_folder):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def read_files(file_paths):
    """Read the content of all files provided in the list."""
    contents = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents.append(file.read())
    return contents

def split_content(content, max_tokens):
    """Split the content into smaller chunks to fit within the token limit."""
    chunks = []
    current_chunk = []
    current_length = 0

    for line in content.split('\n'):
        line_length = len(line.split())
        if current_length + line_length <= max_tokens:
            current_chunk.append(line)
            current_length += line_length
        else:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = line_length

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

def create_new_file_from_api(file_chunks):
    """Create a new file using the content from the API."""
    new_file_content = ""
    tokens_used = 0
    for chunk in file_chunks:
        if tokens_used + len(chunk.split()) > RATE_LIMIT_TOKENS_PER_MINUTE:
            
            tokens_used = 0  # Reset the counter after waiting

        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=[

                {"role": "user", "content": chunk}
            ],
            max_tokens=4096  # Buffer for system messages
        )
        new_file_content += response.choices[0].message['content'] + "\n"
        tokens_used += len(chunk.split())  # Update the counter
    return new_file_content

def main():
    start_folder = 'proj'
    output_file = 'ai_generated.py'

    python_files = find_python_files(start_folder)
    file_contents = read_files(python_files)
    combined_content = "\n".join(file_contents)

    while len(combined_content.split()) > MAX_TOKENS_PER_REQUEST:
        # Remove a file to reduce the content size
        removed_file = python_files.pop()
        print(f"Removing file {removed_file} to stay within token limit.")
        file_contents = read_files(python_files)
        combined_content = "\n".join(file_contents)

    file_chunks = split_content(combined_content, MAX_TOKENS_PER_CHUNK)


    for chunk in file_chunks:
        
        new_file_content=create_new_file_from_api(chunk)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(new_file_content)

        time.sleep(63)

    print(f"New file created at {output_file}")

if __name__ == "__main__":
    main()
