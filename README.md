# JoDBS_Tools

JoDBS_Tools is a utility library designed to simplify tasks such as connecting to MongoDB databases, implementing role-based access control in Discord bots, and interfacing with external APIs or Node Networks.

## Features

- **Simplify Bot Setup**: Clear up your main bot file and just pass what you need.
- **Database Connection**: Seamlessly connect to MongoDB databases.
- **Role-Based Decorators**: Restrict bot commands based on user roles using custom decorators.
- **API Integration**: Easily connect to external APIs and retrieve data for your applications.
- **Enhanced Bot Network Integration**: Additional methods for connecting to your Bot Node Network.
- **YouTube Video Notifier**: Receive notifications for new videos from your favorite YouTubers.

## Upcoming Features

- **Asynchronous Functions**: Improved performance with asynchronous functions for bot setup and network connections.
- **Logging Support**: Log all those print statements into a log.txt file instead, no need for endless console spam. Your code runs without issues now, yes?
- **Extensive Documentation**: Learn how to use a NodeConnection with your Bot. 

## Installation

Install the package using pip:

```sh
pip install JoDBS-Tools
```

## Usage

Run a simple Discord Bot (Local Hosted):

```python
import os
from nextcord.ext import commands
from nextcord import Intents
from JoDBS_Tools import BotSetup

bot = commands.Bot(intents=Intents.all())

env_path = os.path.join(os.path.dirname(__file__), '.env')
bot_setup = BotSetup(bot, env_path=env_path, NodeConnection=False)


if __name__ == "__main__":
    bot_setup.setup_bot(NodeConnection=False)
```

Run Discord Bot with a Node Connection (Cloud Hosted):

```python
from nextcord.ext import commands
from nextcord import Intents
from JoDBS_Tools import BotSetup

bot = commands.Bot(intents=Intents.all())

bot_setup = BotSetup(bot)


if __name__ == "__main__":
    bot_setup.setup_bot()
```

## Required Environment Variables

- **APPLICATION_ID**: Your application ID.
- **BNC_API_KEY**: Your BNC API key.
- **BNC_BASE_URL**: The base URL for the BNC API.
- **TOKEN**: Your authentication token.