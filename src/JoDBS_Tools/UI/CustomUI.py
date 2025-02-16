from nextcord import Embed, ButtonStyle, Interaction
from nextcord.ui import View, Button
from ..utils import load_json
from typing import Dict, List, Optional, Union

class CustomUI:
    def __init__(self, bot):
        self.bot = bot
        self.ui_elements = load_json(file_path="./data/ui_elements.json") or {}
        self.button_style_map = {
            1: ButtonStyle.primary,
            2: ButtonStyle.secondary,
            3: ButtonStyle.success,
            4: ButtonStyle.danger
        }
        
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
                        button = outer_self.create_button(component)  # Use outer class method
                        self.add_item(button)
            
            async def button_callback(self, interaction: Interaction):
                action = self.actions.get(interaction.custom_id)
                if action and action['type'] == 'add_role':
                    role = interaction.guild.get_role(int(action['role_id']))
                    if role:
                        await interaction.user.add_roles(role)
                        await interaction.response.send_message(
                            f"Role {role.name} added!", ephemeral=True
                        )
        
        return DynamicView(components, actions)
    
    async def load_ui_element(self, guild_id: str, element_name: str) -> Union[Dict, None]:
        """Load a UI element with all its components"""
        element = self.get_ui_element(guild_id, element_name)
        if not element:
            return None
            
        result = {
            'id': f"{guild_id}_{element_name}",  # Generate ID from guild_id and element_name
            'persistent': element.get('persistent', False),
            'embeds': [],
            'view': None
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