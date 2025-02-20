from nextcord import Embed, ButtonStyle, Interaction
from nextcord.ui import View, Button
from ..utils import load_json
from typing import Dict, List, Optional, Union
from .ActionHandler import ActionHandler

class CustomUI:
    def __init__(self, bot, debug=False):
        self.bot = bot
        self.ui_elements = load_json(file_path="./data/ui_elements.json") or {}
        self.button_style_map = {
            1: ButtonStyle.primary,
            2: ButtonStyle.secondary,
            3: ButtonStyle.success,
            4: ButtonStyle.danger
        }
        self.action_handler = ActionHandler(bot)
        self.debug = debug
        
    def get_ui_element(self, guild_id: str, element_name: str) -> Optional[Dict]:
        """Retrieve a UI element configuration for a specific guild"""
        guild_elements = self.ui_elements.get(str(guild_id), {})
        return guild_elements.get(element_name)
    
    def create_embed(self, embed_data: Dict) -> Embed:
        """Create an Embed object from configuration data"""
        embed = Embed(
            title=embed_data.get('title'),
            description=embed_data.get('description'),
            color=embed_data.get('color', 0)
        )
        return embed
    
    def create_button(self, button_data: Dict) -> Button:
        """Create a Button object from configuration data"""
        return Button(
            custom_id=button_data.get('custom_id'),
            label=button_data.get('label'),
            style=self.button_style_map.get(button_data.get('style', 1))
        )
    
    async def create_view(self, components: List[Dict], actions: List[Dict]) -> View:
        """Create a View with components and their associated actions"""
        outer_self = self  # Store reference to outer class
        
        class DynamicView(View):
            def __init__(self, components: List[Dict], actions: List[Dict]):
                super().__init__(timeout=None)
                self.actions = {action['custom_id']: action for action in actions}
                
                for component in components:
                    if component['type'] == 'button':
                        button = outer_self.create_button(component)
                        button.callback = self.button_callback
                        self.add_item(button)
            
            async def button_callback(self, interaction: Interaction):
                try:
                    custom_id = interaction.data.get('custom_id')
                    action = self.actions.get(custom_id)
                    if action:
                        await outer_self.action_handler.handle_action(interaction, action)
                    else:
                        await interaction.response.send_message(
                            "No action found for this button.",
                            ephemeral=True
                        )
                except Exception as e:
                    print(f"Error in button callback: {e}")
                    await interaction.response.send_message(
                        "An error occurred while processing your request.",
                        ephemeral=True
                    )
        
        return DynamicView(components, actions)
    
    async def load_ui_element(self, guild_id: str, element_name: str) -> Union[Dict, None]:
        """Load a UI element with all its components"""
        element = self.get_ui_element(guild_id, element_name)
        if not element:
            return None
            
        result = {
            'id': f"{guild_id}_{element_name}",
            'name': element_name,
            'persistent': element.get('persistent', True),  # Default to True for persistence
            'embeds': [],
            'view': None,
            'config': element  # Store original config for reference
        }
        
        # Create embeds
        for embed_data in element.get('embeds', []):
            result['embeds'].append(self.create_embed(embed_data))
        
        # Create view with components and actions
        if 'components' in element:
            result['view'] = await self.create_view(
                element['components'],
                element.get('actions', [])
            )
            
        return result

    async def send_ui_element(self, channel, guild_id: str, element_name: str):
        """Send a UI element to a channel and register it if persistent"""
        if self.debug:
            print(f"[DEBUG] Attempting to send UI element: {element_name} for guild: {guild_id}")
        
        element = await self.load_ui_element(guild_id, element_name)
        if not element:
            if self.debug:
                print(f"[DEBUG] UI element not found: {element_name}")
            return None

        try:
            if self.debug:
                print(f"[DEBUG] Sending element with {len(element['embeds'])} embeds and view: {element['view'] is not None}")
            
            message = await channel.send(
                embeds=element['embeds'],
                view=element['view']
            )

            if element.get('persistent', True):
                if self.debug:
                    print(f"[DEBUG] Registering message {message.id} for persistence")
                await self.action_handler.register_message(
                    message=message,
                    ui_element_id=element['id'],
                    element_data={
                        'name': element['name'],
                        'config': element['config']
                    }
                )

            return message
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error sending UI element: {str(e)}")
            return None

    async def reload_persistent_messages(self):
        """Reload all persistent messages"""
        if self.debug:
            print("\n=== Starting Persistent Messages Reload ===")
            print(f"Found {len(self.action_handler.persistent_messages)} messages to reload")

        for message_id, data in self.action_handler.persistent_messages.items():
            try:
                if self.debug:
                    print(f"\n[DEBUG] Processing message {message_id}:")
                    print(f"  Channel ID: {data['channel_id']}")
                    print(f"  Element Name: {data.get('element_name', 'unknown')}")

                channel = self.bot.get_channel(int(data['channel_id']))
                if not channel and self.debug:
                    print(f"  [ERROR] Channel not found: {data['channel_id']}")
                    continue

                if self.debug:
                    print("  Channel found, fetching message...")

                message = await channel.fetch_message(int(message_id))
                guild_id, element_name = data['ui_element_id'].split('_', 1)
                
                if self.debug:
                    print(f"  Loading UI element: {element_name}")

                element = await self.load_ui_element(guild_id, element_name)
                if element:
                    if self.debug:
                        print("  Updating message with new content...")
                    await message.edit(embeds=element['embeds'], view=element['view'])
                    if self.debug:
                        print("  Message updated successfully")
                else:
                    print(f"  [ERROR] Failed to load UI element: {element_name}")

            except Exception as e:
                if self.debug:
                    print(f"  [ERROR] Failed to reload message {message_id}:")
                    print(f"  Error details: {str(e)}")
                else:
                    print(f"Failed to reload message {message_id}: {e}")

        if self.debug:
            print("\n=== Persistent Messages Reload Complete ===\n")