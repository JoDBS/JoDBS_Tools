from nextcord import Interaction, Member, Embed, Colour, ButtonStyle
from nextcord.ui import View, Button, button
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
            self.stop()

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: Button, interaction: Interaction):
        if interaction.user == self.ctx.user:
            self.value = False
            self.stop()

class GeneralEmbeds():
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
        server_region = server.region
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
        embed.add_field(name="Region", value=server_region)
        embed.add_field(name="Server Created", value=server_created.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Member Count", value=f"{server_member_count} Members")
        embed.add_field(name="Online Members", value=f"{server_online_members} Members")
        embed.add_field(name="Roles", value=f"{len(server.roles)} Roles")
        embed.add_field(name="Channels", value=f"{len(server.channels)} Channels")
        embed.add_field(name="Categories", value=f"{len(server.categories)} Categories")
        embed.add_field(name="BNC Roles.json", value=self.roles.get(str(server_id), "No Roles.json Data"))
        
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
        embed.add_field(name="Verified", value=is_verified, inline=False)
        embed.add_field(name="Staff Member", value=is_staff_member, inline=False)
        embed.add_field(name="Highest Role", value=member_highest_role.mention if member_highest_role else "None", inline=False)

        return embed











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