import os, json
from datetime import datetime, timezone
from dotenv import load_dotenv

def Load_ENV(env_path=None):
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

def Get_ENV(key):
    try:
        return os.environ[key]
    except KeyError:
        raise KeyError(f"Environment variable '{key}' not found.")

def Get_UnixTimestamp_UTC():
    timestamp = datetime.now(tz=timezone.utc).timestamp()
    return int(timestamp)

def GetUnixTime_UTC():
    timestamp = datetime.now(tz=timezone.utc)
    time_str = timestamp.strftime("%H:%M:%S")
    return time_str

# Roles
def save_roles_json(data, file_path='./data/roles.json'):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def load_roles_json(file_path='./data/roles.json'):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)