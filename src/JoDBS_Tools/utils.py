import os
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