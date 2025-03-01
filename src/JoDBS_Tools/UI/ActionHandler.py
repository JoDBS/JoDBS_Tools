from typing import Dict, Any, Optional
from nextcord import Interaction, Member, Message
import json

class ActionHandler:
    def __init__(self, bot):
        self.bot = bot
        self.persistent_messages: Dict[str, Dict[str, Any]] = {}
        self.debug = False  # Will be set by CustomUI
        self._load_persistent_messages()

    def set_debug(self, debug: bool):
        """Set debug mode"""
        self.debug = debug

    def _load_persistent_messages(self):
        try:
            with open('./data/persistent_messages.json', 'r') as f:
                self.persistent_messages = json.load(f)
        except FileNotFoundError:
            self.persistent_messages = {}

    def _save_persistent_messages(self):
        with open('./data/persistent_messages.json', 'w') as f:
            json.dump(self.persistent_messages, f, indent=4)

    async def handle_action(self, interaction: Interaction, action: Dict[str, Any]):
        """Handle different types of actions"""
        if self.debug:
            print(f"\n[DEBUG] Handling action:")
            print(f"  Type: {action.get('type')}")
            print(f"  Custom ID: {action.get('custom_id')}")
        
        action_type = action.get('type')
        
        if action_type == 'add_role':
            await self._handle_add_role(interaction, action)
        elif action_type == 'remove_role':
            await self._handle_remove_role(interaction, action)
        elif action_type == 'message':
            await self._handle_message(interaction, action)
        elif action_type == 'modal':
            await self._handle_modal(interaction, action)

    async def _handle_add_role(self, interaction: Interaction, action: Dict[str, Any]):
        if self.debug:
            print(f"[DEBUG] Adding role {action['role_id']} to user {interaction.user.id}")
        
        role = interaction.guild.get_role(int(action['role_id']))
        if role:
            await interaction.user.add_roles(role)
            response = action.get('response', f"Role {role.name} added!")
            await interaction.response.send_message(response, ephemeral=True)

    async def _handle_remove_role(self, interaction: Interaction, action: Dict[str, Any]):
        role = interaction.guild.get_role(int(action['role_id']))
        if role:
            await interaction.user.remove_roles(role)
            response = action.get('response', f"Role {role.name} removed!")
            await interaction.response.send_message(response, ephemeral=True)

    async def _handle_message(self, interaction: Interaction, action: Dict[str, Any]):
        message = action.get('message', 'Action completed!')
        await interaction.response.send_message(message, ephemeral=True)

    async def _handle_modal(self, interaction: Interaction, action: Dict[str, Any]):
        # Future implementation for modal handling
        pass

    async def register_message(self, message: Message, ui_element_id: str, element_data: Dict):
        """Register a message for persistence"""
        if self.debug:
            print(f"\n[DEBUG] Registering message for persistence:")
            print(f"  Message ID: {message.id}")
            print(f"  Element: {element_data.get('name')}")
            print(f"  Channel: {message.channel.id}")

        self.persistent_messages[str(message.id)] = {
            'channel_id': str(message.channel.id),
            'guild_id': str(message.guild.id),
            'ui_element_id': ui_element_id,
            'element_name': element_data.get('name'),
            'timestamp': str(message.created_at),
            'author_id': str(message.author.id)
        }
        self._save_persistent_messages()
        print(f"Registered persistent message: {message.id} for element: {ui_element_id}")

        if self.debug:
            print("  Message registered successfully")
