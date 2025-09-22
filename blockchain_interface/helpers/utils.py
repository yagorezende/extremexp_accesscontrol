import json

def load_json_from_file(file_path):
    """
    Load JSON data from a file.
    :param file_path: str - path to the JSON file
    :return: dict - JSON data
    """
    with open(file_path, 'r') as file:
        return json.load(file)