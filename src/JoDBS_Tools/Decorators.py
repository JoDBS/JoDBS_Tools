import functools, traceback
from nextcord.ext import commands
from nextcord import Interaction, Member
from .utils import load_json
from datetime import datetime, timedelta

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
                interaction = next((arg for arg in args if isinstance(arg, Interaction)), None)

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
    _cooldowns = {}

    @classmethod
    def protected_command(cls, rate=1, per=60.0, type=commands.BucketType.user):
        """
        A decorator to add cooldown to slash commands.
        
        Args:
            rate (int): Number of uses allowed
            per (float): Cooldown period in seconds
            type (commands.BucketType): The type of cooldown (user, guild, etc.)
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                interaction = next((arg for arg in args if isinstance(arg, Interaction)), None)
                if not interaction:
                    raise TypeError("Interaction object not found in arguments")

                # Create cooldown key based on type
                if type == commands.BucketType.user:
                    key = f"{func.__name__}:{interaction.user.id}"
                elif type == commands.BucketType.guild:
                    key = f"{func.__name__}:{interaction.guild.id}"
                else:
                    key = f"{func.__name__}:global"

                current_time = datetime.now()
                if key in cls._cooldowns:
                    remaining = (cls._cooldowns[key] - current_time).total_seconds()
                    if remaining > 0:
                        await interaction.response.send_message(
                            f"Please wait {round(remaining, 1)} seconds before using this command again.",
                            ephemeral=True
                        )
                        return

                # Execute command and set cooldown
                try:
                    await func(*args, **kwargs)
                    cls._cooldowns[key] = current_time + timedelta(seconds=per)
                except Exception as e:
                    print(f"Error in cooldown protected command: {e}")
                    await interaction.response.send_message(
                        "An error occurred while processing the command.",
                        ephemeral=True
                    )

            return wrapper
        return decorator