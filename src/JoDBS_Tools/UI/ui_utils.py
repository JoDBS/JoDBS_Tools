


# Methods related to the Discord API
from nextcord import Member, Colour
async def get_highest_role_without_color(member: Member):
        roles_without_colour = [role for role in member.roles if role.colour != Colour.default()]
        roles_without_colour.sort(key=lambda role: role.position, reverse=True)
        return roles_without_colour[0] if roles_without_colour else None