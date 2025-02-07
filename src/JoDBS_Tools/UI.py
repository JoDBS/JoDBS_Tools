import nextcord
from nextcord import Interaction, Member, Embed, Colour, ButtonStyle, SelectOption, TextInputStyle, File, ui
from nextcord.ui import View, Button, button, Select, TextInput, Modal
from .utils import Get_Datetime_UTC, save_json, load_json, get_highest_role_without_color
from io import StringIO, BytesIO
import json
import zipfile
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import logging

class ConfirmView(View):
    def __init__(self, ctx: Interaction, amount: int):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.amount = amount
        self.value = None

    @button(label="Confirm", style=ButtonStyle.green)
    async def confirm(self, button: Button, interaction: Interaction):
        if interaction.user == self.ctx.user:
            self.value = True
            button.disabled = True
            await interaction.response.edit_message(content=f"Confirmed {self.amount}!", view=self)
            self.stop()

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: Button, interaction: Interaction):
        if interaction.user == self.ctx.user:
            self.value = False
            button.disabled = True
            await interaction.response.edit_message(content=f"Cancelled {self.amount}!", view=self)
            self.stop()

class GeneralEmbeds:
    def __init__(self, bot):
        self.bot = bot
        self.default_colour = Colour.darker_grey()
        self.roles = load_json(file_path="./data/roles.json") or {}


    async def ping_embed(self, ctx):
        embed = Embed(
            title="🏓",
            color=self.default_colour,
            description=f"Latency: {round(self.bot.latency * 1000)}ms"
        )
        embed.set_footer(text=f"Requested by {ctx.user}")
        embed.timestamp = Get_Datetime_UTC()
        return embed
    
    async def server_info_embed(self, ctx):
        """Create embed with containing server information, index[0] = embed, index [1] includes roles.json for server"""
        server = ctx.guild
        server_id = server.id
        server_name = server.name
        server_owner = server.owner
        server_created = server.created_at
        server_member_count = server.member_count
        server_online_members = len([member for member in server.members if member.status != "offline"])
        server_icon = server.icon
        server_roles = server.roles

        embed = Embed(
            title=f"Server Information for {server_name} ({server_id})",
            color=self.default_colour
        )
        embed.set_thumbnail(url=server_icon)
        embed.set_footer(text=f"Requested by {ctx.user}")
        embed.timestamp = Get_Datetime_UTC()
        embed.add_field(name="Owner", value=server_owner.mention)
        embed.add_field(name="Server Created", value=server_created.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Channels", value=f"{len(server.channels)} Channels")
        embed.add_field(name="Categories", value=f"{len(server.categories)} Categories")
        embed.add_field(name="Member Count", value=f"{server_member_count} Members")
        embed.add_field(name="Online Members", value=f"{server_online_members} Members")
        embed.add_field(name="Roles", value=f"{server_roles} Roles", inline=False)
        embed.add_field(name="BNC Roles.json", value=self.roles.get(str(server_id), "No Roles.json Data"), inline=False)
        
        roles_data = {
            role.name: role.id for role in server_roles
        }
        
        bnc_roles_data = self.roles.get(str(server_id), {})
        
        # Create zip file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add current server roles
            roles_json = json.dumps(roles_data, indent=4)
            zip_file.writestr(f"{server_name}_server_roles.json", roles_json)
            
            # Add BNC roles data
            bnc_roles_json = json.dumps(bnc_roles_data, indent=4)
            zip_file.writestr(f"{server_name}_bnc_roles.json", bnc_roles_json)
        
        # Reset buffer position
        zip_buffer.seek(0)
        
        # Create File object with zip
        server_roles_file = File(
            fp=zip_buffer, 
            filename=f"{server_name}_data.zip",
            description="Exported roles.json for Server (ZIP)"
        )
        
        return [embed, server_roles_file]
    
    async def user_info_embed(self, ctx, member):
        # add docstring
        server_id = str(ctx.guild.id)
        member_role_ids = [role.id for role in member.roles]
        server_roles = self.roles.get(server_id, {})
        verified_role_id = server_roles.get("Verified")
        staff_member_role_id = server_roles.get("Staff_Member")

        member_name = member.name
        member_id = member.id
        member_account_created = ctx.guild.get_member(member_id).created_at
        member_account_joined = ctx.guild.get_member(member_id).joined_at
        member_status = "🟢" if not member.status == "offline" else "🔴"
        is_verified = "🟢" if verified_role_id in member_role_ids else "🔴"
        is_staff_member = "🟢" if staff_member_role_id in member_role_ids else "🔴"
        member_highest_role = await get_highest_role_without_color(member)


        embed = Embed(
            title=f"Member Information for {member_name} ({member_id})",
            color=self.default_colour
            # description=f""
        )
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(text=f"Requested by {ctx.user}")
        embed.timestamp = Get_Datetime_UTC()
        embed.add_field(name="Account Created", value=member_account_created.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Member Joined", value=member_account_joined.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Online Status", value=member_status)
        embed.add_field(name="Verified", value=is_verified, inline=False)
        embed.add_field(name="Staff Member", value=is_staff_member, inline=False)
        embed.add_field(name="Highest Role", value=member_highest_role.mention if member_highest_role else "None", inline=False)

        return embed
    
    
class ActionHandler:
    def __init__(self, bot):
        self.bot = bot
        self.action_callbacks: Dict[str, Callable] = {}

    def get_namespaced_id(self, guild_id: str, custom_id: str) -> str:
        """Create a namespaced custom_id that includes the guild_id"""
        return f"{guild_id}:{custom_id}"

    async def handle_interaction(self, interaction: Interaction):
        """Handle incoming interactions and route to appropriate callbacks"""
        custom_id = interaction.data.get('custom_id')
        guild_id = str(interaction.guild_id)
        namespaced_id = self.get_namespaced_id(guild_id, custom_id)
        
        if namespaced_id in self.action_callbacks:
            await self.action_callbacks[namespaced_id](interaction)

    async def default_message_response(self, interaction: Interaction, message: str):
        """Default handler for message responses"""
        try:
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            print(f"Error sending message response: {e}")

    async def default_role_action(self, interaction: Interaction, role_id: int, remove: bool = False):
        """Default handler for role assignments"""
        try:
            member = interaction.user
            role = interaction.guild.get_role(role_id)
            if role:
                if remove:
                    await member.remove_roles(role)
                else:
                    await member.add_roles(role)
                await interaction.response.send_message(
                    f"Role {'removed' if remove else 'added'} successfully!", 
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error handling role action: {e}")

    def register_action(self, guild_id: str, custom_id: str, callback: Callable):
        """Register a custom action callback with guild namespace"""
        namespaced_id = self.get_namespaced_id(guild_id, custom_id)
        self.action_callbacks[namespaced_id] = callback

class UIElement:
    def __init__(self, element_id: str, persistent: bool = False):
        self.element_id = element_id
        self.persistent = persistent
        self.components = []
        self.embeds = []

class UIManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.elements: Dict[str, UIElement] = {}
        self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            return
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            for element_id, data in config.items():
                element = UIElement(
                    element_id=element_id,
                    persistent=data.get('persistent', False)
                )
                self.elements[element_id] = element

class ComponentBuilder:
    @staticmethod
    def create_button(data: dict) -> Button:  # Changed from ui.Button to Button since we import it directly
        return Button(
            custom_id=data['custom_id'],
            label=data.get('label', ''),
            style=data.get('style', 1)
        )

class ActionRegistry:
    def __init__(self):
        self.actions: Dict[str, callable] = {}

    def register(self, custom_id: str, callback: callable):
        self.actions[custom_id] = callback

    async def execute(self, custom_id: str, interaction):
        if custom_id in self.actions:
            await self.actions[custom_id](interaction)

class UIView(ui.View):
    def __init__(self, element: UIElement, action_registry: ActionRegistry):
        super().__init__(timeout=None if element.persistent else 180)
        self.element = element
        self.action_registry = action_registry

    async def interaction_check(self, interaction) -> bool:
        custom_id = interaction.data.get('custom_id')
        if custom_id:
            await self.action_registry.execute(custom_id, interaction)
        return True

class UIFetcher:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = str(guild_id)
        self.action_handler = ActionHandler(bot)
        self.persistent_views = {}
        self.logger = logging.getLogger('JoDBS_Tools.UI')
        self.load_ui_elements()

    def load_ui_elements(self):
        try:
            self.ui_elements = load_json("./data/ui_elements.json") or {}
            self.guild_ui = self.ui_elements.get(self.guild_id, {})
            # Load persistent views handled separately to avoid async issues
        except Exception as e:
            self.logger.error(f"Error loading UI elements: {e}", exc_info=True)
            self.ui_elements = {}
            self.guild_ui = {}

    async def load_persistent_views(self):
        """Asynchronously load all persistent views"""
        try:
            for name, data in self.guild_ui.items():
                if data.get("persistent", False):
                    await self.load_persistent_view(name, data)
        except Exception as e:
            self.logger.error(f"Error loading persistent views: {e}", exc_info=True)

    async def load_persistent_view(self, name: str, data: dict):
        """Asynchronously load a single persistent view"""
        try:
            view = await self.return_components(name)
            if view:
                view.message_id = data.get("id")
                self.bot.add_view(view)
                self.persistent_views[data["id"]] = view
        except Exception as e:
            self.logger.error(f"Error loading persistent view {name}: {e}", exc_info=True)

    def get_item_data(self, name: str) -> dict:
        """Get all data for a specific UI item"""
        return self.guild_ui.get(name, {})

    def get_embeds_data(self, name: str) -> list:
        """Get embed data for conversion"""
        item = self.guild_ui.get(name, {})
        return item.get("embeds", [])

    def get_components_data(self, name: str) -> list:
        """Get component data for conversion"""
        item = self.guild_ui.get(name, {})
        return item.get("components", [])

    def get_modal_data(self, name: str) -> list:
        """Get modal data for conversion"""
        item = self.guild_ui.get(name, {})
        return item.get("modals", [])

    def get_action_data(self, custom_id: str) -> dict:
        """Get action data by custom_id"""
        for item in self.guild_ui.values():
            actions = item.get("actions", [])
            for action in actions:
                if action.get("custom_id") == custom_id:
                    return action
        return None
    
    async def return_embeds(self, name: str) -> list:
        """Return a list of embeds with a matching name"""
        try:
            embeds_data = self.get_embeds_data(name)
            embeds = []
            for data in embeds_data:
                embed = Embed.from_dict(data)
                embeds.append(embed)
            return embeds
        except Exception as e:
            print(f"Error creating embeds: {e}")
            return []

    async def register_component_actions(self, name: str):
        """Register actions for components"""
        item = self.get_item_data(name)
        actions = item.get("actions", [])
        
        for action in actions:
            custom_id = action.get("custom_id")
            action_type = action.get("type")
            
            if action_type == "message":
                message = action.get("message", "Button clicked!")
                self.action_handler.register_action(
                    self.guild_id,
                    custom_id,
                    lambda i, m=message: self.action_handler.default_message_response(i, m)
                )
            
            elif action_type == "add_role": 
                role_id = action.get("role_id")
                if role_id:
                    self.action_handler.register_action(
                        self.guild_id,
                        custom_id,
                        lambda i, r=role_id: self.action_handler.default_role_action(i, r)
                    )
            
            elif action_type == "remove_role":
                role_id = action.get("role_id")
                if role_id:
                    self.action_handler.register_action(
                        self.guild_id,
                        custom_id,
                        lambda i, r=role_id: self.action_handler.default_role_action(i, r, remove=True)
                    )

    async def return_components(self, name: str) -> Optional[View]:
        """Return a View containing components with a matching name"""
        try:
            components_data = self.get_components_data(name)
            if not components_data:
                return None
            
            view = View(timeout=None)
            
            # Register actions before creating buttons
            await self.register_component_actions(name)
            
            for component in components_data:
                if component["type"] == "button":
                    custom_id = component.get("custom_id")
                    button = Button(
                        style=ButtonStyle(component.get("style", 1)),
                        label=component.get("label", "Button"),
                        custom_id=custom_id,
                        disabled=component.get("disabled", False)
                    )
                    # Add interaction callback
                    button.callback = self.action_handler.handle_interaction
                    view.add_item(button)
            return view
        except Exception as e:
            print(f"Error creating components: {e}")
            return None