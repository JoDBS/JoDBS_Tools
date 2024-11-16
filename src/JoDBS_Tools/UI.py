from nextcord import Interaction, Member, Embed, Colour, ButtonStyle, SelectOption
from nextcord.ui import View, Button, button, Select
from .utils import Get_Datetime_UTC, load_json, get_highest_role_without_color

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
        server = ctx.guild
        server_id = server.id
        server_name = server.name
        server_owner = server.owner
        server_created = server.created_at
        server_member_count = server.member_count
        server_online_members = len([member for member in server.members if member.status != "offline"])
        server_icon = server.icon

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
        embed.add_field(name="Roles", value=f"{server.roles} Roles", inline=False)
        embed.add_field(name="BNC Roles.json", value=self.roles.get(str(server_id), "No Roles.json Data"), inline=False)
        
        return embed
    
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
            color=Colour.darker_grey()
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


class LoadEmbed:
    def __init__(self, guild_id):
        self.guild_id = str(guild_id)
        self.embeds = load_json(file_path="./data/embeds.json") or {}
        # print("Loaded embeds.json", self.embeds)

    async def return_embed(self, name: str):
        # Attempt to get the embed from locally stored embeds.json
        try:
            embed_data = self.embeds.get(self.guild_id, {}).get(name)
            if not embed_data:
                return None, None

            # Create the Embed object
            embed_dict = {k: v for k, v in embed_data.items() if k != "view"}
            embed = Embed.from_dict(embed_dict)

            # Check for associated view
            view_data = embed_data.get("view")
            if view_data:
                view = await self.create_view(view_data)
            else:
                view = None

            return embed, view
        except Exception as e:
            print(f"Error: {e}")
            return None, None

    async def create_view(self, view_data: dict):
        view = View(timeout=None)  # Set timeout to None for persistent components
        
        # Handle buttons
        buttons = view_data.get("buttons", [])
        for button_data in buttons:
            button = Button(
                label=button_data.get("label", "Button"),
                style=getattr(ButtonStyle, button_data.get("style", "secondary")),
                custom_id=button_data.get("custom_id"),  # Ensure custom_id is set
                url=button_data.get("url"),
                emoji=button_data.get("emoji"),
                disabled=button_data.get("disabled", False)
            )
            view.add_item(button)
        
        # Handle select menus
        selects = view_data.get("selects", [])
        for select_data in selects:
            options = [
                SelectOption(
                    label=option.get("label"),
                    value=option.get("value"),
                    description=option.get("description"),
                    emoji=option.get("emoji")
                )
                for option in select_data.get("options", [])
            ]
            select_menu = Select(
                placeholder=select_data.get("placeholder", "Choose an option"),
                min_values=select_data.get("min_values", 1),
                max_values=select_data.get("max_values", 1),
                options=options,
                custom_id=select_data.get("custom_id")  # Ensure custom_id is set
            )
            view.add_item(select_menu)
        
        return view











"""
Basic Embed Structure:
async def name_embed(self, ctx):
        embed = Embed(
            title="Name",
            color=self.default_colour,
            description=f"Name"
        )
        embed.set_footer(text=f"Requested by {ctx.user}")
        embed.timestamp = Get_Datetime_UTC()
        return embed
"""