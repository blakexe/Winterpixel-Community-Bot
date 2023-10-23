import discord
import json
import os
import io
from discord import app_commands
from clients.moonrockminers_client import MoonrockMinersClient


try:
    discord_token = os.environ["discord_token"]
    rbr_mm_email_password = os.environ["rbr_mm_email_password"]
except KeyError:
    print(
        "ERROR: An environment value was not found. Please make sure your environment.json has all the right info or that you have correctly preloaded values into your environment."
    )
    os._exit(1)


# Set up discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
moonrock_miners_server_config = {}


# Initialize moonrock miners client
moonrock_miners_client = MoonrockMinersClient(rbr_mm_email_password, rbr_mm_email_password)


async def refresh_config():
  """Refresh Moonrock Miners game configuration"""

  global moonrock_miners_server_config

  response = await moonrock_miners_client.get_config()
  moonrock_miners_server_config = json.loads(response["payload"])


class MoonrockMiners(app_commands.Group): # MM_NRC
    """Moonrock Miners non-reaction commands"""
    
    def __init__(self, bot: discord.client):
        super().__init__()

    
    @tree.command()
    async def get_config(self, interaction: discord.Interaction):
        """🟢 Get the most updated Moonrock Miners server config"""

        await refresh_config()
        
        file = io.StringIO(json.dumps(moonrock_miners_server_config))
        await interaction.response.send_message(
            file=discord.File(fp=file, filename="moonrock_miners_server_config.json")
        )