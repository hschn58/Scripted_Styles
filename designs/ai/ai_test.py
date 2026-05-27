from openai import OpenAI
import os

# Set your API key here (ensure it's securely stored)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# Base directory and file path for data.py
base_dir = os.path.expanduser("AI")
file_path = os.path.join(base_dir, "data.py")

# Read the content of the data.py file
try:
    with open(file_path, 'r') as file:
        file_content = file.read()
except FileNotFoundError:
    print(f"Error: {file_path} not found.")
    exit()

# Define the prompt to send to the API
prompt = f"Can you make something similar to this:\n\n{file_content}"

# Call the ChatGPT API using the updated structure
response = client.chat.completions.create(
    model="gpt-4",  # or gpt-3.5-turbo
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=500
)

# Print the response from the ChatGPT API
reply = response.choices[0].message.content
print("ChatGPT Response:\n", reply)
