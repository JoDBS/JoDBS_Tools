import nextcord
from .UI_Manager import UIManager

class UIHandler:
    def __init__(self, bot):
        self.bot = bot
        self.ui_manager = UIManager(bot)

    async def create_ui_message(self, interaction, panel_name, guild_id):
        """Creates and sends a UI message based on the configuration."""
        guild_data = self.ui_manager.get_ui_data(guild_id)
        if not guild_data or panel_name not in guild_data:
            return False

        panel_data = guild_data[panel_name]
        
        # Create embeds
        embeds = []
        for embed_data in panel_data.get('embeds', []):
            embed = nextcord.Embed(
                title=embed_data.get('title'),
                description=embed_data.get('description'),
                color=embed_data.get('color', 0)
            )
            for field in embed_data.get('fields', []):
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
            embeds.append(embed)

        # Create components
        components = []
        if panel_data.get('components'):
            action_row = nextcord.ui.ActionRow()
            for comp in panel_data['components']:
                if comp['type'] == 'button':
                    button = nextcord.ui.Button(
                        custom_id=comp['custom_id'],
                        label=comp['label'],
                        style=nextcord.ButtonStyle(comp['style'])
                    )
                    action_row.add_item(button)
            components.append(action_row)

        await interaction.response.send_message(embeds=embeds, components=components)
        return True

    async def handle_component(self, interaction):
        """Handles component interactions based on UI data configuration."""
        guild_data = self.ui_manager.get_ui_data(interaction.guild_id)
        if not guild_data:
            return False

        for panel in guild_data.values():
            for action in panel.get('actions', []):
                if action['custom_id'] == interaction.custom_id:
                    if action['type'] == 'message':
                        await interaction.response.send_message(action['message'], ephemeral=True)
                    elif action['type'] == 'add_role':
                        role = interaction.guild.get_role(int(action['role_id']))
                        if role:
                            await interaction.user.add_roles(role)
                            await interaction.response.send_message(f"Role {role.name} added!", ephemeral=True)
                    return True
        return False
