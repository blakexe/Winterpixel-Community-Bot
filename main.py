import random, aiohttp, replit
import discord, json, asyncio, typing, os
from replit import db
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

players = []
bots = []
playing = False

os.system('clear')

def generate_random_name():
    adjective = [
        "master",
        "crappy",
        "professional",
        "smelly",
        "oily",
        "rusty",
        "crummy",
        "hamstery",
        "crunchy",
        "slippery",
        "watery",
        "super",
        "superlative",
        "creaky",
        "bloody"
    ]

    noun = [
        "blaster",
        "shagster",
        "killer",
        "dunker",
        "krunker",
        "rocketbotter",
        "bot",
        "turbine-engine",
        "diesel-gusher",
        "dumptruck",
        "rat-driver",
        "hamster-manueverer",
        "badengine",
        "killing-machine",
    ]

    name = random.choice(adjective).capitalize() + random.choice(noun).capitalize()

    random_number = random.choice([True, False])

    if random_number:
        name += f"{random.randint(0, 9)}{random.randint(0, 9)}00"
    
    return name
    
def add_player_coin(player, coins):
    player_coins = db.get(player)
    if player_coins == None:
        db[player] = 500
    dp[player] = db[player] + coins
    return dp[player]


async def refresh_config():
    '''Refresh game configuration every 10 minutes'''
    global server_config

    while True:
        response = await rocketbot_client.get_config()
        server_config = json.loads(response['payload'])
        await asyncio.sleep(600)

@client.event
async def on_message(message: discord.message):
     if "moyai" in message.content.lower() or "🗿" in message.content.lower() or "moai" in message.content.lower():
           await message.add_reaction("🗿")

@client.event
async def on_ready():
    '''Called when the discord client is ready.'''
    #Start up the 10 minute config refresher
    asyncio.create_task(refresh_config())

    print("Winterpixel community bot is ready.")

async def on_message(message):
     if "moyai" in message.content or "🗿" in message.content:
           await message.add_reaction(":moyai:")

@tree.command()
async def leaderboard(interaction: discord.Interaction, season: int = -1):
    '''Return the specified season leaderboard, default current'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    curr_season = server_config['season']

    #If season is unreasonable, default to current season
    if season < 0 or season > curr_season:
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
    await interaction.followup.send(embed=discord.Embed(title=f"Season {season} Leaderboard:", description=message))

@tree.command()
async def get_user(interaction: discord.Interaction, user_type: typing.Literal['User ID', 'Friend ID'], id: str):
    '''Return info about a specified user'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    #If the user specificed a friend code we need to query the server for their ID.
    try:
        if (user_type == "Friend ID"):
            id_response = await rocketbot_client.friend_code_to_id(id)
            id = json.loads(id_response['payload'])['user_id']
        
        #Get user data
        response = await rocketbot_client.get_user(id)
        user_data = json.loads(response['payload'])[0]
        metadata = user_data['metadata']
    except aiohttp.ClientResponseError:
        #The code is wrong, send an error response
        await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), title="❌ Player not found ❌"))
        return

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
    await interaction.followup.send(embed=embed)

