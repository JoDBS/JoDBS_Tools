import os
from datetime import datetime
from nextcord import Game
from .Database import BotNetworkConnection
from .DataFetching import DataFetching
from .utils import Get_ENV, Load_ENV, Get_ENV_Bool

class BotSetup:
    def __init__(self, bot, env_path=None, NodeConnection=True):
        self.start_time = datetime.timestamp(datetime.now())
        self.bot = bot

        # If no env_path is provided, look for .env in the current working directory
        if env_path is None:
            env_path = os.path.join(os.getcwd(), '.env')
            
        Load_ENV(env_path)  # Ensure environment variables are loaded before accessing them
        self.NodeConnection = Get_ENV_Bool("NODE_CONNECTION", default=NodeConnection)
        self.token = Get_ENV(key="TOKEN")
        self.cogs_directory = "./cogs"
        self.BNC = BotNetworkConnection() if self.NodeConnection else None 

    def run_bot(self):
        try:
            if not self.token or self.token == "NO_TOKEN_ADDED":
                print("NO_TOKEN_ADDED. Please add a valid token in environment secrets")
                return
            self.bot.run(self.token)
        except Exception as e:
            print("ERROR: bot.py | bot.run() failed to run the bot. Possible wrong token or invalid token?!")
            print(e)
            raise Exception(e)

    def add_cogs(self):
        try:
            if not os.path.exists(self.cogs_directory):
                print(f"ERROR: bot.py | Cog directory '{self.cogs_directory}' does not exist.")
                return

            for filename in os.listdir(self.cogs_directory):
                if filename.endswith(".py"):
                    try:
                        self.bot.load_extension(f"cogs.{filename[:-3]}")
                        print(">", filename)
                    except Exception as e:
                        print(f"ERROR: bot.py | Failed to load cog '{filename}'. Error: {e}")
                        raise Exception(e)
        except Exception as e:
            print(f"ERROR: bot.py | Cog Support failed to load. Possible /cogs does not exist?! or Duplicate?! Error: \n{e}")
            raise Exception(e)

    def setup_bot(self):
        try:
            print("==================================================")
            if self.NodeConnection:
                # Check if bot can connect to BotNetwork
                status = self.BNC.check_status()
                if status is None:
                    print("Bot Setup failed to run;\n BotNetworkConnection failed. Check ENV variables.")
                    return
                print(status)

                # Fetch data from BNC
                data_fetching = DataFetching()
                


                # # Check if bot can get roles.json from BotNetwork
                # print("Retrieving Roles from BotNetwork:")
                # roles_fetch = self.BNC.fetch_and_save_roles()
                # if roles_fetch:
                #     print("Roles fetched successfully.")
                # else:
                #     print("Roles fetch failed. (some cogs might error out if they rely on roles.json)")
                #     print("Update roles.json in BotNetwork.")
            else:
                print("BotNetworkConnection is disabled.\n Some features might not work if cogs rely on BNC functions.")
            print("=====BOT=====")
            print("Loading Cogs:")
            self.add_cogs()
            print("=======================DONE=======================")
            self.run_bot()
        except Exception as e:
            print(f"ERROR: bot.py | Bot Setup failed to run; BotNetworkConnection failed, or cogs failed to run. Check ENV variables.")
    
    async def getBotStartupInfo(self):
        try:
            # Initiate a BotNetworkConnection to get version.
            if self.NodeConnection:
                # BNC = BotNetworkConnection(base_url=Get_ENV("BNC_BASE_URL"), api_key=Get_ENV("BNC_API_KEY"))
                version = self.BNC.get_data(scope="version")
            else:
                version = "N/A"

            launch_time = str(datetime.now())[0:19]
            user = self.bot.user

            end_time = datetime.timestamp(datetime.now())
            elapsed_time = round(end_time - self.start_time, 2)
            launch_message = f"Launched with Version {version} at {launch_time}"+ "\n" + f"Logged in as: {user}" + "\n" +f"Elapsed time: {elapsed_time}s" + "\n" + "\n"

            return launch_message
        except:
            return "Failed to get Bot Startup Info."
    
    async def setBotStatus(self):
        try:
            if self.NodeConnection:
                # Initiate a BotNetworkConnection to get version.
                # BNC = BotNetworkConnection(base_url=Get_ENV("BNC_BASE_URL"), api_key=Get_ENV("BNC_API_KEY"))
                version = self.BNC.get_data(scope="version")
                if version is None:
                    return False
                activity_name = f"with v{version}"
                activity = Game(name=activity_name)
                await self.bot.change_presence(activity=activity)
                return True
            else:
                print("BotNetworkConnection is disabled.\n Bot Status will not be set.")
                return False
        except:
            print("Failed to set Bot Status.")
            return False