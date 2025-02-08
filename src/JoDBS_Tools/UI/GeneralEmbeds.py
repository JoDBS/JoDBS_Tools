from ..utils import load_json, Get_Datetime_UTC, get_highest_role_without_color
from nextcord import Embed, Colour, File
from io import BytesIO
import json, zipfile

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
    
    