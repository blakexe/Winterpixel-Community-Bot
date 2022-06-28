import random, aiohttp, replit
import discord, json, asyncio, typing, os, io
from collections import OrderedDict
from operator import itemgetter
from statistics import mean
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

#Initialize crate bot related variables
one_star_total, two_star_total, three_star_total = 30, 14, 0
total = one_star_total + two_star_total + three_star_total
one_star_weight, two_star_weight, three_star_weight = 30, 10, 1
total_weight = one_star_total * one_star_weight + two_star_total * two_star_weight + three_star_total * three_star_weight
one_star_prob, two_star_prob, three_star_prob = one_star_weight / total_weight, two_star_weight / total_weight, three_star_weight / total_weight

basic_crate_price = 1000
elite_crate_price = 20000

population_crate = list(range(1, total + 1))
weights_crate = []
for i in range(1, one_star_total + 1):
    weights_crate.append(one_star_prob)
for j in range(1, two_star_total + 1):
    weights_crate.append(two_star_prob)
for k in range(1, three_star_total + 1):
    weights_crate.append(three_star_prob)

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

    name = (adjective).capitalize() + random.choice(noun).capitalize()

    random_number = random.choice([True, False])

    if random_number:
        name += f"{random.randint(0, 9)}{random.randint(0, 9)}00"
    
    return name
    
def add_player_coin(player, coins):
    player_coins = db.get(player)
    if player_coins == None:
        db[player] = 500
    db[player] = db[player] + coins
    return db[player]

def basic_or_elite(a, b, c):
    time = 1 / (1 - one_star_prob * a - two_star_prob * b -
                three_star_prob * c)
    expected_basic_crate_coin = basic_crate_price * time
    if expected_basic_crate_coin < elite_crate_price:
        return f":one: The **OPTIMAL** way to unlock **A NEW UNIQUE SKIN** is **EXPECTED** by using **{time:.2f} BASIC CRATE" + (
            "S" if time > 1 else ""
        ) + f" <:crate:988520294132088892>**, which " + (
            "are" if time > 1 else "is"
        ) + f" worth a **TOTAL** of **{expected_basic_crate_coin:,.0f} COINS <:coin:910247623787700264>**\n"
    else:
        return f":one: The **OPTIMAL** way to unlock **A NEW UNIQUE SKIN** is **EXPECTED** by using **1.00 ELITE CRATE <:elitecrate:989954419846184970>**, which is worth a **TOTAL** of **{elite_crate_price:,.0f} COINS <:coin:910247623787700264>**\n"

def basic_and_elite_simulate(a, b, c):
    expected_basic_crate = []
    expected_elite_crate = []
    expected_coins_spent = []

    for i in range(0, 1001):
        basic_crates = 0
        prob = 1 - one_star_prob * a - two_star_prob * b - three_star_prob * c
        collected = set()
        for i in range(1, 1 + a):
            collected.add(i)
        for j in range(one_star_total + 1, one_star_total + 1 + b):
            collected.add(j)
        for k in range(one_star_total + two_star_total + 1, one_star_total + two_star_total + 1 + c):
            collected.add(k)

        while True:
            if (1 / prob) * basic_crate_price >= elite_crate_price:
                break
            got = random.choices(population_crate, weights_crate)
            basic_crates += 1
            for i in got:
                if int(i) not in collected:
                    collected.add(int(i))
                    if 1 <= int(i) <= one_star_total:
                        prob -= one_star_prob
                    elif (one_star_total + 1) <= int(i) <= (one_star_total + two_star_total):
                        prob -= two_star_prob
                    else:
                        prob -= three_star_prob
        elite_crates = total - len(collected)
        coins_spent = basic_crates * basic_crate_price + elite_crates * elite_crate_price
        expected_basic_crate.append(basic_crates)
        expected_elite_crate.append(elite_crates)
        expected_coins_spent.append(coins_spent)
        remaining = total - a - b - c
        expected_basic_crate_mean = mean(expected_basic_crate)
        expected_elite_crate_mean = mean(expected_elite_crate)
    return f":two: The **OPTIMAL** way to unlock **ALL {remaining} REMAINING UNIQUE SKIN" + (
        "S" if remaining > 1 else ""
    ) + "** is **EXPECTED** by using " + (
        (f"**{expected_basic_crate_mean:,.2f} BASIC CRATE" +
         ("S" if expected_basic_crate_mean > 1 else "") +
         " <:crate:988520294132088892>** and ")
        if expected_basic_crate_mean != 0 else ""
    ) + f"**{expected_elite_crate_mean:,.2f} ELITE CRATE" + (
        "S" if expected_elite_crate_mean > 1 else ""
    ) + f" <:elitecrate:989954419846184970>**, which " + (
        "are" if
        (expected_basic_crate_mean
         + expected_elite_crate_mean) > 1 else "is"
    ) + f" worth a **TOTAL** of **{expected_basic_crate_mean * basic_crate_price + expected_elite_crate_mean * elite_crate_price:,.0f} COINS <:coin:910247623787700264>**"

