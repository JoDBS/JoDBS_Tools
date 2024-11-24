import nextcord
from nextcord import Interaction, Member, Embed, Colour, ButtonStyle, SelectOption, TextInputStyle
from nextcord.ui import View, Button, button, Select, TextInput, Modal
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


class PersistentView(View):
    def __init__(self, handler_class, modal_id=None, custom_id=None):
        super().__init__(timeout=None)
        self.handler_class = handler_class
        self.modal_id = modal_id
        self.custom_id = custom_id

    async def handle_interaction(self, interaction: Interaction):
        if self.modal_id:
            fetcher = self.handler_class.get_ui_fetcher(interaction.guild_id)
            modal_data = await fetcher.return_modal_data(self.modal_id)
            modal = await fetcher.create_modal_from_data(modal_data, self.handler_class)
            if modal:
                await interaction.response.send_modal(modal)
                return
        elif self.custom_id:
            action = self.handler_class.get_ui_fetcher(interaction.guild_id).get_action_by_custom_id(self.custom_id)
            if action:
                await self.handler_class.get_ui_fetcher(interaction.guild_id).execute_action(interaction, action)

class ButtonView(PersistentView):
    def __init__(self, handler_class, label, style, modal_id=None, custom_id=None):
        super().__init__(handler_class, modal_id, custom_id)
        self.add_item(Button(label=label, style=style, custom_id=custom_id or "button"))

    @button(custom_id="button")
    async def button_callback(self, button: Button, interaction: Interaction):
        await self.handle_interaction(interaction)

class UIFetcher:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = str(guild_id)
        self.ui_elements = load_json("./data/ui_elements.json")
        self.guild_ui = self.ui_elements.get(self.guild_id, {})
        self.register_interactions()
        self.active_views = {}  # Add this line to store views

    def register_interactions(self):
        @self.bot.event
        async def on_interaction(interaction: Interaction):
            # Only handle non-modal interactions here
            if interaction.type == nextcord.InteractionType.modal_submit:
                return
            
            # Let component callbacks handle their own interactions
            if hasattr(interaction, "message"):
                return
            
            custom_id = interaction.data.get('custom_id')
            if not custom_id:
                return

            action = self.get_action_by_custom_id(custom_id)
            if action and not interaction.response.is_done():
                await self.execute_action(interaction, action)

    async def return_embeds(self, name: str):
        item = self.guild_ui.get(name, {})
        embeds_data = item.get("embeds", [])
        if not embeds_data:
            return None
        embeds = [Embed.from_dict(embed_data) for embed_data in embeds_data]
        return embeds

    async def return_modal_data(self, name: str):
        item = self.guild_ui.get(name, {})
        modals_data = item.get("modals", [])
        if not modals_data:
            return None
        return modals_data

    async def create_modal_from_data(self, modal_data, handler_class=None):
        if not modal_data:
            return None

        class DynamicModal(Modal):
            def __init__(self, modal_data, handler):
                super().__init__(
                    title=modal_data["title"],
                    custom_id=modal_data["custom_id"],
                    timeout=modal_data.get("timeout", 300)
                )
                self.handler = handler
                for item in modal_data["items"]:
                    if item["type"] == "text_input":
                        self.add_item(TextInput(
                            label=item["label"],
                            custom_id=item["label"],  # Add this line
                            placeholder=item.get("placeholder", ""),
                            required=item.get("required", True),
                            min_length=item.get("min_length"),
                            max_length=item.get("max_length"),
                            style=TextInputStyle(item.get("text_input_style", 1))
                        ))

            async def callback(self, interaction: Interaction):
                if self.handler and hasattr(self.handler, f"handle_{self.custom_id}"):
                    handler_method = getattr(self.handler, f"handle_{self.custom_id}")
                    values = {item.custom_id: item.value for item in self.children}
                    await handler_method(interaction, values)
                else:
                    await interaction.response.send_message("No handler found for this modal!", ephemeral=True)

        return DynamicModal(modal_data[0], handler_class)

    async def return_components(self, name: str, handler_class=None) -> View:
        """Returns a view with components and handler class for callbacks"""
        item = self.guild_ui.get(name, {})
        components_data = item.get("components", [])
        if not components_data:
            return None

        view = View(timeout=None)
        
        for component in components_data:
            if component["type"] == "button":
                for item_data in component["items"]:
                    button_view = ButtonView(
                        handler_class,
                        label=item_data["label"],
                        style=item_data["style"],
                        modal_id=item_data.get("modal_id"),
                        custom_id=item_data.get("custom_id")
                    )
                    # Store the view
                    view_key = f"{name}_{item_data.get('custom_id')}"
                    self.active_views[view_key] = button_view
                    view.add_item(button_view.children[0])  # Add the button from the view

            elif component["type"] == "select":
                options = [SelectOption(**opt) for opt in component["items"]]
                select = Select(
                    placeholder=component.get("placeholder", "Choose an option"),
                    options=options,
                    custom_id=component.get("custom_id")
                )
                view.add_item(select)
        return view

    async def get_modal_ids(self, name: str):
        """Returns a list of modal IDs associated with a UI element"""
        item = self.guild_ui.get(name, {})
        components = item.get("components", [])
        modal_ids = []
        for component in components:
            if component["type"] == "button":
                for item in component["items"]:
                    if "modal_id" in item:
                        modal_ids.append(item["modal_id"])
        return modal_ids

    def get_action_by_custom_id(self, custom_id):
        for item in self.guild_ui.values():
            actions = item.get("actions", [])
            for action in actions:
                if action.get("custom_id") == custom_id:
                    return action
        return None

    async def execute_action(self, interaction: Interaction, action: dict):
        """Execute an action if the interaction hasn't been responded to"""
        if interaction.response.is_done():
            return

        if action["type"] == "send_message":
            await interaction.response.send_message(action["content"], ephemeral=True)
        elif action["type"] == "assign_role":
            role = interaction.guild.get_role(action["role_id"])
            if role:
                try:
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