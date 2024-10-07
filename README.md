# JoDBS_Tools

JoDBS_Tools is a utility library designed to simplify tasks such as connecting to MongoDB databases, implementing role-based access control in Discord bots, and interfacing with external APIs or Node Networks.

## Features

- **Simplify Bot Setup**: Clear up your main bot file and just pass what you need.
- **Database Connection**: Seamlessly connect to MongoDB databases.
- **Role-Based Decorators**: Restrict bot commands based on user roles using custom decorators.
- **API Integration**: Easily connect to external APIs and retrieve data for your applications.
- **Enhanced Bot Network Integration**: Additional methods for connecting to your Bot Node Network.

## Upcoming Features

- **YouTube Video Notifier**: Receive notifications for new videos from your favorite YouTubers.
- **Asynchronous Functions**: Improved performance with asynchronous functions for bot setup and network connections.

## Installation

Install the package using pip:

```sh
pip install JoDBS_Tools
```

## Usage

Run a simple Discord Bot:

```python
import os
from nextcord.ext import commands
from nextcord import Intents
from JoDBS_Tools import BotSetup

intents = Intents.all()

bot = commands.Bot(intents=intents)

env_path = os.path.join(os.path.dirname(__file__), '.env')
bot_setup = BotSetup(bot, env_path=env_path)


if __name__ == "__main__":
    bot_setup.setup_bot()
```