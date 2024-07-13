import json
import pdb
import sys
import hashlib
def load_json(file_path):
    """
    Load a JSON file into a dictionary.
    
    :param file_path: The path to the JSON file.
    :return: A dictionary containing the JSON data.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except json.JSONDecodeError:
        print(f"The file {file_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred: {e}")



def hash_data(data):
    # Ensure the data is in bytes format
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()
    
    # Update the hash object with the data
    hash_object.update(data)
    
    # Retrieve the hexadecimal representation of the hash
    hex_dig = hash_object.hexdigest()
    
    return hex_dig


# Example usage:
if __name__ == "__main__":
    files =  sys.argv[1:]# Replace with your JSON file path
    root = ""
    for file_path in files : 
        data = load_json(file_path)
        if data:
            root = hash_data(str(data) + root)
    print(f"Hashed data: {root}")