def all(a, b, c):
    total_owned = a + b + c
    if (1 <= a <= one_star_total) and (0 <= b <= two_star_total) and (0 <= c <=
                                                          three_star_total):
        if total_owned != total:
            return f"**1,000 SIMULATIONS** have been done based on the number of **{a} ONE-STAR :star:** AND **{b} TWO-STAR :star::star: SKIN"+ ("S" if total_owned > 1 else "") + f"** you have already owned:\n" + basic_or_elite(a, b, c) + basic_and_elite_simulate(a, b, c)
            # return f"**1,000 SIMULATIONS** have been done based on the number of **{a} ONE-STAR :star:**, **{b} TWO-STAR :star::star:** and **{c} THREE-STAR :star::star::star: SKIN" + (
            #     "S" if total_owned > 1 else
            #     "") + f"** you have already owned:\n" + basic_or_elite(
            #         a, b, c) + basic_and_elite_simulate(a, b, c)
        else:
            return f"You have alredy unlocked **ALL {total} UNIQUE SKINS**! :tada:"
    else:
        return ":x: **INVALID** data has been entered. Please try again. :x:"

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
     if "!idea" in message.content.lower():
           await message.add_reaction("<:upvote:910250647264329728>")
           await message.add_reaction("<:downvote:910250215217459281>")
           await message.add_reaction("⭐")

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
    response = f"***Meet your lovely new bot!***\n\n`{bot_name}`"
    if len(bots) > 5:
        response += f"\n\n`{bot_name}` can't join because 5 bots have already joined"
    else:
        response += f"\n\n`{bot_name}` is joining the next game"
        players.append(bot_name)
        bots.append(bot_name)
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

    await interaction.response.send_message(response)

@tree.command(guild=discord.Object(id=962142361935314996))
async def get_config(interaction: discord.Interaction):
    file = io.StringIO(json.dumps(server_config))
    await interaction.response.send_message(file=discord.File(fp=file, filename="server_config.json"))

@tree.command()
async def start_game(interaction: discord.Interaction):
    '''Start a game with the people joined'''
    global playing 
    if playing:
        return
    playing = True
    response = "Game Starting With: "
    if len(players) <= 1:
        playing = False
        await interaction.response.send_message("Need 2 or more players to start.")
        return
    for i in players:
        response += "\n" + i
    embed1=discord.Embed(color=0xa80022)
    embed1.add_field(name="Players: ", value=response, inline=False)
    await interaction.response.send_message(response)
    msg = await interaction.channel.send("Starting game")
#     await asyncio.sleep(0)
    moneys = OrderedDict()
    while len(players) >= 1:
        embed=discord.Embed(color=0xa80022)
        if len(players) <= 1:
            embed.add_field(name="Players: ", value=players[0], inline=False)
            embed.add_field(name="Game:", value=players[0] + " wins!", inline=False)
            money_txt = ""
            for i in moneys.keys():
                money_txt += i + " " + str(moneys[i]) + "<:coin:910247623787700264>\n"
            if money_txt != "":
                embed.add_field(name="Money:", value=money_txt, inline=False)
            await msg.edit(embed=embed)
            playing = False
            players.clear()
            bots.clear()
            break
        player_text = ""
        players.sort()
        for i in players:
            player_text += i + " "
        embed.add_field(name="Players: ", value=player_text, inline=False)
        action_types = {"Kill": 100, "Miss": 50, "Self": 20, "Special": 0}
        
        action_choice = random.choices(population=list(action_types.keys()), weights=action_types.values(), k=1)[0]
        
        action = ""
        if action_choice == "Kill":
            coin_num = random.choice(range(1,100))
            player_a = random.choice(players)
            players.remove(player_a)
            player_b = random.choice(players)
            players.remove(player_b)
            kill_messages = {
                "<A> kills <B>.": 100,
                "After a long intense fight <A> kills <B>": 40,
                "<A> kills <B> with <U>": 40,
                "<A> hits <B> into the water": 20,
                "<B> shoots it at <A> but <A> blocks it with a shield reflects it back to <B> who dies": 7,
                "<A> pretends to friend <B> but then kills them": 5,
                "<A> intimidates <B> into jumping into the water": 0.5,
            }
