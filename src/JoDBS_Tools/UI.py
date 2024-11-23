import nextcord
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
        self.ui_elements = load_json("./data/ui_elements.json")
        self.guild_ui = self.ui_elements.get(self.guild_id, {})
        self.register_interactions()

    def register_interactions(self):
        @self.bot.event
        async def on_interaction(interaction: Interaction):
            custom_id = interaction.data.get('custom_id')
            if not custom_id:
                return  # Ignore interactions without custom_id
            action = self.get_action_by_custom_id(custom_id)
            if action:
                # Respond only if not already responded in callback
                if not interaction.response.is_done():
                    await self.execute_action(interaction, action)

    async def return_embeds(self, name: str):
        item = self.guild_ui.get(name, {})
        embeds_data = item.get("embeds", [])
        if not embeds_data:
            return None
        embeds = [Embed.from_dict(embed_data) for embed_data in embeds_data]
        return embeds

    async def return_components(self, name: str) -> View:
        item = self.guild_ui.get(name, {})
        components_data = item.get("components", [])
        if not components_data:
            return None

        view = View(timeout=None)
        for component in components_data:
            if component["type"] == "button":
                for item_data in component["items"]:
                    custom_id = item_data.get("custom_id")
                    button = Button(
                        label=item_data["label"],
                        style=item_data["style"],
                        custom_id=custom_id
                    )

                    # Check if there's a modal associated with this button
                    modal_name = item_data.get("modal_id")
                    if modal_name:
                        async def button_callback(interaction: Interaction, modal_name=modal_name):
                            modals = await self.return_modals(modal_name)
                            if modals:
                                await interaction.response.send_modal(modals[0])
                            else:
                                await interaction.response.send_message("No modal found.", ephemeral=True)

                        button.callback = button_callback
                    # Else, the action will be handled in on_interaction

                    view.add_item(button)

            elif component["type"] == "select":
                options = [SelectOption(**opt) for opt in component["items"]]
                select = Select(
                    placeholder=component.get("placeholder", "Choose an option"),
                    options=options,
                    custom_id=component.get("custom_id")
                )
                view.add_item(select)
        return view

    def get_action_by_custom_id(self, custom_id):
        for item in self.guild_ui.values():
            actions = item.get("actions", [])
            for action in actions:
                if action.get("custom_id") == custom_id:
                    return action
        return None

    async def return_modals(self, name: str):
        item = self.guild_ui.get(name, {})
        modals_data = item.get("modals", [])
        if not modals_data:
            return None
        modals = []
        for modal_data in modals_data:
            class CustomModal(nextcord.ui.Modal):
                def __init__(self):
                    super().__init__(title=modal_data["title"], timeout=modal_data.get("timeout"))
                    for item in modal_data["items"]:
                        style_input = item.get("text_input_style", nextcord.TextInputStyle.short)
                        if isinstance(style_input, int):
                            style_input = nextcord.TextInputStyle(style_input)
                        self.add_item(
                            nextcord.ui.TextInput(
                                label=item["label"],
                                placeholder=item.get("placeholder"),
                                required=item.get("required", True),
                                min_length=item.get("min_length"),
                                max_length=item.get("max_length"),
                                default_value=item.get("default_value"),
                                style=style_input
                            )
                        )

                async def callback(self, interaction: Interaction):
                    # Handle modal submission
                    responses = {item.label: item.value for item in self.children}
                    # Process the responses as needed
                    await interaction.response.send_message("Thank you for your submission!", ephemeral=True)

            modals.append(CustomModal())
        return modals

    async def execute_action(self, interaction: Interaction, action: dict):
        """Refactor to use functions outside of this function to simplify visibility"""
        if action["type"] == "send_message":
            await interaction.response.send_message(action["content"], ephemeral=True)
        elif action["type"] == "assign_role":
            role = interaction.guild.get_role(action["role_id"])
            if role:
                try:
                    # Check if user already has role, then remove it
                    if role in interaction.user.roles:
                        await interaction.user.remove_roles(role)
                        await interaction.response.send_message(
                            f"You have been removed from the role {role.name}", ephemeral=True
                        )
                    else:
                        await interaction.user.add_roles(role)
                        await interaction.response.send_message(
                            f"You have been assigned the role {role.name}", ephemeral=True
                        )
                except nextcord.Forbidden:
                    await interaction.response.send_message(
                        "Sorry, I don't have permission to assign that role.", ephemeral=True
                    )
            else:
                await interaction.response.send_message("Role not found.", ephemeral=True)
        elif action["type"] == "0":
            pass







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