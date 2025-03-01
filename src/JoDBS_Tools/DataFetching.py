import os
from .Database import BotNetworkConnection
from .utils import save_json, load_json

class DataFetching:
    def __init__(self, debug=False):
        self.debug = debug
        self.data_folder = "./data"
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

    def get_version(self):
        try:
            scope = "version"
            data = self.BNC.get_data(scope=scope)

            if self.debug:
                print(f"> {__file__}: Getting version from BotNetworkConnection")
                print(f"> {__file__}: Data: {data}")
            
            if data:
                print(f"> {__file__}: Successfully fetched version from BotNetworkConnection.")
                save_json(data, f"{self.data_folder}/{scope}.json")
                
        except Exception as e:
            print(f"> {__file__}: Failed to fetch version from BotNetworkConnection.")
            print(f"> {__file__}: Error: {e}")




    def get_all_available(self):

        # Attempting to get all available data from BotNetworkConnection using scope full.
        scope = "full"
        print(f"> DataFetching.py: Attempting to get all available data from BotNetworkConnection using scope '{scope}'.")
        data = self.BNC.get_data(scope=scope)
        if data:
            print(f"> DataFetching.py: Successfully fetched data from BotNetworkConnection.")
            save_json(data, "data/all_data.json")
        else:
            print(f"> DataFetching.py: Failed to fetch data from BotNetworkConnection.")