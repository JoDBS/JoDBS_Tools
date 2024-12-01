import nextcord
from nextcord import Interaction, Member, Embed, Colour, ButtonStyle, SelectOption, TextInputStyle, File
from nextcord.ui import View, Button, button, Select, TextInput, Modal
from .utils import Get_Datetime_UTC, save_json, load_json, get_highest_role_without_color
from io import StringIO

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
        roles_json = StringIO(str(roles_data))
        server_roles_file = File(fp=roles_json, filename=f"{server_name}_roles.json", description="Exported roles.json for Server")
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
    
    
class UIFetcher:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = str(guild_id)
        try:
            self.ui_elements = load_json("./data/ui_elements.json") or {}
        except Exception as e:
            print(f"Error loading UI elements: {e}")
            self.ui_elements = {}
        self.guild_ui = self.ui_elements.get(self.guild_id, {})

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

    async def return_components(self, name: str) -> View:
        """Return a View containing components with a matching name"""
        try:
            components_data = self.get_components_data(name)
            if not components_data:
                return None
            
            view = View(timeout=None)
            for component in components_data:
                if component["type"] == "button":
                    button = Button(
                        style=ButtonStyle(component.get("style", 1)),
                        label=component.get("label", "Button"),
                        custom_id=component.get("custom_id"),
                        disabled=component.get("disabled", False)
                    )
                    view.add_item(button)
                # Can be extended for other component types like Select menus
            return view
        except Exception as e:
            print(f"Error creating components: {e}")
            return None