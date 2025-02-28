import os


class DataFetching:
    def __init__(self):
        self.__create_data_folder()

    def __create_data_folder(self):
        try:
            os.makedirs("data")
            print("> DataFetching.py: Created data folder.")
        except FileExistsError:
            return
        else:
            print("> DataFetching.py: Problem whilst creating data folder.")


    def get_all_available():
        pass