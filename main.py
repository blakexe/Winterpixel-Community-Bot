import random, aiohttp, replit
import discord, json, asyncio, typing, os, io
from collections import defaultdict, OrderedDict
from operator import itemgetter
from statistics import mean
from timeit import default_timer as timer
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

#Initialize get_crate_stats related variables
one_star_total, two_star_total, three_star_total = 30, 17, 0
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

#List contains all tank emojis for random_tank and memory command
tanks = [
    "<:betatank:989949271547723796>", "<:bladetank:989949828417060864>",
    "<:buggytank:989951288232013866>", "<:cannontank:989949877079375943>",
    "<:catapultevolvedtank:989951212126359652>",
    "<:catapulttank:989951161152991262>", "<:concavetank:989951111773429841>",
    "<:crabevolvedtank:989951034132693044>", "<:crabtank:989949776927817738>",
    "<:crawlertank:990837535666212884>", "<:cyclopstank:989950970429595688>",
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
    "<:blacktreadtank:990837309446455356>", "<:goldcanontank:990837078340300820>",
    "<:goldbladetank:990837027136241694>", "<:goldcyclopstank:990837123919781898>",
    "<:whitedefaulttank:990837258359799838>", "<:bugtank:991755134193377361>",
    "<:logtank:992858914741825626>", "<:spidertank:992858923306598492>",
    "<:spiderevolvedtank:992858919141646397>", "<:burgerevolvedtank:997133766705291384>",
    "<:burgertank:997133760044744736>", "<:friestank:997133756085325885>",
    "<:hotdogtank:997133751727423498>"
]

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
    
def add_player_coin(player, name, coins):
    if type(player) is int:
        player_coins = db.get(str(player))
        if player_coins == None:
            db[str(player)] = {"name":name,"money":500, "inventory":{}}
        db[player]["money"] = db[player]["money"] + coins
        return db[str(player)]["money"]
    return 0

def convert_mention_to_id(mention):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))

def get_name_from_id(user_id):
    guild = discord.Object(id=962142361935314996)
    return guild.fetch_member(user_id)

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

@client.event
async def on_ready():
    '''Called when the discord client is ready.'''
    
    #Start up the 10 minute config refresher
    asyncio.create_task(refresh_config())

    for key in db.keys():
        print(str(key) + str(db[key]))
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
            add_player_coin(convert_mention_to_id(player_a),coin_num)
            add_player_coin(convert_mention_to_id(player_b),-coin_num)
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
    await interaction.response.send_message(str(interaction.user.mention) + " has " + str(add_player_coin(interaction.user.id,interaction.user.username,0)) + " <:coin:910247623787700264>")

@tree.command()
async def discord_coins_leaderboard(interaction: discord.Interaction):
   '''Return the discord coins leaderboard'''
    
#    await interaction.response.defer(ephemeral=False, thinking=True)
    
   test_keys = db
   rankdict = {}
   
   for key in test_keys.keys():
       rankdict[key] = test_keys[key]
   global sorted_rankdict
   sorted_rankdict = sorted(rankdict.items(), key=itemgetter(1), reverse=True)
   message = f"```\n{'Rank:':<5} {'Name:':<20} {'Coins:'}\n{'‾' * 35}\n"
   sorted_rankdict = sorted_rankdict[:10]
   for i in sorted_rankdict:
        message += f"{'#' + str(sorted_rankdict.index(i) + 1):<5} {i[0]:<20} {i[1]:>5,d} 🪙\n"
   message += "```"
   await interaction.channel.send(message)
   embed=discord.Embed(color=0xffd700, title="Discord Coins Leaderboard", description=message)
   await interaction.followup.send(embed=embed)


@tree.command()
async def random_tank(interaction: discord.Interaction):
    '''Get a random tank'''
    await interaction.response.send_message(random.choice(tanks))

