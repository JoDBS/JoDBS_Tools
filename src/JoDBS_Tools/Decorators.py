from nextcord.ext import commands
from nextcord import Interaction, Member
import functools

class Permission_Checks:
    @staticmethod
    def has_role(role_id):
        """
        A decorator to check if the user has a specific role before executing the command.

        Args:
            role_id (int): The ID of the role required to execute the command.

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
                    if isinstance(interaction.user, Member):
                        user_roles = [role.id for role in interaction.user.roles]
                        if int(role_id) not in user_roles:
                            await interaction.send("You do not have the required role to use this command.", ephemeral=True)
                            print(f"[INFO] Missing role for user {interaction.user} in command {interaction.application_command.name}.")
                            return
                    else:
                        await interaction.send("This command cannot be used in DMs.", ephemeral=True)
                        print(f"[INFO] Command {interaction.application_command.name} attempted in DMs by user {interaction.user}.")
                        return

                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in role check: {e}")
                    await interaction.send("An error occurred while checking your role.", ephemeral=True)
            return wrapper
        return decorator