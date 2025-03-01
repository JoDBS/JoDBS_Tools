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

    # def get_roles_json(self):
    #     print(f"> DataFetching.py: Attempting to get roles.json from BotNetworkConnection.")
    #     roles = self.BNC.fetch_and_save_roles()
    #     if roles:
    #         print(f"> DataFetching.py: Successfully fetched roles.json from BotNetworkConnection.")
    #     else:
    #         print(f"> DataFetching.py: Failed to fetch roles.json from BotNetworkConnection.")

    def get_by_scope(self, scope: str):
        try:
            data = self.BNC.get_data(scope=scope)

            if self.debug:
                print(f"> {self.file_name}: Getting {scope} from BotNetworkConnection")
                print(f"> {self.file_name}: Data: {data}")
            
            if data:
                print(f"> {self.file_name}: Successfully fetched {scope} from BotNetworkConnection.")
                data_json = {scope: data}
                save_json(data_json, f"{self.data_folder}/{scope}.json")
                
        except Exception as e:
            print(f"> {self.file_name}: Failed to fetch {scope} from BotNetworkConnection.")
            print(f"> {self.file_name}: Error: {e}")

    def get_all_available_scopes(self):

        for scope in self.default_scopes:
            self.get_by_scope(scope=scope)



        # Attempting to get all available data from BotNetworkConnection using scope full.
        # scope = "full"
        # print(f"> DataFetching.py: Attempting to get all available data from BotNetworkConnection using scope '{scope}'.")
        # data = self.BNC.get_data(scope=scope)
        # if data:
        #     print(f"> DataFetching.py: Successfully fetched data from BotNetworkConnection.")
        #     save_json(data, "data/all_data.json")
        # else:
        #     print(f"> DataFetching.py: Failed to fetch data from BotNetworkConnection.")