import os, json
from datetime import datetime, timezone
from dotenv import load_dotenv

def Load_ENV(env_path=None):
    """
    Load environment variables from a .env file.

    This function loads environment variables from a specified .env file.
    If no file path is provided, it defaults to loading from a .env file
    in the current working directory.

    Parameters:
    env_path (str, optional): The path to the .env file. Defaults to None.

    Returns:
    None
    """
    if env_path is None:
        return None
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

def Get_ENV(key):
    """
    Retrieve the value of an environment variable.

    Args:
        key (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the environment variable.

    Raises:
        KeyError: If the environment variable is not found.
    """
    try:
        return os.environ[key]
    except KeyError:
        raise KeyError(f"Environment variable '{key}' not found.")

def Get_UnixTimestamp_UTC():
    """
    Get the current Unix timestamp in UTC.

    This function returns the current time as a Unix timestamp (the number of seconds since January 1, 1970) in Coordinated Universal Time (UTC).

    Returns:
        int: The current Unix timestamp in UTC.
    """
    timestamp = datetime.now(tz=timezone.utc).timestamp()
    return int(timestamp)

def GetUnixTime_UTC():
    """
    Get the current time in UTC as a string formatted as HH:MM:SS.

    Returns:
        str: The current time in UTC formatted as HH:MM:SS.
    """
    timestamp = datetime.now(tz=timezone.utc)
    time_str = timestamp.strftime("%H:%M:%S")
    return time_str



# JSON Save & Load Functions

def save_json(data, file_path=None):
    """
    Save a dictionary or JSON object to a file.

    Parameters:
    data (dict): The data to be saved. Must be a dictionary or JSON object.
    file_path (str): The path to the file where the data will be saved. Default is None.

    Raises:
    ValueError: If data or file_path is empty.
    """
    if not data or not file_path:
        raise ValueError("Data or file path is empty.")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def load_json(file_path=None):
    """
    Load data from a JSON file.

    Parameters:
    file_path (str): The path to the file from which the data will be loaded. Default is None.

    Returns:
    dict: The data loaded from the JSON file.

    Raises:
    ValueError: If file_path is empty.
    FileNotFoundError: If the file does not exist.
    """
    if not file_path:
        raise ValueError("File path is empty.")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)