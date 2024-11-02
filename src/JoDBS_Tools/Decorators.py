import functools, traceback
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
    
class Cooldown_Checks:
    @staticmethod
    def protected_command(rate, per, bucket_type=commands.BucketType.user):
        """
        A decorator to apply cooldown and error handling to a command.

        Args:
            rate (int): Number of allowed invocations during the cooldown period.
            per (float): Cooldown period in seconds.
            bucket_type (commands.BucketType): The type of cooldown bucket.

        Returns:
            function: The wrapped function which includes cooldown and error handling.
        """
        def decorator(func):
            @functools.wraps(func)
            @commands.cooldown(rate, per, bucket_type)  # Apply cooldown to the wrapper
            async def wrapper(*args, **kwargs):
                # Extract the Interaction object from arguments
                interaction = next((arg for arg in args if isinstance(arg, Interaction)), None)

                if interaction is None:
                    raise TypeError("Interaction object not found in arguments")

                try:
                    # Execute the command (with cooldown applied)
                    return await func(*args, **kwargs)
                except commands.CommandOnCooldown as e:
                    # Inform the user about the cooldown
                    await interaction.response.send_message(
                        f"This command is on cooldown. Try again in {round(e.retry_after, 2)} seconds.",
                        ephemeral=True
                    )
                except Exception as e:
                    # Handle other exceptions
                    await interaction.response.send_message(
                        "An error occurred while processing the command.",
                        ephemeral=True
                    )
                    # Log the exception details
                    print(f"Error in command '{func.__name__}': {e}")
                    traceback.print_exc()
            return wrapper
        return decorator