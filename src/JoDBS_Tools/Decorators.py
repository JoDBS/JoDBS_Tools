import functools
from nextcord.ext import commands
from nextcord import Interaction, Member
from .utils import load_json

class Permission_Checks:
    @staticmethod
    def has_role(role_name):
        """
        A decorator to check if the user has a specific role before executing the command.

        Args:
            role_name (str): The name of the role required to execute the command.

        Returns:
            function: The wrapped function which includes the role check.
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Find the Interaction object in the arguments
                interaction = None
                for arg in args:
                    if isinstance(arg, Interaction):
                        interaction = arg
                        break

                if interaction is None:
                    raise TypeError("Interaction object not found in arguments")

                try:
                    roles_data = load_json(file_path="./data/roles.json") or {}
                    if isinstance(interaction.user, Member):
                        server_id = str(interaction.guild.id)
                        member_role_ids = [role.id for role in interaction.user.roles]
                        server_roles = roles_data.get(server_id, {})
                        required_role_id = server_roles.get(role_name)

                        if required_role_id and int(required_role_id) in member_role_ids:
                            # User has the required role; proceed with the command
                            return await func(*args, **kwargs)
                        else:
                            await interaction.send(
                                "You do not have the required role to use this command.",
                                ephemeral=True
                            )
                            print(f"[INFO] Missing role for user {interaction.user} in command {interaction.application_command.name}.")
                            return
                    else:
                        await interaction.send(
                            "This command cannot be used in DMs.",
                            ephemeral=True
                        )
                        print(f"[INFO] Command {interaction.application_command.name} attempted in DMs by user {interaction.user}.")
                        return
                except Exception as e:
                    print(f"Error in role check: {e}")
                    await interaction.send(
                        "An error occurred while checking this role based command.",
                        ephemeral=True
                    )
            return wrapper
        return decorator