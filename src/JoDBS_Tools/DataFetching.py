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
            print(f"> {self.file_name}: Created data folder.")
            return
        except FileExistsError:
            return


    def get_by_scope(self, scope: str):
        file_path = f"{self.data_folder}/{scope}.json"
        try:
            data = self.BNC.get_data(scope=scope)

            if self.debug:
                print(f"> {self.file_name}: Getting {scope} from BotNetworkConnection")
                print(f"> {self.file_name}: Data: {data}")
            
            if data:
                data_json = {scope: data}
                save_json(data_json, file_path)
                print(f"> {self.file_name}: Successfully fetched {scope} from BotNetworkConnection.")
            else:
                # If no data received, create empty file
                save_json({}, file_path)
                print(f"> {self.file_name}: No data received, created empty file for {scope}")
                
        except Exception as e:
            print(f"> {self.file_name}: Failed to fetch {scope} from BotNetworkConnection: {e}")
            save_json({}, file_path)
            print(f"> {self.file_name}: Created empty fallback file for {scope}")

    def get_all_available_scopes(self):

        for scope in self.default_scopes:
            self.get_by_scope(scope=scope)