@tree.command()
async def long(interaction: discord.Interaction, length: int, barrel: int = 1):
    '''Build your supercalifragilisticexpialidocious long tank equipped with as many barrels as you want!'''
    try:
        long_emoji = [
            "<:longtank_part1:991838180699541504>",
            "<:longtank_part2:991838184910626916>",
            "<:longtank_part3:991838189591470130>",
            "<:longtank_part4:991838192145793125>"
        ]
        if length < 0: length = 0
        if barrel < 0: barrel = 0
        if barrel > length: barrel = length
        
        def even_space(n, k):
            a = []
            for i in range(k): a.append(n // k)
            for i in range(n % k): a[i] += 1
            b = list(OrderedDict.fromkeys(a))
            global x, y
            x, y = b[0], b[1] if len(b) > 1 else ''
            for i in range(len(a)): a[i] = 'x' if a[i] == b[0] else 'y'
            s = ''.join(str(i) for i in a)
            return s
        
        def palindrome_check(str):
            return sum(map(lambda i: str.count(i) % 2, set(str))) <= 1
        
        def palindrome_rearrange(str):   
            hmap = defaultdict(int)
            for i in range(len(str)): hmap[str[i]] += 1
        
            odd_count = 0
        
            for x in hmap:
                if (hmap[x] % 2 != 0):
                    odd_count += 1
                    odd_char = x
        
            first_half = ''
            second_half = ''
        
            for x in sorted(hmap.keys()):
                s = (hmap[x] // 2) * x
                first_half = first_half + s
                second_half = s + second_half
        
            return (first_half + odd_char + second_half) if (odd_count == 1) else (first_half + second_half)

        even_space_encode = even_space(length - barrel, barrel + 1)
        even_space_encode_palindrome = palindrome_rearrange(even_space_encode) if palindrome_check(even_space_encode) else even_space_encode
        
        even_space_encode_palindrome_decode = []
        for i in even_space_encode_palindrome: even_space_encode_palindrome_decode.append(i)
        for i in range(len(even_space_encode_palindrome_decode)):
            even_space_encode_palindrome_decode[i] = x if even_space_encode_palindrome_decode[i] == 'x' else y
        
        output_middle = ""
        for i in range(len(even_space_encode_palindrome_decode) - 1):
            output_middle += (long_emoji[1] * even_space_encode_palindrome_decode[i] + long_emoji[2])
        output_middle += long_emoji[1] * even_space_encode_palindrome_decode[-1]
        msg = f"{long_emoji[0]}{output_middle}{long_emoji[3]}"
        await interaction.response.send_message(msg)
    except:
        await interaction.response.send_message("The tank is too long to build!")

@tree.command()
async def slot(interaction: discord.Interaction, bet: int):
    '''Play the slot machine game!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    coin = ["<:coin1:910247623787700264>", "<:coin2:991444836869754950>", "<:coin3:976289335844434000>", "<:coin4:976289358200049704>", "<:coin5:976288324266373130>"]
    
    # if bet > db["player_coin"]:
    #     await interaction.followup.send(embed=discord.Embed(
    #         color=discord.Color.red(),
    #         title="SLOT MACHINE :slot_machine:",
    #         description=f"You don't have enough {coin[0]}"))

    if bet <= 0:
    # elif bet <= 0:
        await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), title="SLOT MACHINE :slot_machine:", description=f"The minimum bet is 1 {coin[0]}"))

    else:
        coins_loop = "<a:coin_loop:992273503288037408>"
        multiplier2 = [1, 2, 3, 4, 8]
        multiplier3 = [4, 8, 12, 16, 32]
        events = {
            coin[0]: 12.5 / 26.25,
            coin[1]: 8 / 26.26,
            coin[2]: 3 / 26.26,
            coin[3]: 1.5 / 26.26,
            coin[4]: 1.25 / 26.25,
        }

        slots = []
        for i in range(3):
            slots.append(random.choices(population=list(events.keys()), weights=events.values())[0])

        slot_embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"**{'-' * 18}\n|{' {} |'.format(coins_loop) * 3}\n{'-' * 18}**")

        sent_embed = await interaction.followup.send(embed=slot_embed)
        current_slot_pics = [coins_loop] * 3
        for i in range(len(slots)):
            await asyncio.sleep(1.5)
            current_slot_pics[i] = slots[i]
            slot_results_str = f"**{'-' * 18}\n|"
            for thisSlot in current_slot_pics:
                slot_results_str += f" {thisSlot} |"
            new_slot_embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"{slot_results_str}\n{'-' * 18}**")
            await sent_embed.edit(embed=new_slot_embed)

        if slots[0] == slots[1]:
            if slots[1] == slots[2]:
                multiplier = multiplier3[coin.index(slots[0])]
            else:
                multiplier = multiplier2[coin.index(slots[0])]
            win = True
        else:
          win = False
        
        if win == True:
            res_2 = "-- **YOU WON** --"
            profit = bet * multiplier
            # db["player_coin"] += profit
        else:
            res_2 = "-- **YOU LOST** --"
            profit = -bet
            # db["player_coin"] -= bet

        # new_player_coin = db["player_coin"]

        embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"{slot_results_str}\n{'-' * 18}**\n{res_2}")
        embed.add_field(name="Bet", value=f"{bet} {coin[0]}", inline=True)
        embed.add_field(name="Profit/Loss", value=f"{profit} {coin[0]}" + (f" ({multiplier}x)" if win else ""), inline=True)
        embed.add_field(name="Balance", value=f"N.A. {coin[0]}", inline=True)
        embed.add_field(name="Pay Table", value=f"{'{}'.format(coin[4]) * 3} - 32x\n{'{}'.format(coin[3]) * 3} - 16x\n{'{}'.format(coin[2]) * 3} - 12x\n{'{}'.format(coin[1]) * 3} - 8x\n{'{}'.format(coin[4]) * 2}:grey_question: - 8x\n{'{}'.format(coin[0]) * 3} - 4x\n{'{}'.format(coin[3]) * 2}:grey_question: - 4x\n{'{}'.format(coin[2]) * 2}:grey_question: - 3x\n{'{}'.format(coin[1]) * 2}:grey_question: - 2x\n{'{}'.format(coin[0]) * 2}:grey_question: - 1x", inline=False)
        await sent_embed.edit(embed=embed)

@tree.command()
async def memory(interaction: discord.Interaction):
    '''Test your memory by matching 2 tanks!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    b = [":white_large_square:" for i in range(16)]
    c = ['a1', 'b1', 'c1', 'd1', 'a2', 'b2', 'c2', 'd2', 'a3', 'b3', 'c3', 'd3', 'a4', 'b4', 'c4', 'd4']
    a = random.sample(tanks, 8) * 2
    random.shuffle(a)
    board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
    answer = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {a[0]} {a[1]} {a[2]} {a[3]}\n:two: {a[4]} {a[5]} {a[6]} {a[7]}\n:three: {a[8]} {a[9]} {a[10]} {a[11]}\n:four: {a[12]} {a[13]} {a[14]} {a[15]}\n"

    def check(m):
        return (m.channel.id == interaction.channel.id and m.author == interaction.user)

    embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description="Test your memory by matching 2 tanks!")
    embed.add_field(name="Time", value="<80s\n<100s\n≥100s", inline=True)
    embed.add_field(name="Reward", value="20 <:coin1:910247623787700264>\n10 <:coin1:910247623787700264>\n5 <:coin1:910247623787700264>", inline=True)
    embed.add_field(name="Controls", value="Type `s` to start the game\nType `q` to quit the game", inline=False)
    message = await interaction.followup.send(embed=embed)

    global gamestart
    gamestart = False

    while gamestart == False:
        try:
            msg = await client.wait_for("message", check=check, timeout=15)
            if str(msg.content.lower()) == "q":
                embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description="You have quit the game")
                await message.edit(embed=embed)
                break
            if ((str(msg.content.lower()) == "s") or (str(msg.content.lower()) == "q")) == False:
                warn = await interaction.followup.send(":x: Invalid input has been entered :x:")
                await asyncio.sleep(2)
                await warn.delete()
            if str(msg.content.lower()) == "s":
                gamestart = True
                embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                await message.edit(embed=embed)
                start = timer()
        except asyncio.TimeoutError:
            embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description="You did not start the game")
            await message.edit(embed=embed)
            break

        pair = 0
        flag = False
        while gamestart == True:
            try:
                msg = await client.wait_for("message", check=check, timeout=15)
                if str(msg.content.lower()) == "q":
                    board = answer
                    embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description=f"{board}\nYou have quit the game")
                    await message.edit(embed=embed)
                    break
                if (str(msg.content.lower()) in c) == False:
                    warn2 = await interaction.followup.send(":x: Invalid coordinate has been entered :x:")
                    await asyncio.sleep(2)
                    await warn2.delete()
                elif b[c.index(str(msg.content.lower()))] == ":white_large_square:":
                    if flag == False:
                        x = c.index(str(msg.content.lower()))
                        b[x] = a[x]
                        flag = not flag
                        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                        embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                        embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                        await message.edit(embed=embed)
                    else:
                        y = c.index(str(msg.content.lower()))
                        b[y] = a[y]
                        flag = not flag
                        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                        embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                        embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                        await message.edit(embed=embed)
                        await asyncio.sleep(1)
                        if a[x] == a[y]:
                            pair += 1
                        else:
                            b[x] = ":white_large_square:"
                            b[y] = ":white_large_square:"
                            board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                            embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                            embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                            await message.edit(embed=embed)
                    if pair == 8:
                        end = timer()
                        time_diff = end - start
                        if time_diff < 80:
                            reward = 20
                        elif 80 <= time_diff < 100:
                            reward = 10
                        else:
                            reward = 5
                        gamestart = False
                        # db["player_coin"] += reward
                        # new_player_coin = db["player_coin"]
                        embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=f"{board}\n:tada: **YOU WON** :tada:")
                        embed.add_field(name="Time", value=f"{time_diff:.2f}s", inline=True)
                        embed.add_field(name="Reward", value=f"{reward} <:coin1:910247623787700264>", inline=True)
                        embed.add_field(name="Balance", value=f"N.A. <:coin1:910247623787700264>", inline=True)
                        await message.edit(embed=embed)
                        break
                    await message.edit(embed=embed)
                else:
                    warn3 = await interaction.followup.send(":x: The card has already been flipped :x:")
                    await asyncio.sleep(2)
                    await warn3.delete()
            except asyncio.TimeoutError:
                board = answer
                embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description=f"{board}\nThe game has timed out :hourglass:")
                await message.edit(embed=embed)
                break
        break

# @tree.command()
# async def update_players_database(interaction: discord.Interaction):
#     '''Change from user mention to dict'''
#     for key in db.keys():
#         user_id = convert_mention_to_id(key)
#         db[user_id] = {"name":client.get_user(user_id),"money":db[key], "inventory":{}}
#         db.pop(key)
#     print(db.keys())
#     await interaction.response.send_message("DONE =)")

@tree.command()
async def get_crate_stats(interaction: discord.Interaction, one_star: int, two_star: int):
    '''Optimize the use of in game crates and Estimate the amount of coins'''
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

