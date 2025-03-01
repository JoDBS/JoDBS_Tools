import os
from .Database import BotNetworkConnection
from .utils import save_json, load_json, Load_ENV, Get_ENV, Get_ENV_Bool

class DataFetching:
    def __init__(self, debug=False):
        self.debug = debug
        self.file_name = os.path.basename(__file__)
        self.data_folder = "./data"
        
        # Convert comma-separated string from env var to a list
        default_scopes_str = Get_ENV("DEFAULT_SCOPES")
        self.default_scopes = default_scopes_str.split(",") if default_scopes_str else []
        
        self.__create_data_folder()
        self.BNC = BotNetworkConnection()


    def __create_data_folder(self):
        try:
            os.makedirs(self.data_folder)
            print("> DataFetching.py: Created data folder.")
            return
        except FileExistsError:
            return


    def get_by_scope(self, scope: str):
        try:
            data = self.BNC.get_data(scope=scope)

            if self.debug:
                print(f"> {self.file_name}: Getting {scope} from BotNetworkConnection")
                print(f"> {self.file_name}: Data: {data}")
            
            if data:
                data_json = {scope: data}
                save_json(data_json, f"{self.data_folder}/{scope}.json")
                print(f"> {self.file_name}: Successfully fetched {scope} from BotNetworkConnection.")
                
        except Exception as e:
            print(f"> {self.file_name}: Failed to fetch {scope} from BotNetworkConnection.")
            # print(f"> {self.file_name}: Error: {e}")
            # Create an empty file as fallback
            try:
                file_path = f"{self.data_folder}/{scope}.json"
                save_json({}, file_path)
            except Exception as save_error:
                print(f"> {self.file_name}: Failed to create fallback file: {save_error}")

    def get_all_available_scopes(self):

        for scope in self.default_scopes:
            self.get_by_scope(scope=scope)