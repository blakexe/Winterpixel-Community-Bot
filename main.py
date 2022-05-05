import random
import time
import discord, json, asyncio, typing, os
from discord import app_commands
from rocketbot_client import RocketBotClient

#Attempt to retrieve enviroment from environment.json
working_directory = os.path.dirname(os.path.realpath(__file__))
try:
    with open(os.path.join(working_directory, "environment.json"), "r") as f:
        data = json.loads(f.read())
        for key, value in data.items():
            os.environ[key] = value
except IOError:
    print("Environment.json not found, switching to default environment.")
else:
    print("Found environment.json. Starting bot now...")

#Get sensitive info
try:
    discord_token = os.environ['discord_token']
    rocketbot_user = os.environ['rocketbot_username']
    rocketbot_pass = os.environ['rocketbot_password']
except KeyError:
    print("ERROR: An environment value was not found. Please make sure your environment.json has all the right info or that you have correctly preloaded values into your environment.")
    os._exit(1)

#Set up discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
server_config = {}

#Initialize rockebot client
rocketbot_client = RocketBotClient(rocketbot_user, rocketbot_pass)

async def refresh_config():
    '''Refresh game configuration every 10 minutes'''
    global server_config

    while True:
        response = await rocketbot_client.get_config()
        server_config = json.loads(response['payload'])
        await asyncio.sleep(600)

@client.event
async def on_ready():
    '''Called when the discord client is ready.'''
    #Start up the 10 minute config refresher
    asyncio.create_task(refresh_config())

    print("Winterpixel community bot is ready.")

@tree.command()
async def leaderboard(interaction: discord.Interaction, season: int = -1):
    '''Return the specified season leaderboard, default current'''

    curr_season = server_config['season']

    #If season is unreasonable, default to current season
    if season <= 0 or season > curr_season:
        season = curr_season

    #Get leaderboard info
    response = await rocketbot_client.query_leaderboard(season)
    records = json.loads(response['payload'])['records']

    #Using f-string spacing to pretty print the leaderboard labels
    message = f"```{'Rank:':<5} {'Name:':<20} {'Points:'}\n{'‾' * 35}\n"
    
    #Using f-string spacing to pretty print the leaderboard.
    for record in records:
        message += f"{'#' + str(record['rank']):<5} {record['username']:<20} {'🏆' + '{:,}'.format(record['score'])}\n"
    message += "```"

    #Send
    await interaction.response.send_message(embed=discord.Embed(title=f"Season {season} Leaderboard:", description=message))

@tree.command()
async def get_user(interaction: discord.Interaction, user_type: typing.Literal['User ID', 'Friend ID'], id: str):
    '''Return info about a specified user'''

    #If the user specificed a friend code we need to query the server for their ID.
    if (user_type == "Friend ID"):
        id_response = await rocketbot_client.friend_code_to_id(id)
        id = json.loads(id_response['payload'])['user_id']
    
    #Get user data
    response = await rocketbot_client.get_user(id)
    user_data = json.loads(response['payload'])[0]
    metadata = user_data['metadata']

    #Create embed
    embed = discord.Embed()

    #Get award config
    awards_config = server_config['awards']
    default_award = {'type': "Unknown", "name": "Unknown"}

    #Get general player info
    username = user_data['display_name']
    is_online = user_data['online']
    current_tank = metadata['skin'].replace("_", " ").title()
    current_badge = awards_config.get(metadata['badge'], default_award)['name']
    level = metadata['progress']['level']
    friend_code = metadata['friend_code']
    id = user_data['user_id']

    #Add general player info
    general_info = "```"
    general_info += f"Username: {username}\n"
    general_info += f"Online: {is_online}\n"
    general_info += f"Current Tank: {current_tank}\n"
    general_info += f"Current Badge: {current_badge}\n"
    general_info += f"Level: {level}\n"
    general_info += f"Friend Code: {friend_code}\n"
    general_info += f"User ID: {id}\n"
    general_info += "```"

    #Add to embed
    embed.add_field(name="📓 ***General Info***:", value=general_info, inline=False)

    #Create badge list
    badge_list = "```"

    for badge in metadata['awards']:
        award = awards_config.get(badge, default_award)
        type = award['type']

        if type == "badge":
            badge_list += award['name'] + "\n"
    badge_list += "```"

    #Add to embed
    embed.add_field(name="🛡️ ***Badges***:", value=badge_list, inline=False)

    #Create stats
    stat_list = "```"
    for key, value in metadata['stats'].items():
        stat_list += f"{key.replace('_', ' ').title()}: {value}\n"
    stat_list += "```"

    #Add to embed
    embed.add_field(name="🗒️ ***Stats***:", value=stat_list, inline=False)

    #Send message
    await interaction.response.send_message(embed=embed)

@tree.command()
async def bot_info(interaction: discord.Interaction):
    '''Get info about this bot.'''
    embed = discord.Embed()
    embed.title = "Bot info:"
    embed.description = "Community discord bot, being hosted on repl.it\n\nFor more info visit https://github.com/Blakiemon/Winterpixel-Community-Bot.\n\n All pull requests will be reviewed, and appreciated."
    await interaction.response.send_message(embed=embed)

@tree.command()
async def battle(interaction: discord.Interaction):
    '''Have a battle with a random bot!'''
    async with interaction.channel.typing():
        await asyncio.sleep(1)
    
    event = random.choices(
        population=[
            "The bot dodged your attack. <:bot:917467970182189056>",
            "You thought you hit the bot, but its health goes back up due to network lag.",
            "You destroyed the bot!\nIt drops one coin. <:coin:910247623787700264>",
            "The bot vanishes. An error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>",
            "You get a quad kill, four birds one stone! It was four bots doing the same exact movement. They drop 4 coins. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264>"
        ],
        weights=[
            89,
            5,
            10,
            1,
            1,
        ],
        k=1,
    )[0]
    await interaction.response.send_message(event)


@tree.command(guild=discord.Object(id=962142361935314996))
async def sync_commands(interaction: discord.Interaction):
    await tree.sync()
    await interaction.response.send_message("Commands synced.")

def main():
    client.run(discord_token)


if (__name__ == "__main__"):
    main()
