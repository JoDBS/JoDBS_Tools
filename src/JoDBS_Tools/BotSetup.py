import os
from datetime import datetime
from nextcord import Game
from .Database import BotNetworkConnection
from .DataFetching import DataFetching
from .utils import Get_ENV, Load_ENV, Get_ENV_Bool, load_json

class BotSetup:
    def __init__(self, bot, debug=False, env_path=None, NodeConnection=True):
        self.start_time = datetime.timestamp(datetime.now())
        self.debug = debug
        self.bot = bot

        # If no env_path is provided, look for .env in the current working directory
        if env_path is None:
            env_path = os.path.join(os.getcwd(), '.env')
            
        Load_ENV(env_path)  # Ensure environment variables are loaded before accessing them
        self.NodeConnection = Get_ENV_Bool("NODE_CONNECTION", default=NodeConnection)
        self.token = Get_ENV(key="TOKEN")
        self.cogs_directory = "./cogs"
        self.BNC = BotNetworkConnection() if self.NodeConnection else None 
        self.version = load_json("./data/version.json")["version"] or "N/A"

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
                # print("BotNetworkConnection is enabled.") Put this in status message in bot-database

                # Fetch data from BNC
                data_fetching = DataFetching(debug=self.debug)
                print("Fetching Data:")
                data_fetching.get_all_available_scopes()

            else:
                print("BotNetworkConnection is disabled.\n Some features might not work if cogs rely on BNC functions.")


            print("=====BOT=====")
            print("Loading Cogs:")
            self.add_cogs()
            print("=======================DONE=======================")
            self.run_bot()
        except Exception as e:
            # print(f"ERROR: bot.py | Bot Setup failed to run; BotNetworkConnection failed, or cogs failed to run. Check ENV variables.")
            if not self.debug:
                print(f"Bot Setup failed to run, enable debug for more info.")
            
            print(f"Bot Setup failed to run; BotNetworkConnection failed, or cogs failed to run. Check ENV variables.")
            print(f"Error: {e}")

    async def getBotStartupInfo(self):
        try:
            launch_time = str(datetime.now())[0:19]
            user = self.bot.user

            end_time = datetime.timestamp(datetime.now())
            elapsed_time = round(end_time - self.start_time, 2)
            launch_message = f"Launched with Version {self.version} at {launch_time}"+ "\n" + f"Logged in as: {user}" + "\n" +f"Elapsed time: {elapsed_time}s" + "\n" + "\n"

            return launch_message
        except:
            return "Failed to get Bot Startup Info."
    
    async def setBotStatus(self):
        try:
            activity_name = f"with v{self.version}"
            activity = Game(name=activity_name)
            await self.bot.change_presence(activity=activity)

            return True
        except:
            print("Failed to set Bot Status.")
            return False