#             if len(players) > 2:
#                 kill_messages["<A> kills <B> and <C> `DOUBLE KILL`"] = 10
#             if len(players) > 3:
#                 kill_messages["<A> kills <B> ,<C> and <D> `TRIPPLE KILL`"] = 5
#             if len(players) > 4:
#                 kill_messages["<A> kills <B>, <C>, <D> and <E> `QUAD KILL`"] = 2
            weopons = {
                "A FAT BOI (nuke)": 100,
                "Rapidfire missiles": 100,
                "Grenades": 100,
                "A Homing Missile": 100,
                "A Flak": 100,
                "A Drill": 100,
                "THE POWER OF MOYAI 🗿": 0.1
            }
            event = random.choices(population=list(kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
            event = event.replace("<A>", player_a)
            event = event.replace("<B>", player_b)
            if "<U>" in event:
                event = event.replace("<U>", random.choices(population=list(weopons.keys()), weights=weopons.values(), k=1)[0])
            #B-E die for kills, if we need a non dying player use F
            event += "\n\n" + player_a + " got " + str(coin_num) + " <:coin:910247623787700264>"
            event += " and " + player_b + " lost " + str(coin_num) + " <:coin:910247623787700264>"
            add_player_coin(player_a,coin_num)
            add_player_coin(player_b,-coin_num)
            if moneys.get(player_a) == None:
                moneys[player_a] = coin_num
            else:
                moneys[player_a] = moneys[player_a] + coin_num
            if moneys.get(player_b) == None:
                moneys[player_b] = -coin_num
            else:
                moneys[player_b] = moneys[player_b] - coin_num
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
            action = event
        elif action_choice == "Miss":        
            choices = random.sample(set(players), 2)
            player_a = choices[0]
            player_b = choices[1]
#             if "<F>" in event:
#                 player_f = random.choice(players)
#                 event.replace("<F>", player_f)
            action = player_a + " shoots at " + player_b + " but misses."
        elif action_choice == "Self":
            kill_messages = {
                "<A> jumps into the water.": 50,
                "On <A>'s screen an error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>": 1}
            event = random.choices(population=list(kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
            player_a = random.choice(players)
            players.remove(player_a)
            event = event.replace("<A>", player_a)
            if moneys.get(player_a) == None:
                moneys[player_a] = 0
            action = event
#             case "Special":
#                 pass
        embed.add_field(name="Game:", value=action, inline=False)
        money_txt = ""
        for i in moneys.keys():
            money_txt += i + " " + str(moneys[i]) + "<:coin:910247623787700264>\n"
        if money_txt != "":
            embed.add_field(name="Money:", value=money_txt, inline=False)
        await msg.edit(embed=embed)
        await asyncio.sleep(5)

@tree.command()
async def get_money(interaction: discord.Interaction):
    '''Find out how much money you have in discord'''
    await interaction.response.send_message(interaction.user.mention + " has " + str(add_player_coin(interaction.user.mention,0)) + " <:coin:910247623787700264>")

@tree.command()
async def discord_coins_leaderboard(interaction: discord.Interaction):
    '''Return the discord coins leaderboard'''
    rankdict = {}
  
    for key in db.keys():
        rankdict[key] = db[key]

    sorted_rankdict = sorted(rankdict.items(), key=itemgetter(1), reverse=True)
    message = f"```\n{'Rank:':<5} {'Name:':<20} {'Coins:'}\n{'‾' * 35}\n"
    sorted_rankdict = sorted_rankdict[:10]
    for i in sorted_rankdict:
        message += f"{'#' + str(sorted_rankdict.index(i) + 1):<5} {i[0]:<20} {i[1]:>5,d} 🪙\n"
    message += "```"
    await interaction.response.send_message("test")
#    embed=discord.Embed(color=0xffd700, title="Discord Coins Leaderboard", description=message)
#    await interaction.response.send_message()

@tree.command()
async def slot(interaction: discord.Interaction, bet: int):
    '''Play the slot machine game!'''
    
    tempp = db.get(interaction.user.mention)
    
#     if tempp > 0:
# #     await interaction.response.send_message("test")
#         await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(),title="SLOT MACHINE :slot_machine:", description="You don't have enough <:coin:910247623787700264>"))
#     else:
#         None
        
    if tempp <= 0:
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(),title="SLOT MACHINE :slot_machine:", description="You don't have enough <:coin:910247623787700264>"))

    elif bet <= 0:
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(),title="SLOT MACHINE :slot_machine:", description="The minimum bet is 1 <:coin:910247623787700264>"))
    
