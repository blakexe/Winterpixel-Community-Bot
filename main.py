import random
import aiohttp
import discord
import json
import asyncio
import typing
import os
import io
import datetime
import time
import re
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from collections import defaultdict, OrderedDict, Counter
from operator import itemgetter
from statistics import mean
from timeit import default_timer as timer
from mediawiki import MediaWiki
from fandom import set_wiki, page
from replit import db
from discord import app_commands
from rocketbot_client import RocketBotClient
from moonrock_client import MoonRockClient

db['discord_coins'] = {
    '287357374996545536': {'name': 'minajidas', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '795760729331728464': {'name': 'noobfox unnoob?', 'coins': 549, 'coins_change': 0, 'inventory': {}},
    '953894954307047444': {'name': '! ! ! ! Meme', 'coins': 701, 'coins_change': 0, 'inventory': {}},
    '348667586893971457': {'name': '6721', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '565871617134034965': {'name': 'cant_logic', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '828024836101111839': {'name': 'Unknown User', 'coins': 703, 'coins_change': 0, 'inventory': {}},
    '970784448633258054': {'name': 'TaNk8k', 'coins': 707, 'coins_change': 0, 'inventory': {}},
    '890305108787744838': {'name': 'bireme(tu madre es gorda)', 'coins': 476, 'coins_change': 0, 'inventory': {}},
    '978010453299068958': {'name': 'Sir Canis IV (ʜᴇ/ʜɪᴍ/ʜɪs)', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '741161476353425420': {'name': 'Unknown User', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '917526093165113364': {'name': 'т¥ɧ๏๏Ꮑ', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '667898007592894482': {'name': 'Noahbear23', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '707226035652919336': {'name': 'mininuke🗿', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '639615677262462976': {'name': 'Mirio🗿', 'coins': 504, 'coins_change': 0, 'inventory': {}},
    '908108270638616586': {'name': 'Unknown User', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '835208786909462588': {'name': 'Unknown User', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '217322331385757697': {'name': 'average lighthouse', 'coins': 461, 'coins_change': 0, 'inventory': {}},
    '799355820722225194': {'name': '!Nightdrifter🗿', 'coins': 1247, 'coins_change': 0, 'inventory': {}},
    '507965365930950657': {'name': 'dev', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '152080881220059136': {'name': 'brianflakes', 'coins': 519, 'coins_change': 0, 'inventory': {}},
    '92400886776627200': {'name': 'JL', 'coins': 266, 'coins_change': 0, 'inventory': {}},
    '771472652610174987': {'name': 'What', 'coins': 449, 'coins_change': 0, 'inventory': {}},
    '733827112175140945': {'name': '(Moyai clan) Rebecca 🗿', 'coins': 462, 'coins_change': 0, 'inventory': {}},
    '887318763874189313': {'name': '[DC][MC] BEAST', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '552064129872166912': {'name': '•𝓩ǝ𝔯๏•🗿', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '244935915670077441': {'name': 'Deej Lile Babe', 'coins': 419, 'coins_change': 0, 'inventory': {}},
    '668153108592853006': {'name': 'Guest69', 'coins': 10, 'coins_change': 0, 'inventory': {}},
    '548992701169926161': {'name': 'Unknown User', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '974388748273979392': {'name': 'Ein Purzel', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '843576984621416530': {'name': '(Moyai Clan) PepperBoi🗿', 'coins': 1340, 'coins_change': 0, 'inventory': {}},
    '958845970718785576': {'name': '! ! ! ! BOMB [PRM]', 'coins': 248, 'coins_change': 0, 'inventory': {}},
    '617808605424386057': {'name': 'Arrow', 'coins': 345, 'coins_change': 0, 'inventory': {}},
    '899272561148448828': {'name': '[Tax Evasion] Gr8', 'coins': 721, 'coins_change': 0, 'inventory': {}},
    '933484238219653241': {'name': '[PRM] jellyfrog', 'coins': 291, 'coins_change': 0, 'inventory': {}},
    '610369943967629340': {'name': 'gber 🗿', 'coins': 597, 'coins_change': 0, 'inventory': {}},
    '746054282121576500': {'name': '!odssa (', 'coins': 567, 'coins_change': 0, 'inventory': {}},
    '381074897083826176': {'name': 'Blaki🗿', 'coins': 518, 'coins_change': 0, 'inventory': {}},
    '849305162098278451': {'name': 'Maxarian', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '917204030198022154': {'name': '!armadillo71', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '956571878682677268': {'name': 'Boop', 'coins': 1131, 'coins_change': 0, 'inventory': {}},
    '439869920378093568': {'name': 'Clement', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '972224178692423740': {'name': 'v1b3z', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '958078466971029544': {'name': '(Moyai Clan) Brawl Stars 🗿', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '988795020188483635': {'name': 'RODENTS', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '942236747226574869': {'name': 'Zeek', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '953365001245171794': {'name': 'asia1752', 'coins': -218, 'coins_change': 0, 'inventory': {}},
    '255360946573279233': {'name': 'Unknown User', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '958535660531245106': {'name': 'oofmania', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '660284600400216064': {'name': 'Nowisk', 'coins': 679, 'coins_change': 0, 'inventory': {}},
    '652144896077070366': {'name': 'Evvis', 'coins': 449, 'coins_change': 0, 'inventory': {}},
    '782302769452941333': {'name': 'ultra-lion🗿', 'coins': 524, 'coins_change': 0, 'inventory': {}},
    '898241469788356618': {'name': 'Unknown User', 'coins': 500, 'coins_change': 0, 'inventory': {}},
    '774290172040577034': {'name': '(Moyai Clan) Spearfire81 🗿', 'coins': 766, 'coins_change': 0, 'inventory': {}},
    '947338408429252638': {'name': 'Unknown User', 'coins': 500, 'coins_change': 0, 'inventory': {}}
}

# Attempt to retrieve enviroment from environment.json
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

# Get sensitive info
try:
    discord_token = os.environ['discord_token']
    rocketbot_user = os.environ['rocketbot_username']
    rocketbot_pass = os.environ['rocketbot_password']
except KeyError:
    print("ERROR: An environment value was not found. Please make sure your environment.json has all the right info or that you have correctly preloaded values into your environment.")
    os._exit(1)

# Set up discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
server_config = {}
server_config_2 = {}

# Initialize rocketbot client
rocketbot_client = RocketBotClient(rocketbot_user, rocketbot_pass)

# Initialize moonrock client
moonrock_client = MoonRockClient(rocketbot_user, rocketbot_pass)

players = []
bots = []
playing = False

# Set targeted fandom site's api for fandom command
set_wiki("rocketbotroyale")
rocketbotroyale = MediaWiki(url='https://rocketbotroyale.fandom.com/api.php')

# List contains all tank emojis for random_tank and memory command
tanks = ['<:pumpkin_tank:1022568065034104936>', '<a:pumpkin_evolved_tank_a:1022572757860499486>', '<:eyeball_tank:1022568661745143908>', '<a:skull_tank_a:1022574941591306362>', '<:snowman_tank:1012941920844132362>', '<:snowman_evolved_tank:1012941924094713917>', '<:snowmobile_tank:1012941917337698375>', '<:icy_tank:1012941914254876794>', '<:brain_bot_tank:1006531910224322630>', '<:mine_bot_tank:1006532474945417216>', '<:bot_tank:917467970182189056>', '<:default_tank:996465659812774040>', '<:beta_tank:997947350943277106>', '<:canon_tank:997951207840686162>', '<:hot_dog_tank:997955038435614934>', '<a:wave_tank_a:1001203703325397033>', '<:zig_tank:997954180717215975>', '<:blade_tank:997947874715385856>', '<:buggy_tank:997948966933119016>', '<:burger_evolved_tank:997950412348989562>', '<:burger_tank:997950506976694302>', '<:catapult_evolved_tank:997951715284365323>', '<:catapult_tank:997951809282912346>', '<a:crab_evolved_tank_a:1001203931713654864>', '<a:crab_tank_a:1001203874469793822>', '<:cyclops_tank:997952308333793322>', '<:diamond_tank:997952379595010048>', '<a:dozer_evolved_tank_a:1001204001053876374>',
         '<:dozer_tank:997952516501278760>', '<:fork_tank:997952581408129084>', '<:fries_tank:997952688656494672>', '<:gears_tank:997952760127434782>', '<:hay_tank:997952813386715148>', '<:hollow_tank:997952878142562384>', '<:medic_tank:997953168673619978>', '<:mixer_tank:997953233098113054>', '<:pagliacci_tank:997953348097560628>', '<:pail_tank:997953413717438575>', '<a:pistons_tank_a:1001208481300369608>', '<a:reactor_tank_a:1024935111461969990>', '<a:spider_evolved_tank_a:1001204256193396856>', '<a:spider_tank_a:1001204193887002704>', '<:spike_tank:997953736041308280>', '<:square_tank:997953791217377381>', '<:trap_tank:997953904610381834>', '<:tread_tank:997953970213494905>', '<:tub_tank:997954029902626886>', '<:tubdown_tank:997954078535598270>', '<:concave_tank:997951897749176450>', '<:crawler_tank:997952124279324753>', '<:log_tank:997953009910829198>', '<:long_tank:997953087006330971>', '<a:UFO_evolved_tank_a:1012268475626033174>', '<a:UFO_tank_a:1012268306482343936>', '<a:miner_tank_a:1003099245777276952>', '<:rover_tank:1003014762327716042>', '<a:bug_tank_a:1001203807893590168>', '<:moai_tank:1006528445355917394>']

os.system('clear')


def season_info(season):
    season_durations = []
    season_start_numbers = []
    season_start_timestamps = []
    for key in server_config['season_definitions']:
        season_durations.append(key['season_duration'])
        season_start_numbers.append(key['season_start_number'])
        season_start_timestamps.append(key['season_start_timestamp'])

    season_index = np.searchsorted(season_start_numbers, season+1)-1

    season_start_timestamp = season_start_timestamps[season_index] + (
        season - season_start_numbers[season_index]) * season_durations[season_index]
    season_start = f"{datetime.datetime.utcfromtimestamp(season_start_timestamp):%Y-%m-%d %H:%M:%S} UTC"

    season_end_timestamp = season_start_timestamp + \
        season_durations[season_index]
    season_end = f"{datetime.datetime.utcfromtimestamp(season_end_timestamp):%Y-%m-%d %H:%M:%S} UTC"

    season_duration = season_durations[season_index]
    season_days = f"{season_duration/(60*60*24):.0f} days"

    current_timestamp = time.time()
    if current_timestamp > season_end_timestamp:
        status = "\u001b[2;31mEnded\u001b[0m"
    else:
        status = f"\u001b[2;32mIn progress\u001b[0m ({((current_timestamp - season_start_timestamp)/season_duration)*100:.0f} %)"

    if season == curr_season:
        season_difference = (current_timestamp -
                             season_start_timestamp) / season_duration
        season_seconds_remaining = (
            ceil(season_difference) - season_difference) * season_duration
        day = season_seconds_remaining // (24 * 3600)
        hour = season_seconds_remaining % (24 * 3600) // 3600
        minute = season_seconds_remaining % (24 * 3600) % 3600 // 60
        second = season_seconds_remaining % (24 * 3600) % 3600 % 60
        time_remaining = f"{int(day)}d {int(hour)}h {int(minute)}m {int(second)}s"
    else:
        time_remaining = ""

    all_season_info = [season_start, season_end,
                       season_days, status, time_remaining]
    return all_season_info


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

    name = random.choice(adjective).capitalize() + \
        random.choice(noun).capitalize()

    random_number = random.choice([True, False])

    if random_number:
        name += f"{random.randint(0, 9)}{random.randint(0, 9)}00"

    return name


def change_player_coin(id, name, coins, request=False):
    if id in db['discord_coins']:  # Old id
        db['discord_coins'][id]['name'] = name  # Update nickname
    else:  # New id
        db['discord_coins'][id] = {  # New record
            'name': name, 'coins': 0, 'coins_change': 0, 'inventory': {}}
    db['discord_coins'][id]['coins'] += coins
    db['discord_coins'][id]['coins_change'] += coins
    if request == True:
        return db['discord_coins'][id]['coins']


def convert_mention_to_id(mention):
    id = mention[2:-1]
    if id.startswith('!'):
        id = id[1:]
    return id


async def refresh_config():
    '''Refresh game configuration every 10 minutes'''
    global server_config

    while True:
        response = await rocketbot_client.get_config()
        server_config = json.loads(response['payload'])

        # Remove past season keys
        global curr_season
        curr_season = server_config['season']
        for i in db.prefix("tankkings"):
            if str(curr_season) not in i:
                del db[i]

        await asyncio.sleep(600)


async def refresh_config_2():
    '''Refresh game configuration every 10 minutes'''
    global server_config_2

    while True:
        response = await moonrock_client.get_config()
        server_config_2 = json.loads(response['payload'])

        # Remove past season keys
        global curr_season_2
        curr_season_2 = server_config_2['season']
        for i in db.prefix("trophies"):
            if str(curr_season_2) not in i:
                del db[i]

        await asyncio.sleep(600)


@client.event
async def on_message(message: discord.message):
    if "moyai" in message.content.lower() or "🗿" in message.content.lower() or "moai" in message.content.lower():
        await message.add_reaction("🗿")
    if "!idea" in message.content.lower():
        await message.add_reaction("<:upvote:910250647264329728>")
        await message.add_reaction("<:downvote:910250215217459281>")
    # (caps with spaces >= 10) or (repeated character or number >=10)
    if bool(re.search(r"\w*[A-Z ]{10}", message.content)) or bool(re.search(r"(?:([a-zA-Z0-9])\1{9,})", message.content)):
        await message.reply("Calm down!")


@client.event
async def on_ready():
    '''Called when the discord client is ready.'''

    # Start up the 10 minute config refresher
    asyncio.create_task(refresh_config())
    asyncio.create_task(refresh_config_2())

    # Check keys in repl.it's database
    matches_rbr = db.prefix("tankkings")
    matches_mm = db.prefix("trophies")
    print(matches_rbr)
    print(matches_mm)

    for key in db.keys():
        if key not in matches_rbr and key not in matches_mm:
            print(key)

    print("Winterpixel community bot is ready.")


@tree.command()
async def fix(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=False, thinking=True)

    name_id = dict()
    for id in db['archive']:
        try:  # User in server
            user_object = await interaction.guild.query_members(user_ids=[id])
            if user_object[0].nick == None:  # No nickname is found
                name = str(user_object[0])[:-5]  # Use username
            else:
                name = user_object[0].nick  # Use nickname
            name_id[id] = name
            print(id, name)
        except:  # User not in server
            print(id)

    await interaction.followup.send("Done")
    print(name_id, len(name_id))


@tree.command()
@app_commands.describe(
    mode='Leaderboard by trophies or points',
    changes='Only available for Top 50 records of current season, changes since last command used',
    season='Trophies: Season 10 or later / Points: Season 0 or later, default current'
)
async def leaderboard_rocket_bot_royale(interaction: discord.Interaction, mode: typing.Literal['Trophies', 'Points'], changes: typing.Literal['Shown', 'Hidden'], season: int = -1):
    '''Return the specified season leaderboard of Rocket Bot Royale (by trophies/points), default current'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in ["◀️", "▶️", "⏪", "⏹️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    # Reassign season if unreasonable
    if mode == "Trophies":
        if season < 10 or season > curr_season:
            season = curr_season
    elif mode == "Points":
        if season < 0 or season > curr_season:
            season = curr_season

    # Season Info
    global season_info_2
    season_info_2 = f"📓 ***Season Info***:\n```ansi\n{'Start: ':>10}{season_info(season)[0]}\n{'End: ':>10}{season_info(season)[1]}\n{'Duration: ':>10}{season_info(season)[2]}\n{'Status: ':>10}{season_info(season)[3]}\n" + (
        f"{'Ends in: ':>10}{season_info(season)[4]}\n" if season == curr_season else "") + "```"

    # Hide changes for past seasons
    if season < curr_season:
        changes = "Hidden"

    # Get leaderboard info
    if changes == "Shown":
        limit = 100
    elif changes == "Hidden":
        limit = 25

    if mode == "Trophies":
        response = await rocketbot_client.query_leaderboard(
            season, "tankkings_trophies", limit)
    elif mode == "Points":
        response = await rocketbot_client.query_leaderboard(
            season, "tankkings_points", limit)
    records = json.loads(response['payload'])['records']
    start = records[0]['rank']
    end = records[len(records)-1]['rank']
    cursor_dict = dict()
    cursor_dict[1] = ""

    try:
        cursor_dict[2] = json.loads(response['payload'])['next_cursor']
        next_cursor = True
    except:
        next_cursor = False

    if changes == "Shown":
        # Add to repl.it's database for new keys
        new_key_flag = False
        if f"tankkings_{mode.lower()}_{season}" not in db.keys():
            value = dict()
            for record in records:
                value[record['owner_id']] = {
                    'rank': record['rank'], 'score': record['score']}
            value['last_update_time'] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record['leaderboard_id']] = value
            new_key_flag = True

        if mode == "Trophies":  # By Tropihes
            split = []
            tier = []
            for i in range(5):
                split.append(server_config['trophy_tiers'][i]['maximum_rank'])
                tier.append(server_config['trophy_tiers'][i]['name'].upper())
            tier_color_code = ["35", "36", "33", "34", "31"]

            # Using f-string spacing to pretty print the leaderboard labels (bold)
            message = ""
            label = f"{season_info_2}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'—' * 45}\n"

            # Using f-string spacing to pretty print the leaderboard
            if len(records) < 50:  # Prevent index out of range error
                records_range = len(records)
            else:
                records_range = 50

            for i in range(records_range):
                # Determine which tier the player belongs to
                tier_index = np.searchsorted(split, records[i]['rank'])

                # Rank difference
                try:
                    rank_diff = records[i]['rank'] - \
                        db[records[i]['leaderboard_id']
                           ][records[i]['owner_id']]['rank']
                    if rank_diff < 0:
                        rank_diff_2 = f"\u001b[2;32m▲{abs(rank_diff):<3}\u001b[0m"
                    elif rank_diff > 0:
                        rank_diff_2 = f"\u001b[2;31m▼{abs(rank_diff):<3}\u001b[0m"
                    else:
                        rank_diff_2 = f"{'-':^4}"
                except:
                    rank_diff_2 = f"{'':4}"  # Not found in repl.it's database

                # Rank (bold)
                message += f"{rank_diff_2}\u001b[1;{tier_color_code[tier_index]}m{'#' + str(records[i]['rank']):<5}\u001b[0m "

                # Name and color for players with season pass
                message += ("\u001b[1;33m" if records[i]['metadata']['has_season_pass'] else "") + f"{records[i]['username']:<20}" + (
                    "\u001b[0m " if records[i]['metadata']['has_season_pass'] else " ")

                # Trophies difference
                try:
                    trophies_diff = records[i]['score'] - \
                        db[records[i]['leaderboard_id']
                           ][records[i]['owner_id']]['score']
                    if trophies_diff < 0:
                        trophies_diff_2 = f"\u001b[2;31m-{abs(trophies_diff):<4}\u001b[0m"
                    elif trophies_diff > 0:
                        trophies_diff_2 = f"\u001b[2;32m+{abs(trophies_diff):<4}\u001b[0m"
                    else:
                        trophies_diff_2 = f"{'-':^5}"
                except:
                    # Not found in repl.it's database
                    trophies_diff_2 = f"{'':<5}"

                # Trophies
                message += f"{'🏆' + '{:<6,.0f}'.format(records[i]['score'])}{trophies_diff_2}\n"

                # Tier separators (bold)
                if (records[i]['rank'] in split and records[i]['rank'] % 25 != 0):
                    tier_name_with_space = " "+tier[tier_index]+" "
                    message += f"\u001b[1;{tier_color_code[tier_index]}m{tier_name_with_space.center(45, '─')}\u001b[0m\n"

        elif mode == "Points":  # By Points
            # Using f-string spacing to pretty print the leaderboard labels (bold)
            message = ""
            label = f"{season_info_2}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {'Points:'}\u001b[0m\n{'—' * 47}\n"

            # Using f-string spacing to pretty print the leaderboard
            if len(records) < 50:  # Prevent index out of range error
                records_range = len(records)
            else:
                records_range = 50

            for i in range(records_range):
                # Rank difference
                try:
                    rank_diff = records[i]['rank'] - db[records[i]
                                                        ['leaderboard_id']][records[i]['owner_id']]['rank']
                    if rank_diff < 0:
                        rank_diff_2 = f"\u001b[2;32m▲{abs(rank_diff):<3}\u001b[0m"
                    elif rank_diff > 0:
                        rank_diff_2 = f"\u001b[2;31m▼{abs(rank_diff):<3}\u001b[0m"
                    else:
                        rank_diff_2 = f"{'-':^4}"
                except:
                    rank_diff_2 = f"{'':<4}"  # Not found in repl.it's database

                # Rank (bold)
                message += f"{rank_diff_2}\u001b[1m{'#' + str(records[i]['rank']):<5}\u001b[0m "

                # Name and color for players with season pass
                try:  # For seasons without 'has season pass' key
                    message += (
                        "\u001b[1;33m" if records[i]['metadata']['has_season_pass']
                        else "") + f"{records[i]['username']:<20}" + (
                            "\u001b[0m " if records[i]['metadata']['has_season_pass']
                            else " ")
                except:
                    message += f"{records[i]['username']:<20} "  # Name only

                # Points difference
                try:
                    points_diff = records[i]['score'] - db[records[i]
                                                           ['leaderboard_id']][records[i]['owner_id']]['score']
                    if points_diff > 0:
                        points_diff_2 = f"\u001b[2;32m+{abs(points_diff):<5}\u001b[0m"
                    else:
                        points_diff_2 = f"{'-':^6}"
                except:
                    # Not found ind repl.it's database
                    points_diff_2 = f"{'':<6}"

                # Points
                message += f"{'🧊' + '{:<8,.0f}'.format(records[i]['score'])}{points_diff_2}\n"

        # Split message
        cannot_split = False  # Prevent index out of range error
        split_line_number = 26 if mode == "Trophies" else 24  # Evenly split message
        try:  # In case there are not enough records
            message1 = message[:[m.start() for m in re.finditer(r"\n", message)]
                               [split_line_number]]
            message2 = message[([m.start() for m in re.finditer(r"\n", message)]
                                [split_line_number])+1:] + ("\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n" if mode == "Trophies" else "")+"```"
        except:
            cannot_split = True

        # Send
        if cannot_split == False:
            cur_page = 1
            embed_init = discord.Embed(
                title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=label+message1+("\n\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n" if mode == "Trophies" else "")+"```")
            embed_init.set_footer(
                text=f"Page 1/2:  1 to 25 | Changes since {db[f'tankkings_{mode.lower()}_{season}']['last_update_time']}")
            msg = await interaction.followup.send(embed=embed_init)
            msg2 = await interaction.followup.send(embed=discord.Embed(description="To be edited..."))

            for reaction_emoji in ["◀️", "▶️", "⏹️"]:
                await msg.add_reaction(reaction_emoji)

            while True:
                try:
                    reaction, user = await client.wait_for("reaction_add", timeout=10, check=check)
                    # Waiting for a reaction to be added - times out after 10 seconds

                    if str(reaction.emoji) == "▶️" and cur_page == 1:  # Go to Page 2
                        cur_page += 1
                        embed_first = discord.Embed(
                            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description="\n"+label+message2)
                        embed_first.set_footer(
                            text=f"Page 2/2: 26 to 50 | Changes since {db[f'tankkings_{mode.lower()}_{season}']['last_update_time']}")
                        await msg.edit(embed=embed_first)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page == 2:  # Go to Page 1
                        cur_page -= 1
                        embed_second = discord.Embed(
                            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description="\n"+label+message1+("\n\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n" if mode == "Trophies" else "")+"```")
                        embed_second.set_footer(
                            text=f"Page 1/2:  1 to 25 | Changes since {db[f'tankkings_{mode.lower()}_{season}']['last_update_time']}")
                        await msg.edit(embed=embed_second)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                        await msg.edit(embed=discord.Embed(
                            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=label+message1+"```"))
                        embed_second_timeout = discord.Embed(
                            description="```ansi\n"+message2)
                        embed_second_timeout.set_footer(
                            text=f"Changes since {db[f'tankkings_{mode.lower()}_{season}']['last_update_time']}")
                        await msg2.edit(embed=embed_second_timeout)
                        await msg.clear_reactions()
                        break

                    else:
                        await msg.remove_reaction(reaction, user)
                        # Removes reactions if invalid
                except asyncio.TimeoutError:
                    await msg.edit(embed=discord.Embed(
                        title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=label+message1+"```"))
                    embed_second_timeout = discord.Embed(
                        description="```ansi\n"+message2)
                    embed_second_timeout.set_footer(
                        text=f"Changes since {db[f'tankkings_{mode.lower()}_{season}']['last_update_time']}")
                    await msg2.edit(embed=embed_second_timeout)
                    await msg.clear_reactions()
                    break
                    # Ending the loop if user doesn't react after 10 seconds
        elif cannot_split == True:  # Send in 1 message if there are too little records
            await interaction.followup.send(embed=discord.Embed(
                title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=label+message+"```"))

        # Update to repl.it's database for old keys
        if (f"tankkings_{mode.lower()}_{season}" in db.keys()) and (new_key_flag == False):
            value = dict()
            for record in records:
                value[record['owner_id']] = {
                    'rank': record['rank'], 'score': record['score']}
            value['last_update_time'] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record['leaderboard_id']] = value

    elif changes == "Hidden":
        if mode == "Trophies":  # By Tropihes
            def trophies_hidden(last=True, fifty=False):
                split = []
                tier = []
                for i in range(12):
                    split.append(
                        server_config['trophy_tiers'][i]['maximum_rank'])
                    tier.append(
                        server_config['trophy_tiers'][i]['name'].upper())
                tier_color_code = ["35", "36", "33", "34", "31",
                                   "32", "35", "31", "33", "30", "37", "37"]

                # Using f-string spacing to pretty print the leaderboard labels (bold)
                message = f"{season_info_2}\n📊 ***Leaderboard***:```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'─' * 37}\n"

                # Using f-string spacing to pretty print the leaderboard
                for record in records:
                    # Determine which tier the player belongs to
                    tier_index = np.searchsorted(split, record['rank'])

                    # Rank (bold)
                    message += f"\u001b[1;{tier_color_code[tier_index]}m{'#' + str(record['rank']):<5}\u001b[0m "

                    # Name and color for players with season pass
                    try:  # For seasons without 'has season pass' key
                        message += ("\u001b[1;33m" if record['metadata']['has_season_pass'] else "") + f"{record['username']:<20}" + (
                            "\u001b[0m " if record['metadata']['has_season_pass'] else " ")
                    except:
                        message += f"{record['username']:<20} "  # Name only

                    # Trophies
                    message += f"{'🏆' + '{:,}'.format(record['score'])}\n"

                    # Tier separators (bold)
                    if (record['rank'] in split and record['rank'] % 25 != 0) or (last == True and record['rank'] % 25 == 0) or (len(records) != 25 and record['rank'] % 25 == len(records)):
                        tier_name_with_space = " "+tier[tier_index]+" "
                        message += f"\u001b[1;{tier_color_code[tier_index]}m{tier_name_with_space.center(37, '─')}\u001b[0m\n"

                if fifty == True:
                    message += "\u001b[1;31m──────────────── RUBY ───────────────\u001b[0m\n"
                message += "```"
                return message

            message = f"```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'─' * 37}\n"

        elif mode == "Points":  # By Points
            def points_hidden():
                # Using f-string spacing to pretty print the leaderboard labels (bold)
                message = (f"{season_info_2}\n📊 ***Leaderboard***:" if season != 0 else "") + \
                    f"```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {'Points:'}\u001b[0m\n{'─' * 37}\n"

                # Using f-string spacing to pretty print the leaderboard
                for record in records:
                    # Rank (bold)
                    message += f"\u001b[1m{'#' + str(record['rank']):<5}\u001b[0m "

                    # Name and color for players with season pass
                    try:  # For seasons without 'has season pass' key
                        message += ("\u001b[1;33m" if record['metadata']['has_season_pass'] else "") + f"{record['username']:<20}" + (
                            "\u001b[0m " if record['metadata']['has_season_pass'] else " ")
                    except:
                        message += f"{record['username']:<20} "  # Name only

                    # Points
                    message += f"{'🧊' + '{:,}'.format(record['score'])}\n"
                message += "```"
                return message

        # Send
        cur_page = 1
        embed_init = discord.Embed(title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=(
            points_hidden() if mode == "Points" else trophies_hidden()))
        embed_init.set_footer(
            text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
        msg = await interaction.followup.send(embed=embed_init)

        for reaction_emoji in ["◀️", "▶️", "⏪", "⏹️"]:
            await msg.add_reaction(reaction_emoji)

        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=10, check=check)
                # Waiting for a reaction to be added - times out after 10 seconds

                if str(reaction.emoji) == "▶️" and next_cursor != False:  # Next page
                    cur_page += 1
                    response = await rocketbot_client.query_leaderboard(
                        season, ("tankkings_points" if mode == "Points" else "tankkings_trophies"), 25, cursor_dict[cur_page])
                    records = json.loads(response['payload'])['records']
                    start = records[0]['rank']
                    end = records[len(records)-1]['rank']
                    try:
                        cursor_dict[cur_page +
                                    1] = json.loads(response['payload'])['next_cursor']
                    except:
                        next_cursor = False  # Does not exist
                    embed_next = discord.Embed(title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=(
                        points_hidden() if mode == "Points" else trophies_hidden()))
                    embed_next.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
                    await msg.edit(embed=embed_next)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                    cur_page -= 1
                    response = await rocketbot_client.query_leaderboard(
                        season, ("tankkings_points" if mode == "Points" else "tankkings_trophies"), 25, cursor_dict[cur_page])
                    records = json.loads(response['payload'])['records']
                    start = records[0]['rank']
                    end = records[len(records)-1]['rank']
                    embed_prev = discord.Embed(title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=(
                        points_hidden() if mode == "Points" else trophies_hidden()))
                    embed_prev.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
                    await msg.edit(embed=embed_prev)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                    cur_page = 1
                    next_cursor = True
                    response = await rocketbot_client.query_leaderboard(season, ("tankkings_points" if mode == "Points" else "tankkings_trophies"), 25, cursor_dict[cur_page])
                    records = json.loads(response['payload'])['records']
                    start = records[0]['rank']
                    end = records[len(records)-1]['rank']
                    embed_first = discord.Embed(title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=(
                        points_hidden() if mode == "Points" else trophies_hidden()))
                    embed_first.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
                    await msg.edit(embed=embed_first)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                    response = await rocketbot_client.query_leaderboard(
                        season, ("tankkings_points" if mode == "Points" else "tankkings_trophies"), 50)
                    records = json.loads(response['payload'])['records']
                    await msg.edit(embed=discord.Embed(title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=(points_hidden() if mode == "Points" else trophies_hidden(False, True))))
                    await msg.clear_reactions()
                    break

                else:
                    await msg.remove_reaction(reaction, user)
                    # Removes reactions if invalid
            except asyncio.TimeoutError:
                response = await rocketbot_client.query_leaderboard(
                    season, ("tankkings_points" if mode == "Points" else "tankkings_trophies"), 50)
                records = json.loads(response['payload'])['records']
                await msg.edit(embed=discord.Embed(title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode}):", description=(points_hidden() if mode == "Points" else trophies_hidden(False, True))))
                await msg.clear_reactions()
                break
                # Ending the loop if user doesn't react after 10 seconds


@tree.command()
@app_commands.describe(
    changes='Only available for Top 50 records of current season, changes since last command used',
    season='Beta Season 14 or later'
)
async def leaderboard_moonrock_miners(interaction: discord.Interaction, changes: typing.Literal['Shown', 'Hidden'], season: int = -1):
    '''Return the specified season leaderboard of Moonrock Miners, default current'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in ["◀️", "▶️", "⏪", "⏹️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    # Reassign season if unreasonable
    if season < 14 or season > curr_season_2:
        season = curr_season_2

    # Hide changes for past seasons
    if season < curr_season_2:
        changes = "Hidden"

    # Get leaderboard info
    if changes == "Shown":
        limit = 100
    elif changes == "Hidden":
        limit = 25

    response = await moonrock_client.query_leaderboard(season, "trophies", limit)
    records = json.loads(response['payload'])['records']
    start = records[0]['rank']
    end = records[len(records)-1]['rank']
    cursor_dict = dict()
    cursor_dict[1] = ""

    try:
        cursor_dict[2] = json.loads(response['payload'])['next_cursor']
        next_cursor = True
    except:
        next_cursor = False

    if changes == "Shown":
        # Add to replit's database for new keys
        new_key_flag = False
        if f"trophies_{season}" not in db.keys():
            value = dict()
            for record in records:
                value[record['owner_id']] = {
                    'rank': record['rank'], 'score': record['score']}
            value['last_update_time'] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record['leaderboard_id']] = value
            new_key_flag = True

        # Using f-string spacing to pretty print the leaderboard labels (bold)
        message = ""
        label = f"```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'—' * 45}\n"

        # Using f-string spacing to pretty print the leaderboard
        if len(records) < 50:  # Prevent index out of range error
            records_range = len(records)
        else:
            records_range = 50

        for i in range(records_range):
            # Rank difference
            try:
                rank_diff = records[i]['rank'] - db[records[i]
                                                    ['leaderboard_id']][records[i]['owner_id']]['rank']
                if rank_diff < 0:
                    rank_diff_2 = f"\u001b[2;32m▲{abs(rank_diff):<3}\u001b[0m"
                elif rank_diff > 0:
                    rank_diff_2 = f"\u001b[2;31m▼{abs(rank_diff):<3}\u001b[0m"
                else:
                    rank_diff_2 = f"{'-':^4}"
            except:
                rank_diff_2 = f"{'':<4}"  # Not found ind repl.it's database

            # Rank (bold)
            message += f"{rank_diff_2}\u001b[1m{'#' + str(records[i]['rank']):<5}\u001b[0m "

            # Name
            message += f"{records[i]['username']:<20} "

            # Trophies difference
            try:
                trophies_diff = records[i]['score'] - db[records[i]
                                                         ['leaderboard_id']][records[i]['owner_id']]['score']
                if trophies_diff < 0:
                    trophies_diff_2 = f"\u001b[2;31m-{abs(trophies_diff):<4}\u001b[0m"
                elif trophies_diff > 0:
                    trophies_diff_2 = f"\u001b[2;32m+{abs(trophies_diff):<4}\u001b[0m"
                else:
                    trophies_diff_2 = f"{'-':^5}"
            except:
                trophies_diff_2 = f"{'':<5}"

            # Trophies
            message += f"{'🏆' + '{:<6,.0f}'.format(records[i]['score'])} {trophies_diff_2}\n"

        # Split message
        cannot_split = False  # Prevent index out of range error
        try:  # In case there are not enough records
            message1 = message[:[m.start()
                                 for m in re.finditer(r"\n", message)][24]]
            message2 = message[([m.start()
                                 for m in re.finditer(r"\n", message)][24])+1:] + "```"
        except:
            cannot_split = True

        # Send
        if cannot_split == False:
            cur_page = 1
            embed_init = discord.Embed(
                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=label+message1+"```")
            embed_init.set_footer(
                text=f"Page 1/2:  1 to 25 | Changes since {db[f'trophies_{season}']['last_update_time']}")
            msg = await interaction.followup.send(embed=embed_init)
            msg2 = await interaction.followup.send(embed=discord.Embed(description="To be edited..."))

            for reaction_emoji in ["◀️", "▶️", "⏹️"]:
                await msg.add_reaction(reaction_emoji)

            while True:
                try:
                    reaction, user = await client.wait_for("reaction_add", timeout=10, check=check)
                    # Waiting for a reaction to be added - times out after 10 seconds

                    if str(reaction.emoji) == "▶️" and cur_page == 1:  # Go to Page 2
                        cur_page += 1
                        embed_first = discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description="\n"+label+message2)
                        embed_first.set_footer(
                            text=f"Page 2/2: 26 to 50 | Changes since {db[f'trophies_{season}']['last_update_time']}")
                        await msg.edit(embed=embed_first)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page == 2:  # Go to Page 1
                        cur_page -= 1
                        embed_second = discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description="\n"+label+message1+"```")
                        embed_second.set_footer(
                            text=f"Page 1/2:  1 to 25 | Changes since {db[f'trophies_{season}']['last_update_time']}")
                        await msg.edit(embed=embed_second)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                        await msg.edit(embed=discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=label+message1+"```"))
                        embed_second_timeout = discord.Embed(
                            description="```ansi\n"+message2)
                        embed_second_timeout.set_footer(
                            text=f"Changes since {db[f'trophies_{season}']['last_update_time']}")
                        await msg2.edit(embed=embed_second_timeout)
                        await msg.clear_reactions()
                        break

                    else:
                        await msg.remove_reaction(reaction, user)
                        # Removes reactions if invalid
                except asyncio.TimeoutError:
                    await msg.edit(embed=discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=label+message1+"```"))
                    embed_second_timeout = discord.Embed(
                        description="```ansi\n"+message2)
                    embed_second_timeout.set_footer(
                        text=f"Changes since {db[f'trophies_{season}']['last_update_time']}")
                    await msg2.edit(embed=embed_second_timeout)
                    await msg.clear_reactions()
                    break
                    # Ending the loop if user doesn't react after 10 seconds
        elif cannot_split == True:  # Send in 1 message if there are too little records
            await interaction.followup.send(embed=discord.Embed(
                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=label+message+"```"))

        # Update to replit's database for old keys
        if (f"trophies_{season}" in db.keys()) and (new_key_flag == False):
            value = dict()
            for record in records:
                value[record['owner_id']] = {
                    'rank': record['rank'], 'score': record['score']}
            value['last_update_time'] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record['leaderboard_id']] = value

    elif changes == "Hidden":
        def hidden():
            # Using f-string spacing to pretty print the leaderboard labels (bold)
            message = f"```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {'Points:'}\u001b[0m\n{'─' * 37}\n"

            # Using f-string spacing to pretty print the leaderboard
            for record in records:
                # Rank (bold)
                message += f"\u001b[1m{'#' + str(record['rank']):<5}\u001b[0m "

                # Name
                message += f"{record['username']:<20} "

                # Trophies
                message += f"{'🏆' + '{:,}'.format(record['score'])}\n"
            message += "```"
            return message

        # Send
        cur_page = 1
        embed_init = discord.Embed(
            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=hidden())
        embed_init.set_footer(
            text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
        msg = await interaction.followup.send(embed=embed_init)

        for reaction_emoji in ["◀️", "▶️", "⏪", "⏹️"]:
            await msg.add_reaction(reaction_emoji)

        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=10, check=check)
                # Waiting for a reaction to be added - times out after 10 seconds

                if str(reaction.emoji) == "▶️" and next_cursor != False:  # Next page
                    cur_page += 1
                    response = await moonrock_client.query_leaderboard(
                        season, "trophies", 25, cursor_dict[cur_page])
                    records = json.loads(response['payload'])['records']
                    start = records[0]['rank']
                    end = records[len(records)-1]['rank']
                    try:
                        cursor_dict[cur_page +
                                    1] = json.loads(response['payload'])['next_cursor']
                    except:
                        next_cursor = False  # Does not exist
                    embed_next = discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=hidden())
                    embed_next.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
                    await msg.edit(embed=embed_next)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                    cur_page -= 1
                    response = await moonrock_client.query_leaderboard(
                        season, "trophies", 25, cursor_dict[cur_page])
                    records = json.loads(response['payload'])['records']
                    start = records[0]['rank']
                    end = records[len(records)-1]['rank']
                    embed_prev = discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=hidden())
                    embed_prev.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
                    await msg.edit(embed=embed_prev)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                    cur_page = 1
                    next_cursor = True
                    response = await moonrock_client.query_leaderboard(season, "trophies", 25, cursor_dict[cur_page])
                    records = json.loads(response['payload'])['records']
                    start = records[0]['rank']
                    end = records[len(records)-1]['rank']
                    embed_first = discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=hidden())
                    embed_first.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
                    await msg.edit(embed=embed_first)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                    response = await moonrock_client.query_leaderboard(
                        season, "trophies", 50)
                    records = json.loads(response['payload'])['records']
                    await msg.edit(embed=discord.Embed(title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=hidden()))
                    await msg.clear_reactions()
                    break

                else:
                    await msg.remove_reaction(reaction, user)
                    # Removes reactions if invalid
            except asyncio.TimeoutError:
                response = await moonrock_client.query_leaderboard(
                    season, "trophies", 50)
                records = json.loads(response['payload'])['records']
                await msg.edit(embed=discord.Embed(title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:", description=hidden()))
                await msg.clear_reactions()
                break
                # Ending the loop if user doesn't react after 10 seconds


@tree.command()
@app_commands.describe(
    user_type='Use either User ID or Friend ID of the user',
    id='User ID or Friend ID of the user',
    section='Section(s) to be shown'
)
async def get_user(interaction: discord.Interaction, user_type: typing.Literal['User ID', 'Friend ID'], id: str, section: typing.Literal['General Info only', 'with Badges', 'with Season Top 50 Records', 'with Stats', 'with Items Collected', 'with Tanks', 'with Parachutes', 'with Trails', 'with All Cosmetics', 'All']):
    '''Return info about a specified user'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    # If the user specified a friend code we need to query the server for their ID.
    try:
        if (user_type == "Friend ID"):
            id_response = await rocketbot_client.friend_code_to_id(id)
            id = json.loads(id_response['payload'])['user_id']

        # Get user data
        response = await rocketbot_client.get_user(id)
        user_data = json.loads(response['payload'])[0]
        metadata = user_data['metadata']
    except aiohttp.ClientResponseError:
        # The code is wrong, send an error response
        await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(),
                                                            title="❌ Player not found ❌"))
        return

    # Create message
    message = ""

    # Get award config
    awards_config = server_config['awards']
    default_award = {'type': "Unknown", "name": "Unknown"}

    # Get general player info
    username = user_data['display_name']
    is_online = user_data['online']
    create_time = user_data['create_time']
    timed_bonus_last_collect = metadata['timed_bonus_last_collect']
    current_tank = metadata['skin'].replace(
        '_', ' ').split()[0].title() + " " + awards_config.get(
            awards_config.get(metadata['skin'], default_award)['skin_name'],
            default_award)['name']
    current_trail = awards_config.get(metadata['trail'], default_award)['name']
    current_parachute = awards_config.get(metadata['parachute'],
                                          default_award)['name']
    current_badge = awards_config.get(metadata['badge'], default_award)['name']
    no_season_pass = False
    try:
        has_season_pass = server_config['season'] in metadata['season_passes']
    except:
        no_season_pass = True
    level = metadata['progress']['level']
    XP = metadata['progress']['xp']
    friend_code = metadata['friend_code']
    id = user_data['user_id']

    # Add general player info
    general_info = "```\n"
    general_info += f"Username: {username}\n"
    general_info += f"Online: {is_online}\n"
    general_info += f"Create Time: {datetime.datetime.utcfromtimestamp(create_time):%Y-%m-%d %H:%M:%S} UTC\n"
    general_info += f"Timed Bonus Last Collect: {datetime.datetime.utcfromtimestamp(timed_bonus_last_collect):%Y-%m-%d %H:%M:%S} UTC\n"
    general_info += f"Current Tank: {current_tank}\n"
    general_info += f"Current Trail: {current_trail}\n"
    general_info += f"Current Parachute: {current_parachute}\n"
    general_info += f"Current Badge: {current_badge}\n"
    if no_season_pass == False:
        general_info += f"Has Season Pass: {has_season_pass}\n"
    general_info += f"Level: {level}\n"
    general_info += f"XP: {XP}\n"
    general_info += f"Friend Code: {friend_code}\n"
    general_info += f"User ID: {id}\n"
    general_info += "```"

    # Add to embed
    message += f"📓 ***General Info***:\n{general_info}\n"

    if section in {"with Season Top 50 Records", "All"}:
        # Create season records list
        season_top_50_records_list = "```ansi\n"

        points_label = "\u001b[1;2mBy points (Season 1 to 10)\u001b[0m\n"
        points = f"{'Season:':<8}{'Rank:':<7}{'Points:':<9}\n{'─'*24}\n"
        trophies_label = f"\u001b[1;2mBy trophies (Season 11 to {curr_season - 1})\u001b[0m\n"
        trophies = f"{'Season:':<8}{'Rank:':<7}{'Trophies:':<9}\n{'─'*24}\n"
        points_record = False
        trophies_record = False

        for i in range(1, curr_season):  # From first season to previous season
            response = await rocketbot_client.query_leaderboard(i, ("tankkings_points" if i <= 10 else "tankkings_trophies"), 50)
            records = json.loads(response['payload'])['records']
            for record in records:
                if record['owner_id'] == id:  # Records found (Top 50)
                    if record['rank'] == 1:
                        rank_emoji = '🥇'
                    elif record['rank'] == 2:
                        rank_emoji = '🥈'
                    elif record['rank'] == 3:
                        rank_emoji = '🥉'
                    else:
                        rank_emoji = '  '
                    if i <= 10:
                        points_record = True
                        points += f"{i:^8}{rank_emoji:<1}{record['rank']:<5}🧊{record['score']:<9,.0f}\n"
                    else:
                        trophies_record = True
                        trophies += f"{i:^8}{rank_emoji:<1}{record['rank']:<5}🏆{record['score']:<9,.0f}\n"
        if points_record == False and trophies_record == False:
            season_top_50_records_list += "No records found"
        else:
            if points_record == True:
                season_top_50_records_list += points_label + points
            if trophies_record == True:
                season_top_50_records_list += ("\n" if points_record ==
                                               True else "") + trophies_label + trophies
        season_top_50_records_list += "```"

        # Add to embed
        message += f"📊 ***Season Top 50 Records***:\n{season_top_50_records_list}\n"

    if section in {"with Badges", "All"}:
        # Create badge list
        badge_list = "```\n"

        for badge in metadata['awards']:
            award = awards_config.get(badge, default_award)
            type = award['type']

            if type == "badge":
                badge_list += award['name'] + "\n"
        badge_list += "```"

        # Add to embed
        message += f"🛡️ ***Badges***:\n{badge_list}\n"

    if section in {"with Stats", "All"}:
        # Create stats
        stat_list = "```ansi\n"

        # Rearrange keys
        keys_order = {
            "best_rank": 0,
            "crates_collected": 0,
            "meters_driven": 0,
            "longest_killstreak": 0,
            "5_kills": 0,
            "most_player_kills": 0,
            "most_total_kills": 0,
            "player_kills": 0,
            "bot_kills": 0,
            "total_kills": 0,
            "deaths": 0,
            "K/D Ratio": 0,
            "assists": 0,
            "dunk_tanks": 0,
            "first_bloods": 0,
            "snipers": 0,
            "two_birdss": 0,
            "yardsales": 0,
            "double_kills": 0,
            "triple_kills": 0,
            "quad_kills": 0,
            "games_played": 0,
            "games_won": 0,
            "top_5": 0,
            "teams_played": 0,
            "teams_won": 0,
            "squads_played": 0,
            "squads_won": 0,
            "minemayhem_played": 0,
            "minemayhem_won": 0,
            "total_games_played": 0,
            "missiles_fired": 0,
            "kills_using_missiles": 0,
            "drills_used": 0,
            "kills_using_drill": 0,
            "flaks_used": 0,
            "kills_using_flak": 0,
            "grenades_used": 0,
            "kills_using_grenade": 0,
            "homings_used": 0,
            "kills_using_homing": 0,
            "mines_used": 0,
            "kills_using_mine": 0,
            "nukes_used": 0,
            "kills_using_nuke": 0,
            "poisons_used": 0,
            "kills_using_poison": 0,
            "shields_used": 0,
            "kills_using_shield": 0,
            "triple-shots_used": 0,
            "kills_using_triple-shot": 0,
            "jetpacks_used": 0,
            "whirlwinds_used": 0,
            "blocks_using_proj": 0,
            "blocks_using_shield": 0
        }
        for key, value in metadata['stats'].items():
            keys_order[key] = value

        # Plot Kills by Weapons pie chart
        data_stream = io.BytesIO()  # Initialize IO

        labels = []
        sizes = []
        for key in keys_order:
            if "kills_using" in key and keys_order[key] != 0:
                if "triple-shot" in key:
                    labels.append(key.replace("kills_using_", "").replace(
                        "triple-shot", "rapidfire").title())
                else:
                    labels.append(key.replace("kills_using_", "").title())
                sizes.append(keys_order[key])

        fig1, ax1 = plt.subplots(facecolor=("#2f3137"), figsize=(5, 6))
        ax1.set_title(user_data['display_name']+'\'s\n Kills Using Weapons distribution',
                      color="#FFFFFF", fontsize=16, pad=15)
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'color': "#FFFFFF"}, wedgeprops={
                "edgecolor": "#FFFFFF", 'linewidth': 1, 'antialiased': True}, pctdistance=0.85)
        ax1.axis('equal')

        plt.savefig(data_stream, format='png', dpi=80)
        plt.close()

        # Avoid divided by zero error
        try:
            total_games_played = keys_order["games_played"] + keys_order[
                "teams_played"] + keys_order["squads_played"] + keys_order[
                    "minemayhem_played"]
        except:
            total_games_played = 0
        try:
            player_kills_pct = keys_order["player_kills"] / keys_order[
                "total_kills"]
        except:
            player_kills_pct = 0
        try:
            bot_kills_pct = keys_order["bot_kills"] / keys_order["total_kills"]
        except:
            bot_kills_pct = 0
        try:
            KDR = round(keys_order["total_kills"] / keys_order["deaths"], 2)
        except:
            KDR = 0
        try:
            games_won_pct = keys_order["games_won"] / \
                keys_order["games_played"]
        except:
            games_won_pct = 0
        try:
            top_5_pct = keys_order["top_5"] / keys_order["games_played"]
        except:
            top_5_pct = 0
        try:
            squads_won_pct = keys_order["squads_won"] / keys_order[
                "squads_played"]
        except:
            squads_won_pct = 0
        try:
            teams_won_pct = keys_order["teams_won"] / \
                keys_order["teams_played"]
        except:
            teams_won_pct = 0
        try:
            minemayhem_won_pct = keys_order["minemayhem_won"] / keys_order[
                "minemayhem_played"]
        except:
            minemayhem_won_pct = 0
        try:
            kills_using_drill_pct = keys_order[
                "kills_using_drill"] / keys_order["drills_used"]
        except:
            kills_using_drill_pct = 0
        try:
            kills_using_flak_pct = keys_order["kills_using_flak"] / keys_order[
                "flaks_used"]
        except:
            kills_using_flak_pct = 0
        try:
            kills_using_grenade_pct = keys_order[
                "kills_using_grenade"] / keys_order["grenades_used"]
        except:
            kills_using_grenade_pct = 0
        try:
            kills_using_homing_pct = keys_order[
                "kills_using_homing"] / keys_order["homings_used"]
        except:
            kills_using_homing_pct = 0
        try:
            kills_using_mine_pct = keys_order["kills_using_mine"] / keys_order[
                "mines_used"]
        except:
            kills_using_mine_pct = 0
        try:
            kills_using_nuke_pct = keys_order["kills_using_nuke"] / keys_order[
                "nukes_used"]
        except:
            kills_using_nuke_pct = 0
        try:
            kills_using_poison_pct = keys_order[
                "kills_using_poison"] / keys_order["poisons_used"]
        except:
            kills_using_poison_pct = 0
        try:
            kills_using_shield_pct = keys_order[
                "kills_using_shield"] / keys_order["shields_used"]
        except:
            kills_using_shield_pct = 0
        try:
            kills_using_triple_shot_pct = keys_order[
                "kills_using_triple-shot"] / keys_order["triple-shots_used"]
        except:
            kills_using_triple_shot_pct = 0
        try:
            kills_using_missiles = keys_order["total_kills"] - keys_order[
                "kills_using_drill"] - keys_order[
                    "kills_using_flak"] - keys_order[
                        "kills_using_grenade"] - keys_order[
                            "kills_using_homing"] - keys_order[
                                "kills_using_mine"] - keys_order[
                                    "kills_using_nuke"] - keys_order[
                                        "kills_using_poison"] - keys_order[
                                            "kills_using_shield"] - keys_order[
                                                "kills_using_triple-shot"]
        except:
            kills_using_missiles = 0
        try:
            kills_using_missiles_pct = kills_using_missiles / keys_order[
                "missiles_fired"]
        except:
            kills_using_missiles_pct = 0
        try:
            blocks_using_proj_pct = keys_order["blocks_using_proj"] / (
                keys_order["blocks_using_proj"] +
                keys_order["blocks_using_shield"])
        except:
            blocks_using_proj_pct = 0
        try:
            blocks_using_shield_pct = keys_order["blocks_using_shield"] / (
                keys_order["blocks_using_proj"] +
                keys_order["blocks_using_shield"])
        except:
            blocks_using_shield_pct = 0

        keys_order["meters_driven"] = "{:.1f}".format(
            keys_order["meters_driven"] / 1000) + " km"
        keys_order["player_kills"] = "{:<6}".format(
            keys_order["player_kills"]) + f"({player_kills_pct*100:.0f}%)"
        keys_order["bot_kills"] = "{:<6}".format(
            keys_order["bot_kills"]) + f"({bot_kills_pct*100:.0f}%)"
        keys_order["K/D Ratio"] = KDR
        keys_order["games_won"] = "{:<6}".format(
            keys_order["games_won"]) + f"({games_won_pct*100:.0f}%)"
        keys_order["top_5"] = "{:<6}".format(
            keys_order["top_5"]) + f"({top_5_pct*100:.0f}%)"
        keys_order["squads_won"] = "{:<6}".format(
            keys_order["squads_won"]) + f"({squads_won_pct*100:.0f}%)"
        keys_order["teams_won"] = "{:<6}".format(
            keys_order["teams_won"]) + f"({teams_won_pct*100:.0f}%)"
        keys_order["minemayhem_won"] = "{:<6}".format(
            keys_order["minemayhem_won"]) + f"({minemayhem_won_pct*100:.0f}%)"
        keys_order["total_games_played"] = total_games_played
        keys_order["kills_using_drill"] = "{:<6}".format(
            keys_order["kills_using_drill"]
        ) + f"({kills_using_drill_pct*100:.0f}%)"
        keys_order["kills_using_flak"] = "{:<6}".format(
            keys_order["kills_using_flak"]
        ) + f"({kills_using_flak_pct*100:.0f}%)"
        keys_order["kills_using_grenade"] = "{:<6}".format(
            keys_order["kills_using_grenade"]
        ) + f"({kills_using_grenade_pct*100:.0f}%)"
        keys_order["kills_using_homing"] = "{:<6}".format(
            keys_order["kills_using_homing"]
        ) + f"({kills_using_homing_pct*100:.0f}%)"
        keys_order["kills_using_mine"] = "{:<6}".format(
            keys_order["kills_using_mine"]
        ) + f"({kills_using_mine_pct*100:.0f}%)"
        keys_order["kills_using_nuke"] = "{:<6}".format(
            keys_order["kills_using_nuke"]
        ) + f"({kills_using_nuke_pct*100:.0f}%)"
        keys_order["kills_using_poison"] = "{:<6}".format(
            keys_order["kills_using_poison"]
        ) + f"({kills_using_poison_pct*100:.0f}%)"
        keys_order["kills_using_shield"] = "{:<6}".format(
            keys_order["kills_using_shield"]
        ) + f"({kills_using_shield_pct*100:.0f}%)"
        keys_order["kills_using_triple-shot"] = "{:<6}".format(
            keys_order["kills_using_triple-shot"]
        ) + f"({kills_using_triple_shot_pct*100:.0f}%)"
        keys_order["kills_using_missiles"] = "{:<6}".format(
            str(kills_using_missiles)
        ) + f"({kills_using_missiles_pct*100:.0f}%)"
        keys_order["blocks_using_proj"] = "{:<6}".format(
            keys_order["blocks_using_proj"]
        ) + f"({blocks_using_proj_pct*100:.0f}%)"
        keys_order["blocks_using_shield"] = "{:<6}".format(
            keys_order["blocks_using_shield"]
        ) + f"({blocks_using_shield_pct*100:.0f}%)"

        first_title = " General "
        stat_list += f"\u001b[1;2m{first_title.center(44, '—')}\u001b[0m\n"
        keys = [
            "deaths", "snipers", "two_birdss", "games_played", "games_won",
            "top_5", "teams_played", "teams_won", "triple-shots_used",
            "kills_using_triple-shot", "blocks_using_proj"
        ]
        rennamed_keys = [
            "total_deaths", "long_shot", "two_birdses", "solo_played",
            "solo_won", "solo_top_5", "Red_VS_Blue_played", "Red_VS_Blue_won",
            "rapidfire_used", "kills_using_rapidfire", "blocks_using_missile"
        ]
        for key in keys_order:
            if key in keys:
                renamed_key = rennamed_keys[keys.index(key)]
            else:
                renamed_key = key
            stat_list += f"{renamed_key.replace('_', ' ').title():>21}: {keys_order[key]}\n"
            remaining_titles = [" Medals ", " Games Played ", " Weapons "]
            key_cutoff = ["K/D Ratio", "quad_kills", "total_games_played"]
            if key in key_cutoff:
                stat_list += f"\n\u001b[1;2m{remaining_titles[key_cutoff.index(key)].center(44, '—')}\u001b[0m\n"

        stat_list += "```"

        # Add to embed
        message += f"🗒️ ***Stats***:\n{stat_list}"

    # Send first message if contains all sections
    if section in {"All"}:
        embed1 = discord.Embed(description=message, color=0x00C6FE)
        data_stream.seek(0)
        chart = discord.File(data_stream, filename="plot.png")
        embed1.set_image(url="attachment://plot.png")
        await interaction.followup.send(embed=embed1, file=chart)

    if section in {
            "with Items Collected", "with Tanks", "with Parachutes", "with Trails", "with All Cosmetics", "All"
    }:
        # Get skins info
        tank_common_total = 0
        tank_rare_total = 0
        tank_legendary_total = 0
        tank_purchased_total = 0
        tank_earned_total = 0
        parachute_common_total = 0
        parachute_rare_total = 0
        parachute_legendary_total = 0
        parachute_purchased_total = 0
        parachute_earned_total = 0
        trail_common_total = 0
        trail_rare_total = 0
        trail_legendary_total = 0
        trail_purchased_total = 0
        trail_earned_total = 0

        tank_common_owned = 0
        tank_rare_owned = 0
        tank_legendary_owned = 0
        tank_purchased_owned = 0
        tank_earned_owned = 0
        parachute_common_owned = 0
        parachute_rare_owned = 0
        parachute_legendary_owned = 0
        parachute_purchased_owned = 0
        parachute_earned_owned = 0
        trail_common_owned = 0
        trail_rare_owned = 0
        trail_legendary_owned = 0
        trail_purchased_owned = 0
        trail_earned_owned = 0

        for key, value in awards_config.items():
            try:
                try:
                    if value['hidden'] != True:
                        pass
                    else:
                        if value['name'] == 'Moai':
                            tank_legendary_total += 1

                except:
                    if value['type'] == "skin_set":
                        if value['rarity'] == "common":
                            tank_common_total += 1
                        elif value['rarity'] == "rare":
                            tank_rare_total += 1
                        elif value['rarity'] == "legendary":
                            tank_legendary_total += 1
                        elif value['rarity'] == "purchased":
                            tank_purchased_total += 1
                        elif value['rarity'] == "earned":
                            tank_earned_total += 1
                    elif value['type'] == "parachute":
                        if value['rarity'] == "common":
                            parachute_common_total += 1
                        elif value['rarity'] == "rare":
                            parachute_rare_total += 1
                        elif value['rarity'] == "legendary":
                            parachute_legendary_total += 1
                        elif value['rarity'] == "purchased":
                            parachute_purchased_total += 1
                        elif value['rarity'] == "earned":
                            parachute_earned_total += 1
                    elif value['type'] == "trail":
                        if value['rarity'] == "common":
                            trail_common_total += 1
                        elif value['rarity'] == "rare":
                            trail_rare_total += 1
                        elif value['rarity'] == "legendary":
                            trail_legendary_total += 1
                        elif value['rarity'] == "purchased":
                            trail_purchased_total += 1
                        elif value['rarity'] == "earned":
                            trail_earned_total += 1
            except:
                pass

        tank_list_duplicated = []
        for tank in metadata['awards']:
            award = awards_config.get(tank, default_award)
            type = award['type']

            if type == "skin":
                tank_list_duplicated.append(award['skin_name'])

        tank_list_counter = Counter(tank_list_duplicated)
        for unique_tank in tank_list_counter:
            try:
                if awards_config.get(unique_tank)['rarity'] == "common":
                    tank_common_owned += 1
                elif awards_config.get(unique_tank)['rarity'] == "rare":
                    tank_rare_owned += 1
                elif awards_config.get(unique_tank)['rarity'] == "legendary":
                    tank_legendary_owned += 1
                elif awards_config.get(unique_tank)['rarity'] == "purchased":
                    tank_purchased_owned += 1
                elif awards_config.get(unique_tank)['rarity'] == "earned":
                    tank_earned_owned += 1
            except:
                pass

        # Create parachute list
        parachute_list = f"```\n{'Rarity:':<7} {'Name:':<17}\n{'—'*25}\n"

        # Create trail list
        trail_list = f"```\n{'Rarity:':<7} {'Name:':<17}\n{'—'*25}\n"

        for award in metadata['awards']:
            skin = awards_config.get(award, default_award)

            try:
                if skin['name'] == 'No trail':
                    trail_list += "        " + skin['name'] + "\n"
                else:
                    type = skin['type']
                    rarity = skin['rarity']
                    if type == "parachute":
                        if rarity == 'common':
                            parachute_common_owned += 1
                            parachute_list += "     ⭐ " + skin['name'] + "\n"
                        elif rarity == 'rare':
                            parachute_rare_owned += 1
                            parachute_list += "   ⭐⭐ " + skin['name'] + "\n"
                        elif rarity == 'legendary':
                            parachute_legendary_owned += 1
                            parachute_list += " ⭐⭐⭐ " + skin['name'] + "\n"
                        elif rarity == 'purchased':
                            parachute_purchased_owned += 1
                            parachute_list += "     💰 " + skin['name'] + "\n"
                        elif rarity == 'earned':
                            parachute_earned_owned += 1
                            parachute_list += "     🏅 " + skin['name'] + "\n"
                    if type == "trail":
                        if rarity == 'common':
                            trail_common_owned += 1
                            trail_list += "     ⭐ " + skin['name'] + "\n"
                        elif rarity == 'rare':
                            trail_rare_owned += 1
                            trail_list += "   ⭐⭐ " + skin['name'] + "\n"
                        elif rarity == 'legendary':
                            trail_legendary_owned += 1
                            trail_list += " ⭐⭐⭐ " + skin['name'] + "\n"
                        elif rarity == 'purchased':
                            trail_purchased_owned += 1
                            trail_list += "     💰 " + skin['name'] + "\n"
                        elif rarity == 'earned':
                            trail_earned_owned += 1
                            trail_list += "     🏅 " + skin['name'] + "\n"
            except:
                pass

        parachute_list += "```"
        trail_list += "```"

        common_owned = tank_common_owned + parachute_common_owned + trail_common_owned
        common_total = tank_common_total + parachute_common_total + trail_common_total
        rare_owned = tank_rare_owned + parachute_rare_owned + trail_rare_owned
        rare_total = tank_rare_total + parachute_rare_total + trail_rare_total
        legendary_owned = tank_legendary_owned + \
            parachute_legendary_owned + trail_legendary_owned
        legendary_total = tank_legendary_total + \
            parachute_legendary_total + trail_legendary_total
        purchased_owned = tank_purchased_owned + \
            parachute_purchased_owned + trail_purchased_owned
        purchased_total = tank_purchased_total + \
            parachute_purchased_total + trail_purchased_total
        earned_owned = tank_earned_owned + parachute_earned_owned + trail_earned_owned
        earned_total = tank_earned_total + \
            parachute_earned_total + trail_earned_total

        tank_owned = tank_common_owned + tank_rare_owned + \
            tank_legendary_owned + tank_purchased_owned + tank_earned_owned
        tank_total = tank_common_total + tank_rare_total + \
            tank_legendary_total + tank_purchased_total + tank_earned_total
        parachute_owned = parachute_common_owned + \
            parachute_rare_owned + parachute_legendary_owned + \
            parachute_purchased_owned + parachute_earned_owned
        parachute_total = parachute_common_total + \
            parachute_rare_total + parachute_legendary_total + \
            parachute_purchased_total + parachute_earned_total
        trail_owned = trail_common_owned + trail_rare_owned + \
            trail_legendary_owned + trail_purchased_owned + trail_earned_owned
        trail_total = trail_common_total + trail_rare_total + \
            trail_legendary_total + trail_purchased_total + trail_earned_total

        owned = tank_owned + parachute_owned + trail_owned
        total = tank_total + parachute_total + trail_total

        # Items Collected table
        s = f"```\n┌{'─'*17}┬{'─'*5}┬{'─'*10}┬{'─'*6}┬{'─'*9}┐\n│{'Rarity':^17}│{'Tanks':^5}│{'Parachutes':^10}│{'Trails':^6}│{'Sub-total':^9}│\n├{'─'*17}┼{'─'*5}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│     * {'Common':<10}│{str(tank_common_owned):>2}/{str(tank_common_total):<2}│{str(parachute_common_owned):>4}/{str(parachute_common_total):<5}│{str(trail_common_owned):>2}/{str(trail_common_total):<3}│{str(common_owned):>4}/{str(common_total):<4}│\n├{'─'*17}┼{'─'*5}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│    ** {'Rare':<10}│{str(tank_rare_owned):>2}/{str(tank_rare_total):<2}│{str(parachute_rare_owned):>4}/{str(parachute_rare_total):<5}│{str(trail_rare_owned):>2}/{str(trail_rare_total):<3}│{str(rare_owned):>4}/{str(rare_total):<4}│\n├{'─'*17}┼{'─'*5}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│   *** {'Legendary':<10}│{str(tank_legendary_owned):>2}/{str(tank_legendary_total):<2}│{str(parachute_legendary_owned):>4}/{str(parachute_legendary_total):<5}│{str(trail_legendary_owned):>2}/{str(trail_legendary_total):<3}│{str(legendary_owned):>4}/{str(legendary_total):<4}│\n├{'─'*17}┼{'─'*5}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│     $ {'Purchased':<10}│{str(tank_purchased_owned):>2}/{str(tank_purchased_total):<2}│{str(parachute_purchased_owned):>4}/{str(parachute_purchased_total):<5}│{str(trail_purchased_owned):>2}/{str(trail_purchased_total):<3}│{str(purchased_owned):>4}/{str(purchased_total):<4}│\n├{'─'*17}┼{'─'*5}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│     Ꙋ {'Earned':<10}│{str(tank_earned_owned):>2}/{str(tank_earned_total):<2}│{str(parachute_earned_owned):>4}/{str(parachute_earned_total):<5}│{str(trail_earned_owned):>2}/{str(trail_earned_total):<3}│{str(earned_owned):>4}/{str(earned_total):<4}│\n├{'─'*17}┼{'─'*5}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│ {'Sub-total':^16}│{str(tank_owned):>2}/{str(tank_total):<2}│{str(parachute_owned):>4}/{str(parachute_total):<5}│{str(trail_owned):>2}/{str(trail_total):<3}│{str(owned):>4}/{str(total):<4}│\n└{'─'*17}┴{'─'*5}┴{'─'*10}┴{'─'*6}┴{'─'*9}┘```"

        if section in {"with Items Collected", "with All Cosmetics"}:
            # Add to embed
            message += f"📦 ***Items Collected***:\n{s}\n"

        if section in {"with Tanks", "with All Cosmetics", "All"}:
            # Create tank list
            tank_list = f"```\n{'Rarity:':<7} {'Name:':<17} {'Colors:':}\n{'—'*33}\n"

            for unique_tank in tank_list_counter:
                try:
                    if awards_config.get(unique_tank,
                                         default_award)['rarity'] == 'common':
                        tank_list += f"     ⭐ {awards_config.get(unique_tank, default_award)['name']:<17} {str(tank_list_counter[unique_tank])}\n"
                    elif awards_config.get(unique_tank,
                                           default_award)['rarity'] == 'rare':
                        tank_list += f"   ⭐⭐ {awards_config.get(unique_tank, default_award)['name']:<17} {str(tank_list_counter[unique_tank])}\n"
                    elif awards_config.get(
                            unique_tank,
                            default_award)['rarity'] == 'legendary':
                        tank_list += f" ⭐⭐⭐ {awards_config.get(unique_tank, default_award)['name']:<17} {str(tank_list_counter[unique_tank])}\n"
                    elif awards_config.get(
                            unique_tank,
                            default_award)['rarity'] == 'purchased':
                        tank_list += f"     💰 {awards_config.get(unique_tank, default_award)['name']:<17} {str(tank_list_counter[unique_tank])}\n"
                    elif awards_config.get(
                            unique_tank, default_award)['rarity'] == 'earned':
                        tank_list += f"     🏅 {awards_config.get(unique_tank, default_award)['name']:<17} {str(tank_list_counter[unique_tank])}\n"
                except:
                    pass

            tank_list += "```"

        if section in {"with Tanks", "with All Cosmetics"}:
            # Add to embed
            message += f"🪖 ***Tanks***:\n{tank_list}\n"

        if section in {"with Parachutes", "with All Cosmetics"}:
            # Add to embed
            message += f"🪂 ***Parachutes***:\n{parachute_list}\n"

        if section in {"with Trails", "with All Cosmetics"}:
            # Add to embed
            message += f"🌟 ***Trails***:\n{trail_list}\n"

        if section in {"All"}:
            # Separate message for cosmetics related info for all sections to avoid message exceeds length limit
            message_2 = ""
            message_2 += f"📦 ***Items Collected***:\n{s}\n"
            message_2 += f"🪖 ***Tanks***:\n{tank_list}\n"
            message_2 += f"🪂 ***Parachutes***:\n{parachute_list}\n"
            message_2 += f"🌟 ***Trails***:\n{trail_list}\n"

    # Send message
    if section not in {"All"}:
        embed1 = discord.Embed(description=message, color=0x00C6FE)
        if section in {"with Stats"}:
            data_stream.seek(0)
            chart = discord.File(data_stream, filename="plot.png")
            embed1.set_image(url="attachment://plot.png")
            await interaction.followup.send(embed=embed1, file=chart)
        else:
            await interaction.followup.send(embed=embed1)
    if section in {"All"}:
        await interaction.followup.send(
            embed=discord.Embed(description=message_2, color=0x00C6FE))


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

    events = {
        "The bot dodged your attack. <:bot:917467970182189056>": 70,
        "You destroyed the bot! It drops a single coin. <:coin:910247623787700264>": 10,
        "The bot *expertly* dodged your attack. <:bot:917467970182189056>": 5,
        "You thought you hit the bot, but its health returns to full due to network lag. 📶": 5,
        "You destroyed the bot! It drops a some coins and a crate. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> 📦. But <R> comes out of nowhere and steals it.": 3,
        "You accidentally hit a teammate and dunk them into the water. <:splash:910252276961128469>": 2,
        "The bot vanishes. An error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>": 1,
        "<R> comes out of nowhere and kills you and the bot to win the game.": 1,
        "<R> comes out of nowhere and shoots a shield at the bot deflecting it back to you and you die.": 1,
        "You miss. Before you try to shoot again <R> comes out of nowhere and stands next to the bot and you decide to leave out of sheer intimidation.": 1,
        "The missile goes off-screen. Instead of getting a kill, a beachball comes hurtling back at mach 2.": 0.3,
        "The bot vanishes. Was there ever really a bot there at all?...": 0.2,
        "You destroyed the bot! It drops what appears to be MILLIONS of coins, filling every pixel on your screen with a different shade of gold. Your game immediately slows to a halt and crashes.": 0.2,
        "The missile vanishes off the screen, seemingly lost to the water.\nSuddenly, you hear a flurry of *ping*s! The words \"Long Shot!\" splash across your monitor, followed by \"Two Birds\", \"Double Kill\", \"Triple Kill\", and finally \"Quad Kill\". This is it. This is the moment you thought would never happen. The \"Get a quad kill\" and \"Destroy two tanks with one explosion\" goals you've had for two months are finally complete. As the flood of joy and relief washes over you, so does the rising water over your tank. You've lost the match, but you don't care. The war is already won. In a hurry you leave the match and click to the Goals tab, overcome with anticipation to see those beautiful green *Collect!* buttons. You slide your cursor over.\nBAM! The moment before you click, the screen goes black. All you can see is \"Connecting...\". The loading indicator never goes away.": 0.1,
        "You get a quad kill, four birds one stone! It was four bots doing the same exact movement. They drop 4 coins. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264>": 0.1,
        "🗿 Moyai God comes down from the heavens and blocks your missile. You bow down (as a tank) and repent for your sins.": 0.1,
        "Before your bullet hits the bot you were aiming at, a shiny green bot jumps up and takes the hit. Suddenly a green gem appears where it died, floating in midair. JACKPOT<:gem:910247413695016970>": .1
    }
    event = "You fire a missile at a bot. <:rocketmint:910253491019202661>\n" + \
        random.choices(population=list(events.keys()),
                       weights=events.values(), k=1)[0]

    if "<R>" in event:
        # Get random name from leaderboard
        response = await rocketbot_client.query_leaderboard(curr_season, "tankkings_trophies", 50)
        records = json.loads(response['payload'])['records']
        rand_player = random.choice(records)['username']

        # Formulate response with random name
        event = event.replace("<R>", rand_player)
    else:
        # Otherwise wait half a second
        await asyncio.sleep(.5)

    await interaction.followup.send(event)


@tree.command(guild=discord.Object(id=962142361935314996))
async def build_a_bot(interaction: discord.Interaction):
    '''Bear the responsibility of creating new life... I mean bot'''
    bot_name = generate_random_name()
    response = f"***Meet your lovely new bot!***\n\n`{bot_name}`"
    if len(bots) >= 5:
        response += f"\n\n`{bot_name}` can't join because 5 bots have already joined"
    else:
        response += f"\n\n`{bot_name}` is joining the next game"
        players.append(bot_name)
        bots.append(bot_name)
    await interaction.response.send_message(response)


@tree.command(guild=discord.Object(id=962142361935314996))
async def join_game(interaction: discord.Interaction):
    '''Join the current game'''
    if playing:
        await interaction.response.send_message("Can't join because a game is already in progress")
        return
    response = ""
    if interaction.user.mention not in players:
        players.append(interaction.user.mention)
        response += '{} joined'.format(interaction.user.mention)
    else:
        response += '{} you cant join twice'.format(interaction.user.mention)

    await interaction.response.send_message(response)


@tree.command(guild=discord.Object(id=962142361935314996))
async def get_config(interaction: discord.Interaction):
    file = io.StringIO(json.dumps(server_config))
    await interaction.response.send_message(file=discord.File(fp=file, filename="server_config.json"))


@tree.command(guild=discord.Object(id=962142361935314996))
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
    embed1 = discord.Embed(color=0xa80022)
    embed1.add_field(name="Players: ", value=response, inline=False)
    await interaction.response.send_message(response)
    msg = await interaction.channel.send("Starting game")
#     await asyncio.sleep(0)
    moneys = OrderedDict()
    while len(players) >= 1:
        embed = discord.Embed(color=0xa80022)
        if len(players) <= 1:
            embed.add_field(name="Players: ", value=players[0], inline=False)
            embed.add_field(
                name="Game:", value=players[0] + " wins!", inline=False)
            money_txt = ""
            for i in moneys.keys():
                money_txt += i + " " + \
                    str(moneys[i]) + "<:coin:910247623787700264>\n"
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

        action_choice = random.choices(population=list(
            action_types.keys()), weights=action_types.values(), k=1)[0]

        action = ""
        if action_choice == "Kill":
            coin_num = random.choice(range(1, 100))
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
            weapons = {
                "A FAT BOI (nuke)": 100,
                "Rapidfire missiles": 100,
                "Grenades": 100,
                "A Homing Missile": 100,
                "A Flak": 100,
                "A Drill": 100,
                "THE POWER OF MOYAI 🗿": 0.1
            }
            event = random.choices(population=list(
                kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
            event = event.replace("<A>", player_a)
            event = event.replace("<B>", player_b)
            if "<U>" in event:
                event = event.replace("<U>", random.choices(population=list(
                    weapons.keys()), weights=weapons.values(), k=1)[0])
            # B-E die for kills, if we need a non dying player use F
            event += "\n\n" + player_a + " got " + \
                str(coin_num) + " <:coin:910247623787700264>"
            event += " and " + player_b + " lost " + \
                str(coin_num) + " <:coin:910247623787700264>"
            if '@' in player_a:  # Not a bot
                player_a_id = convert_mention_to_id(player_a)
                player_a_object = await interaction.guild.query_members(user_ids=[player_a_id])
                if player_a_object[0].nick == None:  # No nickname is found
                    player_a_name = str(player_a_object[0])[
                        :-5]  # Use username
                else:
                    player_a_name = player_a_object[0].nick  # Use nickname
                change_player_coin(player_a_id, player_a_name, coin_num)
            if '@' in player_b:  # Not a bot
                player_b_id = convert_mention_to_id(player_b)
                player_b_object = await interaction.guild.query_members(user_ids=[player_b_id])
                if player_b_object[0].nick == None:  # No nickname is found
                    player_b_name = str(player_b_object[0])[
                        :-5]  # Use username
                else:
                    player_b_name = player_b_object[0].nick  # Use nickname
                change_player_coin(player_b_id, player_b_name, -coin_num)
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
                players.remove(player_c)
                event = event.replace("<C>", player_c)
            if "<D>" in event:
                #                 coin_num += random.choice(range(1,100)
                player_d = random.choice(players)
                players.remove(player_d)
                event.replace("<D>", player_d)
            if "<E>" in event:
                #                 coin_num += random.choice(range(1,100)
                player_e = random.choice(players)
                players.remove(player_e)
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
            event = random.choices(population=list(
                kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
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
            money_txt += i + " " + \
                str(moneys[i]) + "<:coin:910247623787700264>\n"
        if money_txt != "":
            embed.add_field(name="Money:", value=money_txt, inline=False)
        await msg.edit(embed=embed)
        await asyncio.sleep(5)


@tree.command(guild=discord.Object(id=962142361935314996))
async def get_money(interaction: discord.Interaction):
    '''Find out how much money you have in discord'''
    await interaction.response.defer(ephemeral=False, thinking=True)

    id = convert_mention_to_id(interaction.user.mention)
    user_object = await interaction.guild.query_members(user_ids=[id])
    if user_object[0].nick == None:  # No nickname is found
        name = str(user_object[0])[:-5]  # Use username
    else:
        name = user_object[0].nick  # Use nickname
    msg = f"{str(interaction.user.mention)} has {str(change_player_coin(id, name, 0, True))} <:coin:910247623787700264>"
    await interaction.followup.send(msg)


@tree.command()
async def discord_coins_leaderboard(interaction: discord.Interaction):
    '''Return the discord coins leaderboard'''

   # await interaction.response.defer(ephemeral=False, thinking=True)

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
    embed = discord.Embed(
        color=0xffd700, title="Discord Coins Leaderboard", description=message)
    await interaction.followup.send(embed=embed)


@tree.command()
async def random_tank(interaction: discord.Interaction):
    '''Get a random tank'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    chosen_tank = random.choice(tanks)

    # Get emoji's source url stored in Discord
    # Png for static emojis and Gif for animated emojis
    if 'a:' in chosen_tank:
        emoji_code_split = chosen_tank[3:-1].split(':')
        img_link = 'https://cdn.discordapp.com/emojis/' + \
            emoji_code_split[1] + '.gif'
        tank_name = emoji_code_split[0].replace('_', ' ')[:-7].title()
    else:
        emoji_code_split = chosen_tank[2:-1].split(':')
        img_link = 'https://cdn.discordapp.com/emojis/' + \
            emoji_code_split[1] + '.png'
        tank_name = emoji_code_split[0].replace('_', ' ')[:-5].title()

    # Manual rename to avoid error
    if tank_name == "Default":
        tank_name = "Tank"
    elif tank_name == "Ufo Evolved":
        tank_name = "UFO Evolved"
    elif tank_name == "Ufo":
        tank_name = "UFO"

    # Get tank info
    awards_config = server_config['awards']
    for key, value in awards_config.items():
        try:
            if value['type'] == "skin_set":
                if value['name'] == tank_name:
                    description = value['description']
                    if value['rarity'] == 'common':
                        rarity_icon = "⭐"
                        color = 0x49C8FF
                    elif value['rarity'] == 'rare':
                        rarity_icon = "⭐⭐"
                        color = 0xCB6DFF
                    elif value['rarity'] == 'legendary':
                        rarity_icon = "⭐⭐⭐"
                        color = 0xFFDC5E
                    elif value['rarity'] == 'purchased':
                        rarity_icon = "💰"
                        color = 0x80FF7C
                    elif value['rarity'] == 'earned':
                        rarity_icon = "🏅"
                        color = 0xF1689D
            elif value['type'] == "skin":
                if value['name'] == tank_name:  # 3 bot skins
                    rarity_icon = ""
                    description = value['description']
                    color = 0x000000
                    break
        except:
            pass

    # Send
    embed = discord.Embed(
        title=f"{rarity_icon} {tank_name}", description=description, color=color)
    embed.set_image(url=img_link)
    await interaction.followup.send(embed=embed)


@tree.command()
@app_commands.describe(
    length='Length of the tank',
    barrel='Number of barrels to be equipped'
)
async def long(interaction: discord.Interaction, length: int, barrel: int = 1):
    '''Build your supercalifragilisticexpialidocious long tank equipped with as many barrels as you want!'''
    try:
        long_emoji = [
            "<:longtank_part1:991838180699541504>",
            "<:longtank_part2:991838184910626916>",
            "<:longtank_part3:991838189591470130>",
            "<:longtank_part4:991838192145793125>"
        ]
        if length < 0:
            length = 0
        if barrel < 0:
            barrel = 0
        if barrel > length:
            barrel = length

        def even_space(n, k):
            a = []
            for i in range(k):
                a.append(n // k)
            for i in range(n % k):
                a[i] += 1
            b = list(OrderedDict.fromkeys(a))
            global x, y
            x, y = b[0], b[1] if len(b) > 1 else ''
            for i in range(len(a)):
                a[i] = 'x' if a[i] == b[0] else 'y'
            s = ''.join(str(i) for i in a)
            return s

        def palindrome_check(str):
            return sum(map(lambda i: str.count(i) % 2, set(str))) <= 1

        def palindrome_rearrange(str):
            hmap = defaultdict(int)
            for i in range(len(str)):
                hmap[str[i]] += 1

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
        even_space_encode_palindrome = palindrome_rearrange(
            even_space_encode) if palindrome_check(even_space_encode) else even_space_encode

        even_space_encode_palindrome_decode = []
        for i in even_space_encode_palindrome:
            even_space_encode_palindrome_decode.append(i)
        for i in range(len(even_space_encode_palindrome_decode)):
            even_space_encode_palindrome_decode[i] = x if even_space_encode_palindrome_decode[i] == 'x' else y

        output_middle = ""
        for i in range(len(even_space_encode_palindrome_decode) - 1):
            output_middle += (long_emoji[1] *
                              even_space_encode_palindrome_decode[i] + long_emoji[2])
        output_middle += long_emoji[1] * \
            even_space_encode_palindrome_decode[-1]
        msg = f"{long_emoji[0]}{output_middle}{long_emoji[3]}"
        await interaction.response.send_message(f"```ansi\nThis is your \u001b[2;32ml\u001b[1;32m{'o'*length}\u001b[0m\u001b[2;32mng\u001b[0m tank!\n```\n{msg}")
    except:
        await interaction.response.send_message("The tank is too long to build!")


@tree.command()
@app_commands.describe(
    bet='The minimum bet is 1 coin'
)
async def slot(interaction: discord.Interaction, bet: int):
    '''Play the slot machine game!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    coin = ["<:coin1:910247623787700264>", "<:coin2:991444836869754950>",
            "<:coin3:976289335844434000>", "<:coin4:976289358200049704>", "<:coin5:976288324266373130>"]

    # Check how many coins the player has
    id = convert_mention_to_id(interaction.user.mention)
    user_object = await interaction.guild.query_members(user_ids=[id])
    if user_object[0].nick == None:  # No nickname is found
        name = str(user_object[0])[:-5]  # Use username
    else:
        name = user_object[0].nick  # Use nickname
    player_coin_before = change_player_coin(id, name, 0, True)

    if bet > player_coin_before:
        await interaction.followup.send(embed=discord.Embed(
            color=discord.Color.red(),
            title="SLOT MACHINE :slot_machine:",
            description=f"You don't have enough {coin[0]}"))
    elif bet <= 0:
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
            slots.append(random.choices(population=list(
                events.keys()), weights=events.values())[0])

        slot_embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:",
                                   description=f"**{'-' * 18}\n|{' {} |'.format(coins_loop) * 3}\n{'-' * 18}**")

        sent_embed = await interaction.followup.send(embed=slot_embed)
        current_slot_pics = [coins_loop] * 3
        for i in range(len(slots)):
            await asyncio.sleep(1.5)
            current_slot_pics[i] = slots[i]
            slot_results_str = f"**{'-' * 18}\n|"
            for thisSlot in current_slot_pics:
                slot_results_str += f" {thisSlot} |"
            new_slot_embed = discord.Embed(
                color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"{slot_results_str}\n{'-' * 18}**")
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
            gain = bet * multiplier
            change_player_coin(id, name, gain)
        else:
            res_2 = "-- **YOU LOST** --"
            loss = -bet
            change_player_coin(id, name, loss)

        player_coin_after = change_player_coin(id, name, 0, True)

        embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:",
                              description=f"{slot_results_str}\n{'-' * 18}**\n{res_2}")
        embed.add_field(name="Bet", value=f"{bet} {coin[0]}", inline=True)
        embed.add_field(name="Profit/Loss", value=f"{profit} {coin[0]}" + (
            f" ({multiplier}x)" if win else ""), inline=True)
        embed.add_field(
            name="Balance", value=f"{player_coin_after} {coin[0]}", inline=True)
        embed.add_field(name="Pay Table", value=f"{'{}'.format(coin[4]) * 3} - 32x\n{'{}'.format(coin[3]) * 3} - 16x\n{'{}'.format(coin[2]) * 3} - 12x\n{'{}'.format(coin[1]) * 3} - 8x\n{'{}'.format(coin[4]) * 2}:grey_question: - 8x\n{'{}'.format(coin[0]) * 3} - 4x\n{'{}'.format(coin[3]) * 2}:grey_question: - 4x\n{'{}'.format(coin[2]) * 2}:grey_question: - 3x\n{'{}'.format(coin[1]) * 2}:grey_question: - 2x\n{'{}'.format(coin[0]) * 2}:grey_question: - 1x", inline=False)
        await sent_embed.edit(embed=embed)


@tree.command()
async def memory(interaction: discord.Interaction):
    '''Test your memory by matching 2 tanks!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    b = [":white_large_square:" for i in range(16)]
    c = ['a1', 'b1', 'c1', 'd1', 'a2', 'b2', 'c2', 'd2',
         'a3', 'b3', 'c3', 'd3', 'a4', 'b4', 'c4', 'd4']
    a = random.sample(tanks, 8) * 2
    random.shuffle(a)
    board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
    answer = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {a[0]} {a[1]} {a[2]} {a[3]}\n:two: {a[4]} {a[5]} {a[6]} {a[7]}\n:three: {a[8]} {a[9]} {a[10]} {a[11]}\n:four: {a[12]} {a[13]} {a[14]} {a[15]}\n"

    def check(m):
        return (m.channel.id == interaction.channel.id and m.author == interaction.user)

    embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:",
                          description="Test your memory by matching 2 tanks!")
    embed.add_field(name="Time", value="<80s\n<100s\n≥100s", inline=True)
    embed.add_field(
        name="Reward", value="20 <:coin1:910247623787700264>\n10 <:coin1:910247623787700264>\n5 <:coin1:910247623787700264>", inline=True)
    embed.add_field(
        name="Controls", value="Type `s` to start the game\nType `q` to quit the game", inline=False)
    message = await interaction.followup.send(embed=embed)

    global gamestart
    gamestart = False

    while gamestart == False:
        try:
            msg = await client.wait_for("message", check=check, timeout=15)
            if str(msg.content.lower()) == "q":
                embed = discord.Embed(color=discord.Color.red(
                ), title="MEMORY GAME :brain:", description="You have quit the game")
                await message.edit(embed=embed)
                break
            if ((str(msg.content.lower()) == "s") or (str(msg.content.lower()) == "q")) == False:
                warn = await interaction.followup.send(":x: Invalid input has been entered :x:")
                await asyncio.sleep(2)
                await warn.delete()
            if str(msg.content.lower()) == "s":
                gamestart = True
                embed = discord.Embed(
                    color=0xffd700, title="MEMORY GAME :brain:", description=board)
                embed.add_field(
                    name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                await message.edit(embed=embed)
                start = timer()
        except asyncio.TimeoutError:
            embed = discord.Embed(color=discord.Color.red(
            ), title="MEMORY GAME :brain:", description="You did not start the game")
            await message.edit(embed=embed)
            break

        pair = 0
        flag = False
        while gamestart == True:
            try:
                msg = await client.wait_for("message", check=check, timeout=15)
                if str(msg.content.lower()) == "q":
                    board = answer
                    embed = discord.Embed(color=discord.Color.red(
                    ), title="MEMORY GAME :brain:", description=f"{board}\nYou have quit the game")
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
                        embed = discord.Embed(
                            color=0xffd700, title="MEMORY GAME :brain:", description=board)
                        embed.add_field(
                            name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                        await message.edit(embed=embed)
                    else:
                        y = c.index(str(msg.content.lower()))
                        b[y] = a[y]
                        flag = not flag
                        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                        embed = discord.Embed(
                            color=0xffd700, title="MEMORY GAME :brain:", description=board)
                        embed.add_field(
                            name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                        await message.edit(embed=embed)
                        await asyncio.sleep(1)
                        if a[x] == a[y]:
                            pair += 1
                        else:
                            b[x] = ":white_large_square:"
                            b[y] = ":white_large_square:"
                            board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                            embed = discord.Embed(
                                color=0xffd700, title="MEMORY GAME :brain:", description=board)
                            embed.add_field(
                                name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
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
                        embed = discord.Embed(
                            color=0xffd700, title="MEMORY GAME :brain:", description=f"{board}\n:tada: **YOU WON** :tada:")
                        embed.add_field(
                            name="Time", value=f"{time_diff:.2f}s", inline=True)
                        embed.add_field(
                            name="Reward", value=f"{reward} <:coin1:910247623787700264>", inline=True)
                        embed.add_field(
                            name="Balance", value=f"N.A. <:coin1:910247623787700264>", inline=True)
                        await message.edit(embed=embed)
                        break
                    await message.edit(embed=embed)
                else:
                    warn3 = await interaction.followup.send(":x: The card has already been flipped :x:")
                    await asyncio.sleep(2)
                    await warn3.delete()
            except asyncio.TimeoutError:
                board = answer
                embed = discord.Embed(color=discord.Color.red(
                ), title="MEMORY GAME :brain:", description=f"{board}\nThe game has timed out :hourglass:")
                await message.edit(embed=embed)
                break
        break


@tree.command()
@app_commands.describe(
    one_star='Number of one-star skin(s) owned',
    two_star='Number of two-star skin(s) owned',
    three_star='Number of three-star skin(s) owned'
)
async def get_crate_stats(interaction: discord.Interaction, one_star: int, two_star: int, three_star: int):
    '''Optimize the use of in game crates and Estimate the amount of coins'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    one_star_total = 0
    two_star_total = 0
    three_star_total = 0

    for key, value in server_config['awards'].items():
        try:
            if value['rarity'] == "common":
                one_star_total += 1
            elif value['rarity'] == "rare":
                two_star_total += 1
            elif value['rarity'] == "legendary":
                three_star_total += 1
        except:
            pass

    total = one_star_total + two_star_total + three_star_total
    one_star_weight, two_star_weight, three_star_weight = server_config[
        'lootbox_rarity_odds']['common'], server_config['lootbox_rarity_odds'][
            'rare'], server_config['lootbox_rarity_odds']['legendary']
    total_weight = one_star_total * one_star_weight + two_star_total * \
        two_star_weight + three_star_total * three_star_weight
    one_star_prob, two_star_prob, three_star_prob = one_star_weight / \
        total_weight, two_star_weight / total_weight, three_star_weight / total_weight

    basic_crate_price = server_config['lootbox_coin_cost']
    elite_crate_price = server_config['unique_lootbox_coin_cost']

    population_crate = list(range(1, total + 1))
    weights_crate = []
    for i in range(1, one_star_total + 1):
        weights_crate.append(one_star_prob)
    for j in range(1, two_star_total + 1):
        weights_crate.append(two_star_prob)
    for k in range(1, three_star_total + 1):
        weights_crate.append(three_star_prob)

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

        for i in range(0, 1000):
            basic_crates = 0
            prob = 1 - one_star_prob * a - two_star_prob * b - three_star_prob * c
            collected = set()
            for i in range(1, 1 + a):
                collected.add(i)
            for j in range(one_star_total + 1, one_star_total + 1 + b):
                collected.add(j)
            for k in range(one_star_total + two_star_total + 1,
                           one_star_total + two_star_total + 1 + c):
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
                        elif (one_star_total + 1) <= int(i) <= (
                                one_star_total + two_star_total):
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
            (expected_basic_crate_mean + expected_elite_crate_mean) > 1 else
            "is"
        ) + f" worth a **TOTAL** of **{expected_basic_crate_mean * basic_crate_price + expected_elite_crate_mean * elite_crate_price:,.0f} COINS <:coin:910247623787700264>**"

    def all(a, b, c):
        total_owned = a + b + c
        if (1 <= a <= one_star_total) and (0 <= b <= two_star_total) and (
                0 <= c <= three_star_total):
            if total_owned != total:
                return f"**1,000 SIMULATIONS** have been done based on the number of **{a} ONE-STAR :star:**, **{b} TWO-STAR :star::star:** and **{c} THREE-STAR :star::star::star: SKIN" + (
                    "S" if total_owned > 1 else
                    "") + f"** you have already owned:\n" + basic_or_elite(
                        a, b, c) + basic_and_elite_simulate(a, b, c)
            else:
                return f"You have already unlocked **ALL {total} UNIQUE SKINS**! :tada:"
        else:
            return ":x: **INVALID** data has been entered. Please try again. :x:"

    await interaction.followup.send(all(one_star, two_star, three_star))


@tree.command()
@app_commands.describe(
    season='Season 1 or later, default current'
)
async def season(interaction: discord.Interaction, season: int = -1):
    '''Return the season info, default current'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    if season < 1 or season > curr_season:
        season = curr_season
    embed = discord.Embed()
    embed.title = "Rocket Bot Royale 🚀"
    embed.add_field(name="📓 ***Season Info***", value=f"```ansi\n{'Season: ':>10}{str(season)}\n{'Start: ':>10}{season_info(season)[0]}\n{'End: ':>10}{season_info(season)[1]}\n{'Duration: ':>10}{season_info(season)[2]}\n{'Status: ':>10}{season_info(season)[3]}\n" + (
        f"{'Ends in: ':>10}{season_info(season)[4]}" if season == curr_season else "") + "```")
    await interaction.followup.send(embed=embed)


@tree.command()
async def random_bot_name(interaction: discord.Interaction):
    '''Generate a random bot name.'''

    adjective = [
        "gray",
        "brown",
        "red",
        "pink",
        "crimson",
        "carnelian",
        "orange",
        "yellow",
        "ivory",
        "cream",
        "green",
        "viridian",
        "aquamarine",
        "cyan",
        "blue",
        "cerulean",
        "azure",
        "indigo",
        "navy",
        "violet",
        "purple",
        "lavender",
        "magenta",
        "rainbow",
        "iridescent",
        "spectrum",
        "prism",
        "bold",
        "vivid",
        "pale",
        "clear",
        "glass",
        "translucent",
        "misty",
        "dark",
        "light",
        "gold",
        "silver",
        "copper",
        "bronze",
        "steel",
        "iron",
        "brass",
        "mercury",
        "zinc",
        "chrome",
        "platinum",
        "titanium",
        "nickel",
        "lead",
        "pewter",
        "rust",
        "metal",
        "stone",
        "quartz",
        "granite",
        "marble",
        "alabaster",
        "agate",
        "jasper",
        "pebble",
        "pyrite",
        "crystal",
        "geode",
        "obsidian",
        "mica",
        "flint",
        "sand",
        "gravel",
        "boulder",
        "basalt",
        "ruby",
        "beryl",
        "scarlet",
        "citrine",
        "sulpher",
        "topaz",
        "amber",
        "emerald",
        "malachite",
        "jade",
        "abalone",
        "lapis",
        "sapphire",
        "diamond",
        "peridot",
        "gem",
        "jewel",
        "bevel",
        "coral",
        "jet",
        "ebony",
        "wood",
        "tree",
        "cherry",
        "maple",
        "cedar",
        "branch",
        "bramble",
        "rowan",
        "ash",
        "fir",
        "pine",
        "cactus",
        "alder",
        "grove",
        "forest",
        "jungle",
        "palm",
        "bush",
        "mulberry",
        "juniper",
        "vine",
        "ivy",
        "rose",
        "lily",
        "tulip",
        "daffodil",
        "honeysuckle",
        "fuschia",
        "hazel",
        "walnut",
        "almond",
        "lime",
        "lemon",
        "apple",
        "blossom",
        "bloom",
        "crocus",
        "rose",
        "buttercup",
        "dandelion",
        "iris",
        "carnation",
        "fern",
        "root",
        "branch",
        "leaf",
        "seed",
        "flower",
        "petal",
        "pollen",
        "orchid",
        "mangrove",
        "cypress",
        "sequoia",
        "sage",
        "heather",
        "snapdragon",
        "daisy",
        "mountain",
        "hill",
        "alpine",
        "chestnut",
        "valley",
        "glacier",
        "forest",
        "grove",
        "glen",
        "tree",
        "thorn",
        "stump",
        "desert",
        "canyon",
        "dune",
        "oasis",
        "mirage",
        "well",
        "spring",
        "meadow",
        "field",
        "prairie",
        "grass",
        "tundra",
        "island",
        "shore",
        "sand",
        "shell",
        "surf",
        "wave",
        "foam",
        "tide",
        "lake",
        "river",
        "brook",
        "stream",
        "pool",
        "pond",
        "sun",
        "sprinkle",
        "shade",
        "shadow",
        "rain",
        "cloud",
        "storm",
        "hail",
        "snow",
        "sleet",
        "thunder",
        "lightning",
        "wind",
        "hurricane",
        "typhoon",
        "dawn",
        "sunrise",
        "morning",
        "noon",
        "twilight",
        "evening",
        "sunset",
        "midnight",
        "night",
        "sky",
        "star",
        "stellar",
        "comet",
        "nebula",
        "quasar",
        "solar",
        "lunar",
        "planet",
        "meteor",
        "sprout",
        "pear",
        "plum",
        "kiwi",
        "berry",
        "apricot",
        "peach",
        "mango",
        "pineapple",
        "coconut",
        "olive",
        "ginger",
        "root",
        "plain",
        "fancy",
        "stripe",
        "spot",
        "speckle",
        "spangle",
        "ring",
        "band",
        "blaze",
        "paint",
        "pinto",
        "shade",
        "tabby",
        "brindle",
        "patch",
        "calico",
        "checker",
        "dot",
        "pattern",
        "glitter",
        "glimmer",
        "shimmer",
        "dull",
        "dust",
        "dirt",
        "glaze",
        "scratch",
        "quick",
        "swift",
        "fast",
        "slow",
        "clever",
        "fire",
        "flicker",
        "flash",
        "spark",
        "ember",
        "coal",
        "flame",
        "chocolate",
        "vanilla",
        "sugar",
        "spice",
        "cake",
        "pie",
        "cookie",
        "candy",
        "caramel",
        "spiral",
        "round",
        "jelly",
        "square",
        "narrow",
        "long",
        "short",
        "small",
        "tiny",
        "big",
        "giant",
        "great",
        "atom",
        "peppermint",
        "mint",
        "butter",
        "fringe",
        "rag",
        "quilt",
        "truth",
        "lie",
        "holy",
        "curse",
        "noble",
        "sly",
        "brave",
        "shy",
        "lava",
        "foul",
        "leather",
        "fantasy",
        "keen",
        "luminous",
        "feather",
        "sticky",
        "gossamer",
        "cotton",
        "rattle",
        "silk",
        "satin",
        "cord",
        "denim",
        "flannel",
        "plaid",
        "wool",
        "linen",
        "silent",
        "flax",
        "weak",
        "valiant",
        "fierce",
        "gentle",
        "rhinestone",
        "splash",
        "north",
        "south",
        "east",
        "west",
        "summer",
        "winter",
        "autumn",
        "spring",
        "season",
        "equinox",
        "solstice",
        "paper",
        "motley",
        "torch",
        "ballistic",
        "rampant",
        "shag",
        "freckle",
        "wild",
        "free",
        "chain",
        "sheer",
        "crazy",
        "mad",
        "candle",
        "ribbon",
        "lace",
        "notch",
        "wax",
        "shine",
        "shallow",
        "deep",
        "bubble",
        "harvest",
        "fluff",
        "venom",
        "boom",
        "slash",
        "rune",
        "cold",
        "quill",
        "love",
        "hate",
        "garnet",
        "zircon",
        "power",
        "bone",
        "void",
        "horn",
        "glory",
        "cyber",
        "nova",
        "hot",
        "helix",
        "cosmic",
        "quark",
        "quiver",
        "holly",
        "clover",
        "polar",
        "regal",
        "ripple",
        "ebony",
        "wheat",
        "phantom",
        "dew",
        "chisel",
        "crack",
        "chatter",
        "laser",
        "foil",
        "tin",
        "clever",
        "treasure",
        "maze",
        "twisty",
        "curly",
        "fortune",
        "fate",
        "destiny",
        "cute",
        "slime",
        "ink",
        "disco",
        "plume",
        "time",
        "psychadelic",
        "relic",
        "fossil",
        "water",
        "savage",
        "ancient",
        "rapid",
        "road",
        "trail",
        "stitch",
        "button",
        "bow",
        "nimble",
        "zest",
        "sour",
        "bitter",
        "phase",
        "fan",
        "frill",
        "plump",
        "pickle",
        "mud",
        "puddle",
        "pond",
        "river",
        "spring",
        "stream",
        "battle",
        "arrow",
        "plume",
        "roan",
        "pitch",
        "tar",
        "cat",
        "dog",
        "horse",
        "lizard",
        "bird",
        "fish",
        "saber",
        "scythe",
        "sharp",
        "soft",
        "razor",
        "neon",
        "dandy",
        "swamp",
        "marsh",
        "bog",
        "peat",
        "moor",
        "muck",
        "mire",
        "grave",
        "fair",
        "just",
        "brick",
        "puzzle",
        "skitter",
        "prong",
        "fork",
        "dent",
        "dour",
        "warp",
        "luck",
        "coffee",
        "split",
        "chip",
        "hollow",
        "heavy",
        "legend",
        "hickory",
        "mesquite",
        "nettle",
        "rogue",
        "charm",
        "prickle",
        "bead",
        "sponge",
        "whip",
        "bald",
        "frost",
        "fog",
        "oil",
        "veil",
        "cliff",
        "volcano",
        "rift",
        "maze",
        "proud",
        "dew",
        "mirror",
        "shard",
        "salt",
        "pepper",
        "honey",
        "thread",
        "bristle",
        "ripple",
        "glow",
        "zenith"
    ]

    noun = [
        "head",
        "crest",
        "crown",
        "tooth",
        "fang",
        "horn",
        "frill",
        "skull",
        "bone",
        "tongue",
        "throat",
        "voice",
        "nose",
        "snout",
        "chin",
        "eye",
        "sight",
        "seer",
        "speaker",
        "singer",
        "song",
        "chanter",
        "howler",
        "chatter",
        "shrieker",
        "shriek",
        "jaw",
        "bite",
        "biter",
        "neck",
        "shoulder",
        "fin",
        "wing",
        "arm",
        "lifter",
        "grasp",
        "grabber",
        "hand",
        "paw",
        "foot",
        "finger",
        "toe",
        "thumb",
        "talon",
        "palm",
        "touch",
        "racer",
        "runner",
        "hoof",
        "fly",
        "flier",
        "swoop",
        "roar",
        "hiss",
        "hisser",
        "snarl",
        "dive",
        "diver",
        "rib",
        "chest",
        "back",
        "ridge",
        "leg",
        "legs",
        "tail",
        "beak",
        "walker",
        "lasher",
        "swisher",
        "carver",
        "kicker",
        "roarer",
        "crusher",
        "spike",
        "shaker",
        "charger",
        "hunter",
        "weaver",
        "crafter",
        "binder",
        "scribe",
        "muse",
        "snap",
        "snapper",
        "slayer",
        "stalker",
        "track",
        "tracker",
        "scar",
        "scarer",
        "fright",
        "killer",
        "death",
        "doom",
        "healer",
        "saver",
        "friend",
        "foe",
        "guardian",
        "thunder",
        "lightning",
        "cloud",
        "storm",
        "forger",
        "scale",
        "hair",
        "braid",
        "nape",
        "belly",
        "thief",
        "stealer",
        "reaper",
        "giver",
        "taker",
        "dancer",
        "player",
        "gambler",
        "twister",
        "turner",
        "painter",
        "dart",
        "drifter",
        "sting",
        "stinger",
        "venom",
        "spur",
        "ripper",
        "devourer",
        "knight",
        "lady",
        "lord",
        "queen",
        "king",
        "master",
        "mistress",
        "prince",
        "princess",
        "duke",
        "dutchess",
        "samurai",
        "ninja",
        "knave",
        "servant",
        "sage",
        "wizard",
        "witch",
        "warlock",
        "warrior",
        "jester",
        "paladin",
        "bard",
        "trader",
        "sword",
        "shield",
        "knife",
        "dagger",
        "arrow",
        "bow",
        "fighter",
        "bane",
        "follower",
        "leader",
        "scourge",
        "watcher",
        "cat",
        "panther",
        "tiger",
        "cougar",
        "puma",
        "jaguar",
        "ocelot",
        "lynx",
        "lion",
        "leopard",
        "ferret",
        "weasel",
        "wolverine",
        "bear",
        "raccoon",
        "dog",
        "wolf",
        "kitten",
        "puppy",
        "cub",
        "fox",
        "hound",
        "terrier",
        "coyote",
        "hyena",
        "jackal",
        "pig",
        "horse",
        "donkey",
        "stallion",
        "mare",
        "zebra",
        "antelope",
        "gazelle",
        "deer",
        "buffalo",
        "bison",
        "boar",
        "elk",
        "whale",
        "dolphin",
        "shark",
        "fish",
        "minnow",
        "salmon",
        "ray",
        "fisher",
        "otter",
        "gull",
        "duck",
        "goose",
        "crow",
        "raven",
        "bird",
        "eagle",
        "raptor",
        "hawk",
        "falcon",
        "moose",
        "heron",
        "owl",
        "stork",
        "crane",
        "sparrow",
        "robin",
        "parrot",
        "cockatoo",
        "carp",
        "lizard",
        "gecko",
        "iguana",
        "snake",
        "python",
        "viper",
        "boa",
        "condor",
        "vulture",
        "spider",
        "fly",
        "scorpion",
        "heron",
        "toucan",
        "bee",
        "wasp",
        "hornet",
        "rabbit",
        "bunny",
        "hare",
        "brow",
        "mustang",
        "ox",
        "piper",
        "soarer",
        "moth",
        "mask",
        "hide",
        "hero",
        "antler",
        "chill",
        "chiller",
        "gem",
        "ogre",
        "myth",
        "elf",
        "fairy",
        "pixie",
        "dragon",
        "griffin",
        "unicorn",
        "pegasus",
        "sprite",
        "fancier",
        "chopper",
        "slicer",
        "skinner",
        "butterfly",
        "legend",
        "wanderer",
        "rover",
        "raver",
        "loon",
        "lancer",
        "glass",
        "glazer",
        "flame",
        "crystal",
        "lantern",
        "lighter",
        "cloak",
        "bell",
        "ringer",
        "keeper",
        "centaur",
        "bolt",
        "catcher",
        "whimsey",
        "quester",
        "rat",
        "mouse",
        "serpent",
        "wyrm",
        "gargoyle",
        "thorn",
        "whip",
        "rider",
        "spirit",
        "sentry",
        "bat",
        "beetle",
        "burn",
        "cowl",
        "stone",
        "gem",
        "collar",
        "mark",
        "grin",
        "scowl",
        "spear",
        "razor",
        "edge",
        "seeker",
        "jay",
        "ape",
        "monkey",
        "gorilla",
        "koala",
        "kangaroo",
        "yak",
        "sloth",
        "ant",
        "roach",
        "seed",
        "eater",
        "razor",
        "shirt",
        "face",
        "goat",
        "mind",
        "shift",
        "rider",
        "face",
        "mole",
        "vole",
        "pirate",
        "llama",
        "stag",
        "bug",
        "cap",
        "boot",
        "drop",
        "hugger",
        "sargent",
        "snagglefoot",
        "carpet",
        "curtain"
    ]

    generated_random_bot_name = random.choice(
        noun).capitalize() + random.choice(adjective)
    await interaction.response.send_message(generated_random_bot_name)


@tree.command()
@app_commands.describe(
    article='The article you want to look up. Make sure capitalization is correct!'
)
async def fandom(interaction: discord.Interaction, article: str):
    '''Fetch any articles from Rocket Bot Royale fandom wiki here!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    p = rocketbotroyale.page(article)
    try:
        page1 = page(title=article)
        sent_embed = await interaction.followup.send(embed=discord.Embed(description="Fetching page..."))
        output = discord.Embed(
            color=0xffd700,
            title=page1.title,
            description=page1.summary,
            url=f"https://rocketbotroyale.fandom.com/wiki/{page1.title}".replace(
                " ", "_"),
            timestamp=datetime.datetime.utcnow())
        list_of_images = p.images
        png_or_gif = [x for x in list_of_images if ".png" in x or ".gif" in x]
        set_image = "https://static.wikia.nocookie.net/rocketbotroyale/images/c/c4/Slide1_mainpage.png/revision/latest?cb=20220712121433" if len(
            png_or_gif) == 0 else png_or_gif[0]
        output.set_image(url=set_image)
        output.set_thumbnail(
            url="https://static.wikia.nocookie.net/rocketbotroyale/images/e/e6/Site-logo.png")
        output.set_footer(
            text="All information is gathered through fandom.com")
        await sent_embed.edit(embed=output)
    except:
        await interaction.followup.send(embed=discord.Embed(color=0xff0000, description=f':x: "{article}" is not found. Make sure capitalization is correct!', timestamp=datetime.datetime.utcnow()))


@tree.command(guild=discord.Object(id=962142361935314996))
async def sync_commands(interaction: discord.Interaction):
    await tree.sync()
    await tree.sync(guild=discord.Object(id=962142361935314996))
    await interaction.response.send_message("Commands synced.")


def main():
    try:
        client.run(discord_token)
    except:
        os.system("kill 1")


if (__name__ == "__main__"):
    main()
""
