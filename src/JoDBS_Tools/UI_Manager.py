import json
import os

class UIManager:
    def __init__(self, bot):
        self.bot = bot
        self.ui_data = {}

    async def load_ui_data(self, file_path=None):
        """Load UI data from a JSON file."""
        try:
            if file_path is None:
                # Get the directory where bot.py is located
                bot_root = os.path.dirname(os.path.abspath(self.bot.file_path))
                file_path = os.path.join(bot_root, 'data', 'ui_data.json')
            
            print(f"Loading UI data from: {file_path}")  # Debug print
            
            if not os.path.exists(file_path):
                print(f"UI data file not found at: {file_path}")
                return False
                
            with open(file_path, 'r') as f:
                self.ui_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading UI data: {e}")
            return False

    # ...existing code...
