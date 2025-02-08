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
                file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ui_data.json')
            
            with open(file_path, 'r') as f:
                self.ui_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading UI data: {e}")
            return False

    def get_ui_data(self, guild_id=None):
        """Get UI data for a specific guild or all UI data if no guild_id is provided."""
        if guild_id:
            return self.ui_data.get(str(guild_id))
        return self.ui_data
