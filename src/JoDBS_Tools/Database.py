import requests
from pymongo import MongoClient, errors
from .utils import Get_ENV

class Database:
    def __init__(self, connection_string=None, collection=None, database_name=None):
        self.connection_string = connection_string or Get_ENV("CONNECTION_STRING")
        self.collection = collection
        self.database_name = database_name or Get_ENV("DATABASE_NAME")
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            if not self.database_name:
                raise errors.ConfigurationError("No default database defined")
            self.db = self.client[self.database_name]
            self.ensure_collection_exists()
            print("MongoDB Connection: Successful ✔️")
        except errors.ServerSelectionTimeoutError as err:
            print(f"MongoDB Connection: Failed ❌ - {err}")
            raise Exception("MongoDB Connection: Failed ❌")
        except errors.ConfigurationError as err:
            print(f"MongoDB Configuration Error: ❌ - {err}")
            raise Exception("MongoDB Configuration Error: ❌")

    def get_database(self):
        if not self.db:
            self.connect()
        return self.db
    
    def exists(self):
        try:
            self.client.server_info()
            return True
        except errors.ServerSelectionTimeoutError:
            return False
    
    def create_collection(self, collection_name):
        try:
            self.db.create_collection(collection_name)
            print(f"Collection '{collection_name}' created successfully.")
        except errors.CollectionInvalid as err:
            print(f"Collection '{collection_name}' creation failed. Error: {err}")
            raise Exception(f"Collection '{collection_name}' creation failed. Error: {err}")
        
    def ensure_collection_exists(self):
        if self.collection not in self.db.list_collection_names():
            self.create_collection(self.collection)
    
    def check_status(self):
        try:
            if not self.db:
                self.connect()
            self.client.server_info()
            print("MongoDB Connection: Successful ✔️")
        except errors.ServerSelectionTimeoutError as err:
            print(f"MongoDB Connection: Failed ❌ - {err}")
            raise Exception("MongoDB Connection: Failed ❌")

class BotNetworkConnection:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url or Get_ENV(key="BNC_BASE_URL")
        self.token = api_key or Get_ENV(key="BNC_API_KEY")
        self.headers = {
            "x-api-key": self.token,
            "Content-Type": "application/json"
        }

    def get_data(self, application_id, scope="full"):
        url = f"{self.base_url}/data/{application_id}"
        response = requests.get(url, headers=self.headers)

        if scope == "full":
            return self._handle_response(response)
        elif scope == "version":
            data = self._handle_response(response)
            return data.get('data', {}).get('version')
        elif scope == "startup_info":
            data = self._handle_response(response)
            return data.get('data', {}).get('startup_info')
        elif scope == "roles":
            data = self._handle_response(response)
            return data.get('data', {}).get('roles')
        
        ### TODO: if scope is == "full", then give full data, else try to give .get(scope), if not, return None

    def create_data(self, application_id, data):
        url = f"{self.base_url}/data"
        payload = {
            "applicationId": application_id,
            "data": data
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return self._handle_response(response)

    def update_data(self, application_id, data):
        url = f"{self.base_url}/data/{application_id}"
        payload = {
            "data": data
        }
        response = requests.put(url, headers=self.headers, json=payload)
        return self._handle_response(response)

    def delete_data(self, application_id):
        url = f"{self.base_url}/data/{application_id}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)

    # def get_startup_info(self, application_id):
    #     url = f"{self.base_url}/"

    def check_status(self):
        url = f"{self.base_url}/status"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print("BotNetworkConnection: ✔️")
            return response.json()
        except requests.exceptions.ConnectionError:
            print("BotNetworkConnection: Failed ❌ - Please check if the BotNetworkConnection server is running.")
            return None
        except requests.exceptions.HTTPError as err:
            print(f"BotNetworkConnection: Failed ❌ - {err}")
            raise Exception("BotNetworkConnection: Failed ❌")

    def _handle_response(self, response):
        if response.status_code in [200, 201]:
            return response.json()
        else:
            response.raise_for_status()