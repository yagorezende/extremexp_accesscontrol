import json

def load_json_from_file(file_path):
    """
    Load JSON data from a file.
    :param file_path: str - path to the JSON file
    :return: dict - JSON data
    """
    with open(file_path, 'r') as file:
        return json.load(file)


def transaction_to_dict(tx):
    """
    Convert a transaction object to a dictionary.
    :param tx: transaction object
    :return: dict - transaction data
    """
    result = {}
    for key in tx.keys():
        value = tx[key]
        if isinstance(value, bytes):
            result[key] = value.hex()
        elif isinstance(value, dict):
            result[key] = transaction_to_dict(value)
        else:
            result[key] = value
    return result