#     else:
#         await interaction.response.send_message('test')

    else:
        events_2 = {
        "<:coin:910247623787700264>": 50,
        "<:coins2:991267848875950210>": 25,
        "<:coins2:976289335844434000>": 12.5,
        "<:coins3:976289358200049704>": 7.5,
        "<:coins:976288324266373130>": 5,
        }
        multiplier = [5, 15, 25, 75, 450]
    
        slots = []  
        for i in range(9):
            slots.append(random.choices(population=list(events_2.keys()), weights=events_2.values())[0])
        
        res_1 = f":black_large_square: {slots[0]} {slots[1]} {slots[2]} :black_large_square:\n:arrow_forward:~~ {slots[3]} {slots[4]} {slots[5]} ~~:arrow_backward: :joystick:\n:black_large_square: {slots[6]} {slots[7]} {slots[8]} :black_large_square:"

#         if (slots[3] == slots[4] == slots[5]):
#             p = list(events_2).index(slots[3])
#             res_2 = f"Congratulations! :tada:\nYou won **{bet * multiplier[p]}** <:coin:910247623787700264>! ({multiplier[p]}x)"
#             add_player_coin(interaction.user.mention, bet * multiplier[p])
#         else:
#             res_2 = "Try again?"
#             add_player_coin(interaction.user.mention, -bet)
        
#         new_player_coin = add_player_coin(interaction.user.mention, 0)
#         res_3 = f"You now have {new_player_coin} <:coin:910247623787700264>"
        await interaction.response.send_message(embed=discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"{res_1}"))
#         await interaction.response.send_message(embed=discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"{res_1}\n\n{res_2}\n\n{res_3}"))

@tree.command()
async def random_tank(interaction: discord.Interaction):
    '''Get a random tank'''
    tanks = [
        "<:betatank:989949271547723796>", "<:bladetank:989949828417060864>",
        "<:buggytank:989951288232013866>", "<:cannontank:989949877079375943>",
        "<:catapultevolvedtank:989951212126359652>",
        "<:catapulttank:989951161152991262>", "<:concavetank:989951111773429841>",
        "<:crabevolvedtank:989951034132693044>", "<:crabtank:989949776927817738>",
        "<:crawlertank:989949727858630726>", "<:cyclopstank:989950970429595688>",
        "<:diamondtank:989950859561566328>",
        "<:dozerevolvedtank:989950801663369226>",
        "<:dozertank:989950741433163806>", "<:forklifttank:989950685288222720>",
        "<:gearstank:989950531772493844>", "<:haytank:989950495181393922>",
        "<:hollowtank:989949132934361259>", "<:longtank:989950441477513247>",
        "<:medictank:989950400796950538>", "<:mixertank:989950349764878376>",
        "<:pagliaccitank:989950280487567370>", "<:pailtank:989951621314256987>",
        "<:pistonstank:989949672372174888>", "<:reactortank:989949207244853319>",
        "<:spiketank:989949916614889494>", "<:squaretank:989950023750017064>",
        "<:traptank:989950224187412510>", "<:treadtank:989949317404061717>",
        "<:tubdowntank:989950141370892368>", "<:tubtank:989950185159401513>",
        "<:wavetank:989950102414180442>", "<:zigtank:989950065101639720>",
        "<:blackdefaulttank:990837213556244490>", "<:blacklongtank:990837173970411600>",
        "<:blacktreadtank:990837309446455356>", "<:browncrawlertank:990837535666212884>",
        "<:goldcanontank:990837078340300820>", "<:goldbladetank:990837027136241694>",
        "<:goldcyclopstank:990837123919781898>", "<:whitedefaulttank:990837258359799838>"
    ]
    await interaction.response.send_message(random.choice(tanks))

@tree.command()
async def get_crate_stats(interaction: discord.Interaction, one_star: int, two_star: int):
    '''Optimize the use of in game crates and Estimate the amount of coins'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    await interaction.followup.send(all(one_star, two_star, 0))

@tree.command(guild=discord.Object(id=962142361935314996))
async def sync_commands(interaction: discord.Interaction):
    await tree.sync()
    await tree.sync(guild=discord.Object(id=962142361935314996))
    await interaction.response.send_message("Commands synced.")

def main():
    client.run(discord_token)

if (__name__ == "__main__"):
    main()
""
