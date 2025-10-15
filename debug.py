import os
import json

# Assuming this is in your project directory
models_dir = 'models/saved_models/'  # Adjust path as needed

# List all metadata files
metadata_files = [f for f in os.listdir(models_dir) if f.endswith('_metadata.json')]

print("Metadata files found:")
for filename in metadata_files:
    filepath = os.path.join(models_dir, filename)

    # Print full file path
    print(f"\nFile: {filepath}")

    # Print file size
    print(f"File size: {os.path.getsize(filepath)} bytes")

    # Try to read and print file contents
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            print("File contents:")
            print(content)

            # Try to parse JSON
            try:
                json.loads(content)
                print("✅ Valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                # Print the problematic part of the file
                print(f"Error occurs near: {content[max(0, e.pos - 50):e.pos + 50]}")
    except Exception as e:
        print(f"Error reading file: {e}")