@tree.command()
async def bot_info(interaction: discord.Interaction):
    '''Get info about this bot.'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    embed = discord.Embed()
    embed.title = "Bot info:"
    embed.description = "Community discord bot, being hosted on repl.it\n\nFor more info visit https://github.com/Blakiemon/Winterpixel-Community-Bot.\n\n All pull requests will be reviewed, and appreciated."
    await interaction.followup.send(embed=embed)

@tree.command()
async def battle(interaction: discord.Interaction):
    '''Have a battle with a random bot!'''

    await interaction.response.defer(ephemeral=False, thinking=True)
        
    curr_season = server_config['season']

    events = {
        "The bot dodged your attack. <:bot:917467970182189056>"
        : 70,
        "You destroyed the bot! It drops a single coin. <:coin:910247623787700264>"
        : 10,
        "The bot *expertly* dodged your attack. <:bot:917467970182189056>"
        : 5,
        "You thought you hit the bot, but its health returns to full due to network lag. 📶"
        : 5,
        "You destroyed the bot! It drops a some coins and a crate. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> 📦. But <R> comes out of nowhere and steals it."
        : 3,
        "You accidentally hit a teammate and dunk them into the water. <:splash:910252276961128469>"
        : 2,
        "The bot vanishes. An error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>"
        : 1,
        "<R> comes out of nowhere and kills you and the bot to win the game."
        : 1,
        "<R> comes out of nowhere and shoots a shield at the bot deflecting it back to you and you die."
        : 1,
        "You miss. Before you try to shoot again <R> comes out of nowhere and stands next to the bot and you decide to leave out of sheer intimidation."
        : 1,
        "The missile goes off-screen. Instead of getting a kill, a beachball comes hurtling back at mach 2."
        : 0.3,
        "The bot vanishes. Was there ever really a bot there at all?..."
        : 0.2,
        "You destroyed the bot! It drops what appears to be MILLIONS of coins, filling every pixel on your screen with a different shade of gold. Your game immediately slows to a halt and crashes."
        : 0.2,
        "The missile vanishes off the screen, seemingly lost to the water.\nSuddenly, you hear a flurry of *ping*s! The words \"Long Shot!\" splash across your monitor, followed by \"Two Birds\", \"Double Kill\", \"Triple Kill\", and finally \"Quad Kill\". This is it. This is the moment you thought would never happen. The \"Get a quad kill\" and \"Destroy two tanks with one explosion\" goals you've had for two months are finally complete. As the flood of joy and relief washes over you, so does the rising water over your tank. You've lost the match, but you don't care. The war is already won. In a hurry you leave the match and click to the Goals tab, overcome with anticipation to see those beautiful green *Collect!* buttons. You slide your cursor over.\nBAM! The moment before you click, the screen goes black. All you can see is \"Connecting...\". The loading indicator never goes away."
        : 0.1,
        "You get a quad kill, four birds one stone! It was four bots doing the same exact movement. They drop 4 coins. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264>"
        : 0.1,
        "🗿 Moyai God comes down from the heavens and blocks your missile. You bow down (as a tank) and repent for your sins."
        : 0.1,
        "Before your bullet hits the bot you were aiming at, a shiny green bot jumps up and takes the hit. Suddenly a green gem appears where it died, floating in midair. JACKPOT<:gem:910247413695016970>": .1
    }
    event = "You fire a missile at a bot. <:rocketmint:910253491019202661>\n" + random.choices(population=list(events.keys()), weights=events.values(), k=1)[0]
    
    if "<R>" in event:
        #Get random name from leaderboard
        response = await rocketbot_client.query_leaderboard(curr_season)
        records = json.loads(response['payload'])['records']
        rand_player = random.choice(records)['username']

        #Formulate response with random name
        event = event.replace("<R>", rand_player)
    else:
        #Otherwise wait half a second
        await asyncio.sleep(.5)
    
    await interaction.followup.send(event)

@tree.command()
async def build_a_bot(interaction: discord.Interaction):
    '''Bear the responsibility of creating new life... I mean bot'''
    bot_name = generate_random_name()
    players.append(bot_name)
    bots.append(bot_name)
    response = f"***Meet your lovely new bot!***\n\n`{bot_name}`"
    if len(bots) > 5:
        response += f"\n\n`{bot_name}` can't join because 5 bots have already joined"
    else:
        response += f"\n\n`{bot_name}` is joining the next game"
    await interaction.response.send_message(response)


@tree.command()
async def join_game(interaction: discord.Interaction):
    '''Join the current game'''
    response_hidden = False
    if playing:
        await interaction.response.send_message("Can't join because a game is already in progress")
        return
    response = ""
    if interaction.user.mention not in players:
        players.append(interaction.user.mention)
        response += '{} joined'.format(interaction.user.mention)
    else:
        response_hidden = True
        response += '{} you cant join twice'.format(interaction.user.mention)

    await interaction.response.send_message(response, hidden = response_hidden)

@tree.command()
async def start_game(interaction: discord.Interaction):
    '''Start a game with the people joined'''
    global playing 
    if playing:
        return
    playing = True
    response = "Game Starting With: "
    if len(players) <= 1:
        await interaction.response.send_message("Need 2 or more players to start.")
        return
    for i in players:
        response += i + " "
    await interaction.response.send_message(response)
    while len(players) >= 2:
        action_types = {"Kill": 100, "Self": 50, "Miss": 50, "Special": 0}
        
        action_choice = random.choices(population=list(action_types.keys()), weights=action_types.values(), k=1)[0]
        
        
        if action_choice == "Kill":
            coin_num = random.choice(range(1,100))
            player_a = random.choice(players)
            players.remove(player_a)
            player_b = random.choice(players)
            players.remove(player_b)
            kill_messages = {
                "<A> kills <B>.": 100,
                "After a long intense fight <A> kills <B>": 40, 
            }
#                 "<A> kills <B> and <C> `DOUBLE KILL`": 10
#             ,
#                 "<A> kills <B> ,<C> and <D> `TRIPPLE KILL`": 5,
#                 "<A> kills <B>, <C>, <D> and <E> `QUAD KILL`": 5,
            event = random.choices(population=list(kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
            event = event.replace("<A>", player_a)
            event = event.replace("<B>", player_b)
            #B-E die for kills, if we need a non dying player use F
            event += "\n\n" + player_a + " got " + str(coin_num) + " <:coin:910247623787700264>"
            event += " and " + player_b + " lost " + str(coin_num) + " <:coin:910247623787700264>"
            if "<C>" in event:
#                 cur_num = random.choice(range(1,100)
                player_c = random.choice(players)
                db[player_c] = db[player_c] - cur_num
                player.remove(player_c)
                event = event.replace("<C>", player_c)
            if "<D>" in event:
#                 coin_num += random.choice(range(1,100)
                player_d = random.choice(players)
                player.remove(player_d)
                event.replace("<D>", player_d)
            if "<E>" in event:
#                 coin_num += random.choice(range(1,100)
                player_e = random.choice(players)
                player.remove(player_e)
                event.replace("<E>", player_e)
            if "<F>" in event:
                player_f = random.choice(players)
                event.replace("<F>", player_f)
            players.append(player_a)
            await interaction.channel.send(event)
        elif action_choice == "Miss":        
            choices = random.sample(set(players), 2)
            player_a = choices[0]
            player_b = choices[1]
            await interaction.channel.send(player_a + " shoots at " + player_b + " but misses.")
        elif action_choice == "Self":
            kill_messages = {
                "<A> jumps into the water.": 100,
                "On <A>'s screen an error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>": 1}
            event = random.choices(population=list(kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
            player_a = random.choice(players)
            players.remove(player_a)
            event = event.replace("<A>", player_a)
            await interaction.channel.send(event)
#             case "Special":
#                 pass
        await asyncio.sleep(5)
    await interaction.channel.send(players[0] + " wins!")
    playing = False
    players.clear()
    bots.clear()

@tree.command()
async def get_money(interaction: discord.Interaction):
    await interaction.channel.send(add_player_coin(0))

@tree.command(guild=discord.Object(id=962142361935314996))
async def sync_commands(interaction: discord.Interaction):
    await tree.sync()
    await tree.sync(guild=discord.Object(id=962142361935314996))
    await interaction.response.send_message("Commands synced.")

def main():
    client.run(discord_token)


if (__name__ == "__main__"):
    main()
