import random
import textwrap
import aiohttp
import discord
import json
import asyncio
import typing
import os
import io
import datetime
import time
import timeago
import re
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.cbook import boxplot_stats
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.gridspec import GridSpec
from scipy.interpolate import PchipInterpolator
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
    discord_token = os.environ["discord_token"]
    rocketbot_user = os.environ["rocketbot_username"]
    rocketbot_pass = os.environ["rocketbot_password"]
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
rocketbotroyale = MediaWiki(url="https://rocketbotroyale.fandom.com/api.php")

# List contains all tank emojis for random_tank and memory command
tanks = [
    "<:pumpkin_tank:1022568065034104936>",
    "<a:pumpkin_evolved_tank_a:1022572757860499486>",
    "<:eyeball_tank:1022568661745143908>",
    "<a:skull_tank_a:1022574941591306362>",
    "<:snowman_tank:1012941920844132362>",
    "<:snowman_evolved_tank:1012941924094713917>",
    "<:snowmobile_tank:1012941917337698375>",
    "<:icy_tank:1012941914254876794>",
    "<:brain_bot_tank:1006531910224322630>",
    "<:mine_bot_tank:1006532474945417216>",
    "<:bot_tank:917467970182189056>",
    "<:default_tank:996465659812774040>",
    "<:beta_tank:997947350943277106>",
    "<:canon_tank:997951207840686162>",
    "<:hot_dog_tank:997955038435614934>",
    "<a:wave_tank_a:1001203703325397033>",
    "<:zig_tank:997954180717215975>",
    "<:blade_tank:997947874715385856>",
    "<:buggy_tank:997948966933119016>",
    "<:burger_evolved_tank:997950412348989562>",
    "<:burger_tank:997950506976694302>",
    "<:catapult_evolved_tank:997951715284365323>",
    "<:catapult_tank:997951809282912346>",
    "<a:crab_evolved_tank_a:1001203931713654864>",
    "<a:crab_tank_a:1001203874469793822>",
    "<:cyclops_tank:997952308333793322>",
    "<:diamond_tank:997952379595010048>",
    "<a:dozer_evolved_tank_a:1001204001053876374>",
    "<:dozer_tank:997952516501278760>",
    "<:fork_tank:997952581408129084>",
    "<:fries_tank:997952688656494672>",
    "<:gears_tank:997952760127434782>",
    "<:hay_tank:997952813386715148>",
    "<:hollow_tank:997952878142562384>",
    "<:medic_tank:997953168673619978>",
    "<:mixer_tank:997953233098113054>",
    "<:pagliacci_tank:997953348097560628>",
    "<:pail_tank:997953413717438575>",
    "<a:pistons_tank_a:1001208481300369608>",
    "<a:reactor_tank_a:1024935111461969990>",
    "<a:spider_evolved_tank_a:1001204256193396856>",
    "<a:spider_tank_a:1001204193887002704>",
    "<:spike_tank:997953736041308280>",
    "<:square_tank:997953791217377381>",
    "<:trap_tank:997953904610381834>",
    "<:tread_tank:997953970213494905>",
    "<:tub_tank:997954029902626886>",
    "<:tubdown_tank:997954078535598270>",
    "<:concave_tank:997951897749176450>",
    "<:crawler_tank:997952124279324753>",
    "<:log_tank:997953009910829198>",
    "<:long_tank:997953087006330971>",
    "<a:UFO_evolved_tank_a:1012268475626033174>",
    "<a:UFO_tank_a:1012268306482343936>",
    "<a:miner_tank_a:1003099245777276952>",
    "<:rover_tank:1003014762327716042>",
    "<a:bug_tank_a:1001203807893590168>",
    "<:moai_tank:1006528445355917394>",
    "<:128bit_tank:1073330000868163624>",
    "<:16bit_tank:1073329502148644904>",
    "<:32bit_tank:1073329509824204960>",
    "<:8bit_tank:1073329497451008140>",
    "<a:army1_tank_a:1080827324133539891>",
    "<a:army2_tank_a:1080827333453303818>",
    "<a:army3_tank_a:1080827342982750208>",
    "<a:army4_tank_a:1080827352977776640>",
    "<:champion_s13_tank:1051208428263067728>",
    "<:champion_s14_tank:1063549554798120960>",
    "<:champion_s15_tank:1073329544410443897>",
    "<:giftbox_tank:1073329550492172388>",
    "<:gingerbread_tank:1073330256578093208>",
    "<:handheld_tank:1073329559694495854>",
    "<:pirate_tank:1073329566657032282>",
    "<:pixel_tank:1073329572218671266>",
    "<:sailboat_tank:1073329578308812871>",
    "<:snowflake_tank:1073330011597197384>",
    "<:snowglobe_tank:1073330262441734164>",
    "<:tree_evolved_tank:1073330265742643344>",
    "<:tree_tank:1073329598542123018>",
    "<:viking_evolved_tank:1073329604393173023>",
    "<:viking_tank:1073329612513366087>",
    "<a:DualMini_HT_tank_a:1080827376960815205>",
    "<a:DualWide_HT_tank_a:1080827384015634432>",
    "<a:Evolved_TriLine_tank_a:1080827392785924116>",
    "<a:TriLine_HT_tank_a:1080827401472331806>",
    "<a:champion_s16_tank_a:1080827366957400146>",
]

os.system("clear")


def season_info(season):
    season_durations, season_start_numbers, season_start_timestamps = (
        [] for i in range(3)
    )
    for key in server_config["season_definitions"]:
        season_durations.append(key["season_duration"])
        season_start_numbers.append(key["season_start_number"])
        season_start_timestamps.append(key["season_start_timestamp"])

    season_index = np.searchsorted(season_start_numbers, season + 1) - 1

    season_start_timestamp = (
        season_start_timestamps[season_index]
        + (season - season_start_numbers[season_index]
           ) * season_durations[season_index]
    )
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
        season_difference = (
            current_timestamp - season_start_timestamp
        ) / season_duration
        season_seconds_remaining = (
            ceil(season_difference) - season_difference
        ) * season_duration
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
        "bloody",
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
    if id in db["discord_coins"]:  # Old id
        db["discord_coins"][id]["name"] = name  # Update nickname
    else:  # New id
        db["discord_coins"][id] = {  # New record
            "name": name,
            "coins": 500,
            "coins_change": 0,
            "inventory": {},
        }
    db["discord_coins"][id]["coins"] += coins
    db["discord_coins"][id]["coins_change"] += coins
    if request == True:
        return db["discord_coins"][id]["coins"]


def convert_mention_to_id(mention):
    id = mention[2:-1]
    if id.startswith("!"):
        id = id[1:]
    return id


async def refresh_config():
    """Refresh game configuration every 10 minutes"""
    global server_config

    while True:
        response = await rocketbot_client.get_config()
        server_config = json.loads(response["payload"])

        global curr_season, league_range_orig, league_range, league_names, league_colors_orig, league_colors
        curr_season = server_config["season"]
        league_range_orig = [
            server_config["trophy_tiers"][league]["maximum_rank"]
            for league in range(len(server_config["trophy_tiers"]) - 1)
        ]
        league_range = [
            league_range_orig[i] if j == 0 else league_range_orig[i] + 1
            for i in range(len(league_range_orig))
            for j in range(min(len(league_range_orig) - i + 1, 2))
        ]
        league_names = [
            server_config["trophy_tiers"][league]["name"]
            for league in range(len(server_config["trophy_tiers"]))
        ]
        league_colors_orig = [
            f"#{server_config['trophy_tiers'][league]['color']}"
            for league in range(len(server_config["trophy_tiers"]))
        ]
        league_colors = [
            color for color in league_colors_orig for _ in (0, 1)][1:-1]

        # Remove past season keys
        for i in db.prefix("tankkings"):
            if str(curr_season) not in i:
                del db[i]

        await asyncio.sleep(600)


async def refresh_config_2():
    """Refresh game configuration every 10 minutes"""
    global server_config_2

    while True:
        response = await moonrock_client.get_config()
        server_config_2 = json.loads(response["payload"])

        # Remove past season keys
        global curr_season_2
        curr_season_2 = server_config_2["season"]
        for i in db.prefix("trophies"):
            if str(curr_season_2) not in i:
                del db[i]

        await asyncio.sleep(600)


@client.event
async def on_message(message: discord.message):
    if (
        "moyai" in message.content.lower()
        or "🗿" in message.content.lower()
        or "moai" in message.content.lower()
    ):
        await message.add_reaction("🗿")
    if "!idea" in message.content.lower():
        await message.add_reaction("<:upvote:910250647264329728>")
        await message.add_reaction("<:downvote:910250215217459281>")
    # (caps with spaces >= 10) or (repeated character or number >=10)
    if bool(re.search(r"\w*[A-Z ]{10}", message.content)) or bool(
        re.search(r"(?:([a-zA-Z0-9])\1{9,})", message.content)
    ):
        await message.reply("Calm down!")


@client.event
async def on_ready():
    """Called when the discord client is ready."""

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


@tree.commamd()
async def tank(interaction: discord.Interaction):
    """tank"""

    await interaction.response.defer(ephemeral=False, thinking=True)
    await interaction.followup.send(
            embed=discord.Embed(
                description="Dude... your balance isn't negative", color=0xFF0000
            )

@tree.command()
async def double_or_half(interaction: discord.Interaction):
    """Helps you get out of a rut if your balance is negative."""

    await interaction.response.defer(ephemeral=False, thinking=True)

    id = convert_mention_to_id(interaction.user.mention)
    user_object = await interaction.guild.query_members(user_ids=[id])
    if user_object[0].nick == None:  # No nickname is found
        name = str(user_object[0])[:-5]  # Use username
    else:
        name = user_object[0].nick  # Use nickname

    coins = change_player_coin(id, name, 0, True)

    if coins > 0:
        await interaction.followup.send(
            embed=discord.Embed(
                description="Dude... your balance isn't negative", color=0xFF0000
            )
        )
    else:
        events = {True: 2, False: 1}
        success = random.choices(
            population=list(events.keys()), weights=events.values(), k=1
        )[0]

        if success:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{interaction.user} tries their hand at resolving their debt...",
                    description=f"Your debt has been halved! New balance: {change_player_coin(id, name, -1 * int(coins / 2), True)}<:coin1:910247623787700264>",
                    color=0x00FF00,
                )
            )
        else:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{interaction.user} tries their hand at resolving their debt...",
                    description=f"Lol. Your debt has been doubled. New Balance: {change_player_coin(id, name, coins, True)}<:coin1:910247623787700264>",
                    color=0xFF0000,
                )
            )


@tree.command()
@app_commands.describe(
    mode="Leaderboard by 🏆 Trophies/🧊 Points/🎉 Wins/💀 Player Kills/🤖 Bot Kills",
    changes="Only available for Top 50 records of current season, changes since last command used",
    season="🏆 Trophies: Season 10 or later / Others: Season 0 or later, default current",
)
async def leaderboard_rocket_bot_royale(
    interaction: discord.Interaction,
    mode: typing.Literal[
        "🏆 Trophies", "🧊 Points", "🎉 Wins", "💀 Player Kills", "🤖 Bot Kills"
    ],
    changes: typing.Literal["Shown", "Hidden"],
    season: int = -1,
):
    """Return the specified season leaderboard of Rocket Bot Royale by various modes, default current"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    # Emojis for different modes
    emojis = {
        "trophies": "🏆 ",
        "points": "🧊 ",
        "wins": "🎉 ",
        "player kills": "💀 ",
        "bot kills": "🤖 ",
    }

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in [
            "◀️",
            "▶️",
            "⏪",
            "⏹️",
        ]
        # This makes sure nobody except the command sender can interact with the "menu"

    curr_season = server_config["season"]

    # Reassign season if unreasonable
    if mode == "🏆 Trophies":
        if season < 10 or season > curr_season:
            season = curr_season
    else:
        if season < 0 or season > curr_season:
            season = curr_season

    # Season Info
    global season_info_2
    season_info_2 = (
        f"📓 ***Season Info***:\n```ansi\n{'Start: ':>10}{season_info(season)[0]}\n{'End: ':>10}{season_info(season)[1]}\n{'Duration: ':>10}{season_info(season)[2]}\n{'Status: ':>10}{season_info(season)[3]}\n"
        + (
            f"{'Ends in: ':>10}{season_info(season)[4]}\n"
            if season == curr_season
            else ""
        )
        + "```"
    )

    # Hide changes for past seasons
    if season < curr_season:
        changes = "Hidden"

    # Get leaderboard info
    if changes == "Shown":
        limit = 100
    elif changes == "Hidden":
        limit = 25

    response = await rocketbot_client.query_leaderboard(
        season,
        f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
        limit,
    )
    records = json.loads(response["payload"])["records"]
    start = records[0]["rank"]
    end = records[len(records) - 1]["rank"]
    cursor_dict = dict()
    cursor_dict[1] = ""

    try:
        cursor_dict[2] = json.loads(response["payload"])["next_cursor"]
        next_cursor = True
    except:
        next_cursor = False

    if changes == "Shown":
        # Add to repl.it's database for new keys
        new_key_flag = False
        if (
            f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"
            not in db.keys()
        ):
            value = dict()
            for record in records:
                value[record["owner_id"]] = {
                    "rank": record["rank"],
                    "score": record["score"],
                }
            value[
                "last_update_time"
            ] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record["leaderboard_id"]] = value
            new_key_flag = True

        if mode == "🏆 Trophies":  # By Trophies
            split = []
            tier = []
            for i in range(5):
                split.append(server_config["trophy_tiers"][i]["maximum_rank"])
                tier.append(server_config["trophy_tiers"][i]["name"].upper())
            tier_color_code = ["35", "36", "33", "34", "31"]

            # Using f-string spacing to pretty print the leaderboard labels (bold)
            message = ""
            label = f"{season_info_2}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'—' * 46}\n"

            # Using f-string spacing to pretty print the leaderboard
            if len(records) < 50:  # Prevent index out of range error
                records_range = len(records)
            else:
                records_range = 50

            for i in range(records_range):
                # Determine which tier the player belongs to
                tier_index = np.searchsorted(split, records[i]["rank"])

                # Rank difference
                try:
                    rank_diff = (
                        records[i]["rank"]
                        - db[records[i]["leaderboard_id"]][records[i]["owner_id"]][
                            "rank"
                        ]
                    )
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
                message += (
                    (
                        "\u001b[1;33m"
                        if records[i]["metadata"]["has_season_pass"]
                        else ""
                    )
                    + f"{records[i]['username']:<20}"
                    + (
                        "\u001b[0m "
                        if records[i]["metadata"]["has_season_pass"]
                        else " "
                    )
                )

                # Trophies difference
                try:
                    trophies_diff = (
                        records[i]["score"]
                        - db[records[i]["leaderboard_id"]][records[i]["owner_id"]][
                            "score"
                        ]
                    )
                    if trophies_diff < 0:
                        trophies_diff_2 = (
                            f"\u001b[2;31m-{abs(trophies_diff):<4}\u001b[0m"
                        )
                    elif trophies_diff > 0:
                        trophies_diff_2 = (
                            f"\u001b[2;32m+{abs(trophies_diff):<4}\u001b[0m"
                        )
                    else:
                        trophies_diff_2 = f"{'-':^5}"
                except:
                    # Not found in repl.it's database
                    trophies_diff_2 = f"{'':<5}"

                # Trophies
                message += f"{emojis[mode.lower()[2:]] + '{:<6,.0f}'.format(records[i]['score'])}{trophies_diff_2}\n"

                # Tier separators (bold)
                if records[i]["rank"] in split and records[i]["rank"] % 25 != 0:
                    tier_name_with_space = " " + tier[tier_index] + " "
                    message += f"\u001b[1;{tier_color_code[tier_index]}m{tier_name_with_space.center(45, '─')}\u001b[0m\n"

        else:  # By Points/Wins/Player Kills/Bot Kills
            # Using f-string spacing to pretty print the leaderboard labels (bold)
            message = ""
            label = f"{season_info_2}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {mode[2:]}:\u001b[0m\n{'—' * 48}\n"

            # Using f-string spacing to pretty print the leaderboard
            if len(records) < 50:  # Prevent index out of range error
                records_range = len(records)
            else:
                records_range = 50

            for i in range(records_range):
                # Rank difference
                try:
                    rank_diff = (
                        records[i]["rank"]
                        - db[records[i]["leaderboard_id"]][records[i]["owner_id"]][
                            "rank"
                        ]
                    )
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
                        (
                            "\u001b[1;33m"
                            if records[i]["metadata"]["has_season_pass"]
                            else ""
                        )
                        + f"{records[i]['username']:<20}"
                        + (
                            "\u001b[0m "
                            if records[i]["metadata"]["has_season_pass"]
                            else " "
                        )
                    )
                except:
                    message += f"{records[i]['username']:<20} "  # Name only

                # Points/Wins/Player Kills/Bot Kills difference
                try:
                    non_trophies_diff = (
                        records[i]["score"]
                        - db[records[i]["leaderboard_id"]][records[i]["owner_id"]][
                            "score"
                        ]
                    )
                    if non_trophies_diff > 0:
                        non_trophies_diff_2 = (
                            f"\u001b[2;32m+{abs(non_trophies_diff):<5}\u001b[0m"
                        )
                    else:
                        non_trophies_diff_2 = f"{'-':^6}"
                except:
                    # Not found ind repl.it's database
                    non_trophies_diff_2 = f"{'':<6}"

                # Points/Wins/Player Kills/Bot Kills
                message += f"{emojis[mode.lower()[2:]] + '{:<8,.0f}'.format(records[i]['score'])}{non_trophies_diff_2}\n"

        # Split message
        cannot_split = False  # Prevent index out of range error
        split_line_number = 26 if mode == "🏆 Trophies" else 24  # Evenly split message
        try:  # In case there are not enough records
            message1 = message[
                : [m.start() for m in re.finditer(r"\n", message)][split_line_number]
            ]
            message2 = (
                message[
                    (
                        [m.start() for m in re.finditer(r"\n", message)][
                            split_line_number
                        ]
                    )
                    + 1:
                ]
                + (
                    "\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n"
                    if mode == "🏆 Trophies"
                    else ""
                )
                + "```"
            )
        except:
            cannot_split = True

        # Send
        if cannot_split == False:
            cur_page = 1
            embed_init = discord.Embed(
                title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {'Player Kills' if mode == 'Kills' else mode.replace('_', ' ').title()}):",
                description=label
                + message1
                + (
                    "\n\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n"
                    if mode == "🏆 Trophies"
                    else ""
                )
                + "```",
            )
            embed_init.set_footer(
                text=f"""Page 1/2:  1 to 25 | Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
            )
            msg = await interaction.followup.send(embed=embed_init)
            msg2 = await interaction.followup.send(
                embed=discord.Embed(description="To be edited...")
            )

            for reaction_emoji in ["◀️", "▶️", "⏹️"]:
                await msg.add_reaction(reaction_emoji)

            while True:
                try:
                    reaction, user = await client.wait_for(
                        "reaction_add", timeout=15, check=check
                    )
                    # Waiting for a reaction to be added - times out after 15 seconds

                    if str(reaction.emoji) == "▶️" and cur_page == 1:  # Go to Page 2
                        cur_page += 1
                        embed_first = discord.Embed(
                            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description="\n" + label + message2,
                        )
                        embed_first.set_footer(
                            text=f"""Page 2/2: 26 to 50 | Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
                        )
                        await msg.edit(embed=embed_first)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page == 2:  # Go to Page 1
                        cur_page -= 1
                        embed_second = discord.Embed(
                            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description="\n"
                            + label
                            + message1
                            + (
                                "\n\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n"
                                if mode == "🏆 Trophies"
                                else ""
                            )
                            + "```",
                        )
                        embed_second.set_footer(
                            text=f"""Page 1/2:  1 to 25 | Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
                        )
                        await msg.edit(embed=embed_second)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                        await msg.edit(
                            embed=discord.Embed(
                                title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                                description=label + message1 + "```",
                            )
                        )
                        embed_second_timeout = discord.Embed(
                            description="```ansi\n" + message2
                        )
                        embed_second_timeout.set_footer(
                            text=f"""Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
                        )
                        await msg2.edit(embed=embed_second_timeout)
                        await msg.clear_reactions()
                        break

                    else:
                        await msg.remove_reaction(reaction, user)
                        # Removes reactions if invalid
                except asyncio.TimeoutError:
                    await msg.edit(
                        embed=discord.Embed(
                            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description=label + message1 + "```",
                        )
                    )
                    embed_second_timeout = discord.Embed(
                        description="```ansi\n" + message2
                    )
                    embed_second_timeout.set_footer(
                        text=f"""Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
                    )
                    await msg2.edit(embed=embed_second_timeout)
                    await msg.clear_reactions()
                    break
                    # Ending the loop if user doesn't react after 15 seconds
        elif cannot_split == True:  # Send in 1 message if there are too little records
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                    description=label + message + "```",
                )
            )

        # Update to repl.it's database for old keys
        if (
            f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"
            in db.keys()
        ) and (new_key_flag == False):
            value = dict()
            for record in records:
                value[record["owner_id"]] = {
                    "rank": record["rank"],
                    "score": record["score"],
                }
            value[
                "last_update_time"
            ] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record["leaderboard_id"]] = value

    elif changes == "Hidden":
        if mode == "🏆 Trophies":  # By Tropihes

            def trophies_hidden(last=True, fifty=False):
                split = []
                tier = []
                for i in range(12):
                    split.append(
                        server_config["trophy_tiers"][i]["maximum_rank"])
                    tier.append(
                        server_config["trophy_tiers"][i]["name"].upper())
                tier_color_code = [
                    "35",
                    "36",
                    "33",
                    "34",
                    "31",
                    "32",
                    "35",
                    "31",
                    "33",
                    "30",
                    "37",
                    "37",
                ]

                # Using f-string spacing to pretty print the leaderboard labels (bold)
                message = f"{season_info_2}\n📊 ***Leaderboard***:```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {'Trophies:':<9} {'Games:':<6} {'T/G:'}\u001b[0m\n{'─' * 49}\n"

                # Using f-string spacing to pretty print the leaderboard
                for record in records:
                    # Determine which tier the player belongs to
                    tier_index = np.searchsorted(split, record["rank"])

                    # Rank (bold)
                    message += f"\u001b[1;{tier_color_code[tier_index]}m{'#' + str(record['rank']):<5}\u001b[0m "

                    # Name and color for players with season pass
                    try:  # For seasons without 'has season pass' key
                        message += (
                            (
                                "\u001b[1;33m"
                                if record["metadata"]["has_season_pass"]
                                else ""
                            )
                            + f"{record['username']:<20}"
                            + (
                                "\u001b[0m "
                                if record["metadata"]["has_season_pass"]
                                else " "
                            )
                        )
                    except:
                        message += f"{record['username']:<20} "  # Name only

                    # Trophies
                    message += f"{emojis[mode.lower()[2:]] + '{:,}'.format(record['score']):<10}"

                    # Games Played
                    message += f"{record['num_score']:<6}"

                    # Trophies / Games Played
                    message += f"{record['score']/record['num_score']:.2f}\n"

                    # Tier separators (bold)
                    if (
                        (record["rank"] in split and record["rank"] % 25 != 0)
                        or (last == True and record["rank"] % 25 == 0)
                        or (len(records) != 25 and record["rank"] % 25 == len(records))
                    ):
                        tier_name_with_space = " " + tier[tier_index] + " "
                        message += f"\u001b[1;{tier_color_code[tier_index]}m{tier_name_with_space.center(49, '─')}\u001b[0m\n"

                if fifty == True:
                    message += "\u001b[1;31m────────────────────── RUBY ─────────────────────\u001b[0m\n"
                message += "```"
                return message

        else:  # By Points/Wins/Player Kills/Bot Kills

            def non_trophies_hidden():
                # Using f-string spacing to pretty print the leaderboard labels (bold)
                if mode == "🎉 Wins":  # By Wins
                    message = (
                        (
                            f"{season_info_2}\n📊 ***Leaderboard***:"
                            if season != 0
                            else ""
                        )
                        + f"```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {mode[2:]+':'}\u001b[0m\n{'─' * 35}\n"
                    )
                else:  # By Points/Player Kills/Bot Kills
                    message = (
                        (
                            f"{season_info_2}\n📊 ***Leaderboard***:"
                            if season != 0
                            else ""
                        )
                        + f"```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {mode[2:]+':':<11} {'Games:':<7} {'P/G:' if mode == '🧊 Points' else 'K/G:'}\u001b[0m\n{'─' * (53 if mode == '💀 Player Kills' else 52)}\n"
                    )

                # Using f-string spacing to pretty print the leaderboard
                for record in records:
                    # Rank (bold)
                    message += f"\u001b[1m{'#' + str(record['rank']):<5}\u001b[0m "

                    # Name and color for players with season pass
                    try:  # For seasons without 'has season pass' key
                        message += (
                            (
                                "\u001b[1;33m"
                                if record["metadata"]["has_season_pass"]
                                else ""
                            )
                            + f"{record['username']:<20}"
                            + (
                                "\u001b[0m "
                                if record["metadata"]["has_season_pass"]
                                else " "
                            )
                        )
                    except:
                        message += f"{record['username']:<20} "  # Name only

                    if mode == "🎉 Wins":
                        # Wins
                        message += f"{emojis[mode.lower()[2:]] + '{:,}'.format(record['score'])}\n"
                    else:
                        # Points/Player Kills/Bot Kills
                        if mode == "💀 Player Kills":
                            message += f"{emojis[mode.lower()[2:]] + '{:,}'.format(record['score']):<14}"
                        elif mode == "🤖 Bot Kills":
                            message += f"{emojis[mode.lower()[2:]] + '{:,}'.format(record['score']):<12}"
                        else:
                            message += f"{emojis[mode.lower()[2:]] + '{:,}'.format(record['score']):<11}"

                    if mode != "🎉 Wins":
                        # Games Played
                        message += f"{record['num_score']:<7}"

                        # Points/Wins/Player Kills/Bot Kills / Games Played
                        message += f"{record['score']/record['num_score']:.2f}\n"

                message += "```"
                return message

        # Send
        cur_page = 1
        embed_init = discord.Embed(
            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
            description=(
                trophies_hidden() if mode == "🏆 Trophies" else non_trophies_hidden()
            ),
        )
        embed_init.set_footer(
            text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
        msg = await interaction.followup.send(embed=embed_init)

        for reaction_emoji in ["◀️", "▶️", "⏪", "⏹️"]:
            await msg.add_reaction(reaction_emoji)

        while True:
            try:
                reaction, user = await client.wait_for(
                    "reaction_add", timeout=15, check=check
                )
                # Waiting for a reaction to be added - times out after 15 seconds

                if str(reaction.emoji) == "▶️" and next_cursor != False:  # Next page
                    cur_page += 1
                    response = await rocketbot_client.query_leaderboard(
                        season,
                        f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                        25,
                        cursor_dict[cur_page],
                    )
                    records = json.loads(response["payload"])["records"]
                    start = records[0]["rank"]
                    end = records[len(records) - 1]["rank"]
                    try:
                        cursor_dict[cur_page + 1] = json.loads(response["payload"])[
                            "next_cursor"
                        ]
                    except:
                        next_cursor = False  # Does not exist
                    embed_next = discord.Embed(
                        title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                        description=(
                            trophies_hidden()
                            if mode == "🏆 Trophies"
                            else non_trophies_hidden()
                        ),
                    )
                    embed_next.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    )
                    await msg.edit(embed=embed_next)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                    cur_page -= 1
                    response = await rocketbot_client.query_leaderboard(
                        season,
                        f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                        25,
                        cursor_dict[cur_page],
                    )
                    records = json.loads(response["payload"])["records"]
                    start = records[0]["rank"]
                    end = records[len(records) - 1]["rank"]
                    embed_prev = discord.Embed(
                        title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                        description=(
                            trophies_hidden()
                            if mode == "🏆 Trophies"
                            else non_trophies_hidden()
                        ),
                    )
                    embed_prev.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    )
                    await msg.edit(embed=embed_prev)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                    cur_page = 1
                    next_cursor = True
                    response = await rocketbot_client.query_leaderboard(
                        season,
                        f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                        25,
                        cursor_dict[cur_page],
                    )
                    records = json.loads(response["payload"])["records"]
                    start = records[0]["rank"]
                    end = records[len(records) - 1]["rank"]
                    embed_first = discord.Embed(
                        title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                        description=(
                            trophies_hidden()
                            if mode == "🏆 Trophies"
                            else non_trophies_hidden()
                        ),
                    )
                    embed_first.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    )
                    await msg.edit(embed=embed_first)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                    response = await rocketbot_client.query_leaderboard(
                        season,
                        f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                        50,
                    )
                    records = json.loads(response["payload"])["records"]
                    await msg.edit(
                        embed=discord.Embed(
                            title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description=(
                                trophies_hidden(False, True)
                                if mode == "🏆 Trophies"
                                else non_trophies_hidden()
                            ),
                        )
                    )
                    await msg.clear_reactions()
                    break

                else:
                    await msg.remove_reaction(reaction, user)
                    # Removes reactions if invalid
            except asyncio.TimeoutError:
                response = await rocketbot_client.query_leaderboard(
                    season,
                    f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                    50,
                )
                records = json.loads(response["payload"])["records"]
                await msg.edit(
                    embed=discord.Embed(
                        title=f"Rocket Bot Royale 🚀\nSeason {season} Leaderboard (by {mode[2:]}):",
                        description=(
                            trophies_hidden(False, True)
                            if mode == "🏆 Trophies"
                            else non_trophies_hidden()
                        ),
                    )
                )
                await msg.clear_reactions()
                break
                # Ending the loop if user doesn't react after 15 seconds


@tree.command()
@app_commands.describe(
    changes="Only available for Top 50 records of current season, changes since last command used",
    season="Beta Season 14 or later",
)
async def leaderboard_moonrock_miners(
    interaction: discord.Interaction,
    changes: typing.Literal["Shown", "Hidden"],
    season: int = -1,
):
    """Return the specified season leaderboard of Moonrock Miners, default current"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in [
            "◀️",
            "▶️",
            "⏪",
            "⏹️",
        ]
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
    records = json.loads(response["payload"])["records"]
    start = records[0]["rank"]
    end = records[len(records) - 1]["rank"]
    cursor_dict = dict()
    cursor_dict[1] = ""

    try:
        cursor_dict[2] = json.loads(response["payload"])["next_cursor"]
        next_cursor = True
    except:
        next_cursor = False

    if changes == "Shown":
        # Add to replit's database for new keys
        new_key_flag = False
        if f"trophies_{season}" not in db.keys():
            value = dict()
            for record in records:
                value[record["owner_id"]] = {
                    "rank": record["rank"],
                    "score": record["score"],
                }
            value[
                "last_update_time"
            ] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record["leaderboard_id"]] = value
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
                rank_diff = (
                    records[i]["rank"]
                    - db[records[i]["leaderboard_id"]
                         ][records[i]["owner_id"]]["rank"]
                )
                if rank_diff < 0:
                    rank_diff_2 = f"\u001b[2;32m▲{abs(rank_diff):<3}\u001b[0m"
                elif rank_diff > 0:
                    rank_diff_2 = f"\u001b[2;31m▼{abs(rank_diff):<3}\u001b[0m"
                else:
                    rank_diff_2 = f"{'-':^4}"
            except:
                rank_diff_2 = f"{'':<4}"  # Not found ind repl.it's database

            # Rank (bold)
            message += (
                f"{rank_diff_2}\u001b[1m{'#' + str(records[i]['rank']):<5}\u001b[0m "
            )

            # Name
            message += f"{records[i]['username']:<20} "

            # Trophies difference
            try:
                trophies_diff = (
                    records[i]["score"]
                    - db[records[i]["leaderboard_id"]
                         ][records[i]["owner_id"]]["score"]
                )
                if trophies_diff < 0:
                    trophies_diff_2 = f"\u001b[2;31m-{abs(trophies_diff):<4}\u001b[0m"
                elif trophies_diff > 0:
                    trophies_diff_2 = f"\u001b[2;32m+{abs(trophies_diff):<4}\u001b[0m"
                else:
                    trophies_diff_2 = f"{'-':^5}"
            except:
                trophies_diff_2 = f"{'':<5}"

            # Trophies
            message += (
                f"{'🏆 ' + '{:<6,.0f}'.format(records[i]['score'])} {trophies_diff_2}\n"
            )

        # Split message
        cannot_split = False  # Prevent index out of range error
        try:  # In case there are not enough records
            message1 = message[: [m.start()
                                  for m in re.finditer(r"\n", message)][24]]
            message2 = (
                message[([m.start()
                         for m in re.finditer(r"\n", message)][24]) + 1:]
                + "```"
            )
        except:
            cannot_split = True

        # Send
        if cannot_split == False:
            cur_page = 1
            embed_init = discord.Embed(
                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                description=label + message1 + "```",
            )
            embed_init.set_footer(
                text=f"Page 1/2:  1 to 25 | Changes since {db[f'trophies_{season}']['last_update_time']}"
            )
            msg = await interaction.followup.send(embed=embed_init)
            msg2 = await interaction.followup.send(
                embed=discord.Embed(description="To be edited...")
            )

            for reaction_emoji in ["◀️", "▶️", "⏹️"]:
                await msg.add_reaction(reaction_emoji)

            while True:
                try:
                    reaction, user = await client.wait_for(
                        "reaction_add", timeout=15, check=check
                    )
                    # Waiting for a reaction to be added - times out after 15 seconds

                    if str(reaction.emoji) == "▶️" and cur_page == 1:  # Go to Page 2
                        cur_page += 1
                        embed_first = discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                            description="\n" + label + message2,
                        )
                        embed_first.set_footer(
                            text=f"Page 2/2: 26 to 50 | Changes since {db[f'trophies_{season}']['last_update_time']}"
                        )
                        await msg.edit(embed=embed_first)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page == 2:  # Go to Page 1
                        cur_page -= 1
                        embed_second = discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                            description="\n" + label + message1 + "```",
                        )
                        embed_second.set_footer(
                            text=f"Page 1/2:  1 to 25 | Changes since {db[f'trophies_{season}']['last_update_time']}"
                        )
                        await msg.edit(embed=embed_second)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                        await msg.edit(
                            embed=discord.Embed(
                                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                                description=label + message1 + "```",
                            )
                        )
                        embed_second_timeout = discord.Embed(
                            description="```ansi\n" + message2
                        )
                        embed_second_timeout.set_footer(
                            text=f"Changes since {db[f'trophies_{season}']['last_update_time']}"
                        )
                        await msg2.edit(embed=embed_second_timeout)
                        await msg.clear_reactions()
                        break

                    else:
                        await msg.remove_reaction(reaction, user)
                        # Removes reactions if invalid
                except asyncio.TimeoutError:
                    await msg.edit(
                        embed=discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                            description=label + message1 + "```",
                        )
                    )
                    embed_second_timeout = discord.Embed(
                        description="```ansi\n" + message2
                    )
                    embed_second_timeout.set_footer(
                        text=f"Changes since {db[f'trophies_{season}']['last_update_time']}"
                    )
                    await msg2.edit(embed=embed_second_timeout)
                    await msg.clear_reactions()
                    break
                    # Ending the loop if user doesn't react after 15 seconds
        elif cannot_split == True:  # Send in 1 message if there are too little records
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                    description=label + message + "```",
                )
            )

        # Update to replit's database for old keys
        if (f"trophies_{season}" in db.keys()) and (new_key_flag == False):
            value = dict()
            for record in records:
                value[record["owner_id"]] = {
                    "rank": record["rank"],
                    "score": record["score"],
                }
            value[
                "last_update_time"
            ] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            db[record["leaderboard_id"]] = value

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
                message += f"{'🏆 ' + '{:,}'.format(record['score'])}\n"
            message += "```"
            return message

        # Send
        cur_page = 1
        embed_init = discord.Embed(
            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
            description=hidden(),
        )
        embed_init.set_footer(
            text=f"Page {cur_page:<2}: {start:<4} to {end:<4}")
        msg = await interaction.followup.send(embed=embed_init)

        for reaction_emoji in ["◀️", "▶️", "⏪", "⏹️"]:
            await msg.add_reaction(reaction_emoji)

        while True:
            try:
                reaction, user = await client.wait_for(
                    "reaction_add", timeout=15, check=check
                )
                # Waiting for a reaction to be added - times out after 15 seconds

                if str(reaction.emoji) == "▶️" and next_cursor != False:  # Next page
                    cur_page += 1
                    response = await moonrock_client.query_leaderboard(
                        season, "trophies", 25, cursor_dict[cur_page]
                    )
                    records = json.loads(response["payload"])["records"]
                    start = records[0]["rank"]
                    end = records[len(records) - 1]["rank"]
                    try:
                        cursor_dict[cur_page + 1] = json.loads(response["payload"])[
                            "next_cursor"
                        ]
                    except:
                        next_cursor = False  # Does not exist
                    embed_next = discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                        description=hidden(),
                    )
                    embed_next.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    )
                    await msg.edit(embed=embed_next)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                    cur_page -= 1
                    response = await moonrock_client.query_leaderboard(
                        season, "trophies", 25, cursor_dict[cur_page]
                    )
                    records = json.loads(response["payload"])["records"]
                    start = records[0]["rank"]
                    end = records[len(records) - 1]["rank"]
                    embed_prev = discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                        description=hidden(),
                    )
                    embed_prev.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    )
                    await msg.edit(embed=embed_prev)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                    cur_page = 1
                    next_cursor = True
                    response = await moonrock_client.query_leaderboard(
                        season, "trophies", 25, cursor_dict[cur_page]
                    )
                    records = json.loads(response["payload"])["records"]
                    start = records[0]["rank"]
                    end = records[len(records) - 1]["rank"]
                    embed_first = discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                        description=hidden(),
                    )
                    embed_first.set_footer(
                        text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    )
                    await msg.edit(embed=embed_first)
                    await msg.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                    response = await moonrock_client.query_leaderboard(
                        season, "trophies", 50
                    )
                    records = json.loads(response["payload"])["records"]
                    await msg.edit(
                        embed=discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                            description=hidden(),
                        )
                    )
                    await msg.clear_reactions()
                    break

                else:
                    await msg.remove_reaction(reaction, user)
                    # Removes reactions if invalid
            except asyncio.TimeoutError:
                response = await moonrock_client.query_leaderboard(
                    season, "trophies", 50
                )
                records = json.loads(response["payload"])["records"]
                await msg.edit(
                    embed=discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                        description=hidden(),
                    )
                )
                await msg.clear_reactions()
                break
                # Ending the loop if user doesn't react after 15 seconds


@tree.command()
@app_commands.describe(
    user_type="Use either User ID or Friend ID of the user",
    id="User ID or Friend ID of the user",
    section="Section(s) to be shown",
)
async def get_user(
    interaction: discord.Interaction,
    user_type: typing.Literal["User ID", "Friend ID"],
    id: str,
    section: typing.Literal[
        "🍩 Graphs only",
        "📓 General Info only",
        "with 📊 Seasons Records",
        "with 🛡️ Badges",
        "with 🗒️ Stats",
        "with 🥅 Current Goals",
        "with 📦 Items Collected",
        "with 🪖 Tanks",
        "with 🪂 Parachutes",
        "with 🌟 Trails",
        "with All Cosmetics",
        "All",
    ],
):
    """Return info about a specified user with optional section(s)"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    # If the user specified a friend code we need to query the server for their ID.
    try:
        if user_type == "Friend ID":
            id_response = await rocketbot_client.friend_code_to_id(id)
            id = json.loads(id_response["payload"])["user_id"]

        # Get user data
        response = await rocketbot_client.get_user(id)
        user_data = json.loads(response["payload"])[0]
        metadata = user_data["metadata"]
    except aiohttp.ClientResponseError:
        # The code is wrong, send an error response
        await interaction.followup.send(
            embed=discord.Embed(color=discord.Color.red(),
                                title="❌ Player not found ❌")
        )
        return

    # Get award config
    awards_config = server_config["awards"]
    default_award = {"type": "Unknown", "name": "Unknown"}

    # Get goal config
    goals_config = server_config["player_goals"]
    default_goal = {"name": "Unknown"}

    # Get general player info
    username = user_data["display_name"]
    is_online = user_data["online"]
    create_time = user_data["create_time"]
    try:
        timed_bonus_last_collect = metadata["timed_bonus_last_collect"]
    except:
        timed_bonus_last_collect = "N.A."
    current_tank = (
        metadata["skin"].replace("_", " ").split()[0].title()
        + " "
        + awards_config.get(
            awards_config.get(metadata["skin"], default_award)["skin_name"],
            default_award,
        )["name"]
    )
    current_trail = awards_config.get(metadata["trail"], default_award)["name"]
    current_parachute = awards_config.get(
        metadata["parachute"], default_award)["name"]
    current_badge = awards_config.get(metadata["badge"], default_award)["name"]
    try:
        has_season_pass = server_config["season"] in metadata["season_passes"]
    except:
        has_season_pass = False
    level = metadata["progress"]["level"]
    XP = metadata["progress"]["xp"]
    friend_code = metadata["friend_code"]
    id = user_data["user_id"]

    if section != "🍩 Graphs only":
        # Add general player info
        general_info = "```ansi\n"
        general_info += f"Username: {username}\n"
        general_info += (
            "Online: \u001b[2;" + ("32" if is_online else "31") +
            f"m{is_online}\u001b[0m\n"
        )
        dt_create_time = f"{datetime.datetime.fromtimestamp(create_time):%Y-%m-%d %H:%M:%S}"
        general_info += f"Create Time: {dt_create_time} UTC ({timeago.format(dt_create_time, datetime.datetime.now())})\n"
        dt_timed_bonus = f"{datetime.datetime.fromtimestamp(timed_bonus_last_collect):%Y-%m-%d %H:%M:%S}"
        general_info += "Last Bonus: " + (
            f"{dt_timed_bonus} UTC ({timeago.format(dt_timed_bonus, datetime.datetime.now())})\n"
            if timed_bonus_last_collect != "N.A." else "N.A.\n")
        general_info += f"Current Tank: {current_tank}\n"
        general_info += f"Current Trail: {current_trail}\n"
        general_info += f"Current Parachute: {current_parachute}\n"
        general_info += f"Current Badge: {current_badge}\n"
        general_info += (
            "Has Season Pass: \u001b[2;"
            + ("32" if has_season_pass else "31")
            + f"m{has_season_pass}\u001b[0m\n"
        )
        general_info += f"Level: {level}\n"
        max_level = len(server_config["player_progression"]["xp_levels"])
        try:
            XP_target = server_config["player_progression"]["xp_levels"][level][
                str(level + 1)
            ]["xp_target"]
            reach_max_level = False
        except IndexError:
            XP_target = server_config["player_progression"]["xp_levels"][-1][
                str(max_level)
            ]["xp_target"]
            reach_max_level = True
        general_info += (
            f"XP: {XP}/{XP_target} ("
            + ("MAX" if reach_max_level else f"{XP/XP_target*100:.0f}%")
            + ")\n"
        )
        general_info += f"Friend Code: {friend_code}\n"
        general_info += f"User ID: {id}\n"
        general_info += "```"

        # Add to embed
        message1 = ""
        message1 += f"📓 ***General Info***:\n{general_info}\n"

        # Send
        await interaction.followup.send(
            embed=discord.Embed(description=message1, color=0x00C6FE)
        )

    if section in {"with 📊 Seasons Records", "All"}:
        # Create seasons records list
        seasons_records_list = "```ansi\n"

        points_label = "\u001b[1;2mBy points (Season 1 to 10)\u001b[0m\n"
        points = f"{'Season:':<8}{'Days:':<6}{'Rank:':<10}{'Points:':<11}{'Games Played:'}\n{'─'*47}\n"
        trophies_label = (
            f"\u001b[1;2mBy trophies (Season 11 to {curr_season})\u001b[0m\n"
        )
        trophies = f"{'Season:':<8}{'Days:':<6}{'Rank:':<10}{'Trophies:':<10}{'League:':<9}{'Games Played:'}\n{'─'*56}\n"
        points_record = False
        trophies_record = False

        for season in range(1, curr_season + 1):  # From first season to current season
            response = await rocketbot_client.query_leaderboard(
                season,
                ("tankkings_points" if season <= 10 else "tankkings_trophies"),
                1,
                "",
                id,
            )
            records = json.loads(response["payload"])["owner_records"]

            for record in records:
                if record["rank"] == 1:
                    rank_emoji = "🥇"
                elif record["rank"] == 2:
                    rank_emoji = "🥈"
                elif record["rank"] == 3:
                    rank_emoji = "🥉"
                else:
                    rank_emoji = "  "
                if season <= 10:
                    points_record = True
                    points += f"{season:^8}{season_info(season)[2][:-5]:<6}{rank_emoji:<1}{record['rank']:<8,}🧊 {record['score']:<9,}{record['num_score']:,}\n"
                else:
                    trophies_record = True
                    trophies += (
                        (f"{'-'*56}\n" if season == curr_season else "")
                        + f"{season:^8}{season_info(season)[2][:-5]:<6}{rank_emoji:<1}{record['rank']:<8,}🏆 {record['score']:<9,}{league_names[np.searchsorted(league_range_orig, record['rank'])]:<9}{record['num_score']:,}\n"
                    )
        if points_record == False and trophies_record == False:
            seasons_records_list += "No records found"
        else:
            if points_record == True:
                seasons_records_list += points_label + points
            if trophies_record == True:
                seasons_records_list += (
                    ("\n" if points_record == True else "") +
                    trophies_label + trophies
                )
        seasons_records_list += "```"

        # Add to embed
        message2 = ""
        message2 += f"📊 ***Seasons Records***:\n{seasons_records_list}\n"

        # Send
        await interaction.followup.send(
            embed=discord.Embed(description=message2, color=0x00C6FE)
        )

    if section in {"with 🛡️ Badges", "All"}:
        # Create badge list
        badge_list = "```\n"

        for badge in metadata["awards"]:
            award = awards_config.get(badge, default_award)
            type = award["type"]

            if type == "badge":
                badge_list += award["name"] + "\n"
        badge_list += "```"

        # Add to embed
        message3 = ""
        message3 += f"🛡️ ***Badges***:\n{badge_list}\n"

        # Send
        await interaction.followup.send(
            embed=discord.Embed(description=message3, color=0x00C6FE)
        )

    if section in {"🍩 Graphs only", "with 🗒️ Stats", "All"}:
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
            "deathmatch_played": 0,
            "deathmatch_won": 0,
            "teams_played": 0,
            "teams_won": 0,
            "squads_played": 0,
            "squads_won": 0,
            "minemayhem_played": 0,
            "minemayhem_won": 0,
            "total_games_played": 0,
            "total_games_won": 0,
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

        # Color codes reference: https://htmlcolorcodes.com/
        YELLOW, DARK_YELLOW, LIGHT_YELLOW = '#B7950B', '#9A7D0A', '#D4AC0D'
        RED, DARK_RED, LIGHT_RED = '#B03A2E', '#943126', '#CB4335'
        BLUE, DARK_BLUE, LIGHT_BLUE = '#2874A6', '#21618C', '#2E86C1'
        GREEN, DARK_GREEN, LIGHT_GREEN = '#239B56', '#1D8348', '#28B463'
        PURPLE, DARK_PURPLE, LIGHT_PURPLE = '#76448A', '#633974', '#884EA0'
        ORANGE, DARK_ORANGE, LIGHT_ORANGE = '#B9770E', '#9C640C', '#D68910'
        DARKER_GREY, DARK_DARKER_GREY, LIGHT_DARKER_GREY = '#283747', '#212F3C', '#2E4053'
        BROWN = '#A04000'
        GREY = '#616A6B'
        TURQUOISE = '#117A65'

        labels_a_1, sizes_a_1, colors_a_1, sizes_a_2, colors_a_2, labels_b, sizes_b, colors_b, sizes_c, sizes_d = ([
        ] for i in range(10))

        total_games_played = 0
        total_games_won = 0
        kills_not_using_missiles = 0

        games_won_pct = 0
        deathmatch_won_pct = 0
        teams_won_pct = 0
        squads_won_pct = 0
        minemayhem_won_pct = 0

        kills_using_drill_pct = 0
        kills_using_flak_pct = 0
        kills_using_grenade_pct = 0
        kills_using_homing_pct = 0
        kills_using_mine_pct = 0
        kills_using_nuke_pct = 0
        kills_using_poison_pct = 0
        kills_using_shield_pct = 0
        kills_using_triple_shot_pct = 0

        for key in keys_order:
            if 'played' in key and keys_order[key] != 0:
                if key == 'games_played':
                    labels_a_1.append('Solo')
                    sizes_a_1.append(keys_order['games_played'])
                    colors_a_1.append(YELLOW)
                    sizes_a_2.append(
                        [keys_order['games_played']-keys_order['games_won'], keys_order['games_won']])
                    colors_a_2.append([DARK_YELLOW, LIGHT_YELLOW])
                    games_won_pct = keys_order["games_won"] / \
                        keys_order["games_played"]
                    sizes_c.append(float(f"{games_won_pct*100:.1f}"))
                    total_games_played += keys_order['games_played']
                    total_games_won += keys_order['games_won']
                elif key == 'deathmatch_played':
                    labels_a_1.append('Squads\nDeathmatch')
                    sizes_a_1.append(keys_order['deathmatch_played'])
                    colors_a_1.append(RED)
                    sizes_a_2.append([keys_order['deathmatch_played'] -
                                      keys_order['deathmatch_won'], keys_order['deathmatch_won']])
                    colors_a_2.append([DARK_RED, LIGHT_RED])
                    deathmatch_won_pct = keys_order["deathmatch_won"] / \
                        keys_order["deathmatch_played"]
                    sizes_c.append(float(f"{deathmatch_won_pct*100:.1f}"))
                    total_games_played += keys_order['deathmatch_played']
                    total_games_won += keys_order['deathmatch_won']
                elif key == 'teams_played':
                    labels_a_1.append('Red Vs Blue')
                    sizes_a_1.append(keys_order['teams_played'])
                    colors_a_1.append(BLUE)
                    sizes_a_2.append(
                        [keys_order['teams_played']-keys_order['teams_won'], keys_order['teams_won']])
                    colors_a_2.append([DARK_BLUE, LIGHT_BLUE])
                    teams_won_pct = keys_order["teams_won"] / \
                        keys_order["teams_played"]
                    sizes_c.append(float(f"{teams_won_pct*100:.1f}"))
                    total_games_played += keys_order['teams_played']
                    total_games_won += keys_order['teams_won']
                elif key == 'squads_played':
                    labels_a_1.append('Squads')
                    sizes_a_1.append(keys_order['squads_played'])
                    colors_a_1.append(GREEN)
                    sizes_a_2.append([keys_order['squads_played'] -
                                      keys_order['squads_won'], keys_order['squads_won']])
                    colors_a_2.append([DARK_GREEN, LIGHT_GREEN])
                    squads_won_pct = keys_order["squads_won"] / \
                        keys_order["squads_played"]
                    sizes_c.append(float(f"{squads_won_pct*100:.1f}"))
                    total_games_played += keys_order['squads_played']
                    total_games_won += keys_order['squads_won']
                elif key == 'minemayhem_played':
                    labels_a_1.append('Mine\nMayhem')
                    sizes_a_1.append(keys_order['minemayhem_played'])
                    colors_a_1.append(PURPLE)
                    sizes_a_2.append([keys_order['minemayhem_played'] -
                                      keys_order['minemayhem_won'], keys_order['minemayhem_won']])
                    colors_a_2.append([DARK_PURPLE, LIGHT_PURPLE])
                    minemayhem_won_pct = keys_order["minemayhem_won"] / \
                        keys_order["minemayhem_played"]
                    sizes_c.append(float(f"{minemayhem_won_pct*100:.1f}"))
                    total_games_played += keys_order['minemayhem_played']
                    total_games_won += keys_order['minemayhem_won']
                elif key != 'total_games_played':  # In case of new game mode added
                    labels_a_1.append(key.replace('_played', '').title())
                    sizes_a_1.append(keys_order[key])
                    colors_a_1.append(ORANGE)
                    sizes_a_2.append([keys_order[key]-keys_order[key.replace('_played',
                                                                             '_won')], keys_order[key.replace('_played', '_won')]])
                    colors_a_2.append([DARK_ORANGE, LIGHT_ORANGE])
                    sizes_c.append(
                        float(f"{keys_order[key.replace('_played', '_won')]/keys_order[key]*100:.1f}"))
                    total_games_played += keys_order[key]
                    total_games_won += keys_order[key.replace(
                        '_played', '_won')]
            elif 'kills_using' in key and key != 'kills_using_missiles' and keys_order[key] != 0:
                if key == 'kills_using_drill':
                    labels_b.append('Drill')
                    sizes_b.append(keys_order[key])
                    colors_b.append(BROWN)
                    kills_using_drill_pct = keys_order["kills_using_drill"] / \
                        keys_order["drills_used"]
                    sizes_d.append(float(f"{kills_using_drill_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_flak':
                    labels_b.append('Flak')
                    sizes_b.append(keys_order[key])
                    colors_b.append(YELLOW)
                    kills_using_flak_pct = keys_order["kills_using_flak"] / \
                        keys_order["flaks_used"]
                    sizes_d.append(float(f"{kills_using_flak_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_grenade':
                    labels_b.append('Grenade')
                    sizes_b.append(keys_order[key])
                    colors_b.append(GREY)
                    kills_using_grenade_pct = keys_order["kills_using_grenade"] / \
                        keys_order["grenades_used"]
                    sizes_d.append(float(f"{kills_using_grenade_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_homing':
                    labels_b.append('Homing')
                    sizes_b.append(keys_order[key])
                    colors_b.append(TURQUOISE)
                    kills_using_homing_pct = keys_order["kills_using_homing"] / \
                        keys_order["homings_used"]
                    sizes_d.append(float(f"{kills_using_homing_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_mine':
                    labels_b.append('Mine')
                    sizes_b.append(keys_order[key])
                    colors_b.append(RED)
                    kills_using_mine_pct = keys_order["kills_using_mine"] / \
                        keys_order["mines_used"]
                    sizes_d.append(float(f"{kills_using_mine_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_nuke':
                    labels_b.append('Nuke')
                    sizes_b.append(keys_order[key])
                    colors_b.append(BLUE)
                    kills_using_nuke_pct = keys_order["kills_using_nuke"] / \
                        keys_order["nukes_used"]
                    sizes_d.append(float(f"{kills_using_nuke_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_poison':
                    labels_b.append('Poison')
                    sizes_b.append(keys_order[key])
                    colors_b.append(GREEN)
                    kills_using_poison_pct = keys_order["kills_using_poison"] / \
                        keys_order["poisons_used"]
                    sizes_d.append(float(f"{kills_using_poison_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_shield':
                    labels_b.append('Shield')
                    sizes_b.append(keys_order[key])
                    colors_b.append(PURPLE)
                    kills_using_shield_pct = keys_order["kills_using_shield"] / \
                        keys_order["shields_used"]
                    sizes_d.append(float(f"{kills_using_shield_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                elif key == 'kills_using_triple-shot':
                    labels_b.append('Rapidfire')
                    sizes_b.append(keys_order[key])
                    colors_b.append(ORANGE)
                    kills_using_triple_shot_pct = keys_order["kills_using_triple-shot"] / \
                        keys_order["triple-shots_used"]
                    sizes_d.append(
                        float(f"{kills_using_triple_shot_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]
                else:  # In case of new weapon added
                    labels_b.append(key.replace('kills_using_', '').title())
                    sizes_b.append(keys_order[key])
                    colors_b.append(DARKER_GREY)
                    kills_using_pct = keys_order[key] / \
                        keys_order[key.replace('kills_using_', '')+'_used']
                    sizes_d.append(float(f"{kills_using_pct*100:.1f}"))
                    kills_not_using_missiles += keys_order[key]

        keys_order['total_games_played'] = total_games_played
        keys_order['total_games_won'] = total_games_won
        try:
            total_games_won_pct = keys_order["total_games_won"] / \
                keys_order['total_games_played']
        except:
            total_games_won_pct = 0

        keys_order['kills_using_missiles'] = keys_order['total_kills'] - \
            kills_not_using_missiles

        if keys_order['kills_using_missiles'] != 0:
            labels_b.append('Missiles')
            sizes_b.append(keys_order['kills_using_missiles'])
            colors_b.append(LIGHT_DARKER_GREY)
            kills_using_missiles_pct = keys_order["kills_using_missiles"] / \
                keys_order["missiles_fired"]
            sizes_d.append(float(f"{kills_using_missiles_pct*100:.1f}"))

        # Avoid divided by zero error
        try:
            kills_using_missiles_ratio = keys_order["kills_using_missiles"] / \
                keys_order["total_kills"]
        except:
            kills_using_missiles_ratio = 0
        try:
            kills_not_using_missiles_ratio = kills_not_using_missiles / \
                keys_order["total_kills"]
        except:
            kills_not_using_missiles_ratio = 0

        no_left_graphs = True if total_games_played == 0 else False
        no_right_graphs = True if kills_not_using_missiles == 0 else False

        # Graph
        if not (no_left_graphs == True and no_right_graphs == True):
            fig = plt.figure(facecolor=("#2C2F33"), figsize=(
                19.2, 10.8), edgecolor="w", linewidth=3 if section == "🍩 Graphs only" else 0)  # 1920x1080 pixels

            # Divide into subplots
            gs = GridSpec(2, 3, height_ratios=[
                          2, 1.5], width_ratios=[.45, .45, .1])
            ax0, ax1, ax2, ax3, ax4 = fig.add_subplot(gs[0]), fig.add_subplot(
                gs[1]), fig.add_subplot(gs[2]), fig.add_subplot(gs[3]), fig.add_subplot(gs[4])

            # Main title
            fig.suptitle(username, fontsize=18, color="#FFFFFF", weight='bold')

            # Threshold to hide small percentages and labels in pie charts + show them in legends
            # a_1 = left_inner; a_2 = left_outer; b = right
            threshold_a_1, threshold_a_2, threshold_b = 5, 4, 3

            # Sort and calculate
            if no_left_graphs == False:
                df_left = pd.DataFrame({
                    "labels_a_1":  labels_a_1,
                    "sizes_a_1": sizes_a_1,
                    "colors_a_1": colors_a_1,
                    "sizes_a_2": sizes_a_2,
                    "colors_a_2": colors_a_2,
                    "sizes_c": sizes_c,
                })

                df_left_sorted_a = df_left.sort_values(
                    by=['sizes_a_1']).reset_index(drop=True)

                labels_a_1_sorted = df_left_sorted_a['labels_a_1']
                sizes_a_1_sorted = df_left_sorted_a['sizes_a_1']
                colors_a_1_sorted = df_left_sorted_a['colors_a_1']
                sizes_a_1_normsizes = [
                    i/total_games_played*100 for i in sizes_a_1_sorted]
                legends_a_1_sorted = [
                    f"{8-2*i}*{labels_a_1_sorted[i]}: {sizes_a_1_sorted[i]/total_games_played*100:.1f}% ({sizes_a_1_sorted[i]})" for i in range(len(labels_a_1_sorted))]

                sizes_a_2_sorted = list(
                    itertools.chain.from_iterable(df_left_sorted_a['sizes_a_2']))
                colors_a_2_sorted = list(
                    itertools.chain.from_iterable(df_left_sorted_a['colors_a_2']))
                sizes_a_2_normsizes = [
                    i/total_games_played*100 for i in sizes_a_2_sorted]
                legends_a_2_sorted = []
                for j, i in enumerate(sizes_a_2_sorted):
                    index = j
                    pair_sum = sizes_a_2_sorted[index] + sizes_a_2_sorted[index +
                                                                          1] if index % 2 == 0 else sizes_a_2_sorted[index-1] + sizes_a_2_sorted[index]
                    percent = i/pair_sum*100
                    prefix = '- L: ' if index % 2 == 0 else '- W: '
                    legends_a_2_sorted.append(
                        f'{9-index}' + '† ' + prefix +
                        '{:.1f}% ({:.0f})'.format(percent, i)
                    )

                df_left_sorted_c = df_left.sort_values(
                    by=['sizes_c']).reset_index(drop=True)

            if no_right_graphs == False:
                df_right = pd.DataFrame({
                    "labels_b":  labels_b,
                    "sizes_b": sizes_b,
                    "colors_b": colors_b,
                    "sizes_d": sizes_d,
                })

                df_right_sorted_b = df_right.drop(df_right.tail(1).index).sort_values(
                    by=['sizes_b']).reset_index(drop=True)

                labels_b_sorted = df_right_sorted_b['labels_b']
                sizes_b_sorted = df_right_sorted_b['sizes_b']
                colors_b_sorted = df_right_sorted_b['colors_b']
                sizes_b_normsizes = [
                    i/kills_not_using_missiles*100 for i in sizes_b_sorted]
                legends_b_sorted = [
                    f"{labels_b_sorted[i]}: {sizes_b_sorted[i]/kills_not_using_missiles*100:.1f}% ({sizes_b_sorted[i]})" for i in range(len(labels_b_sorted))]

                df_right_sorted_d = df_right.sort_values(
                    by=['sizes_d']).reset_index(drop=True)

            # Custom function
            if no_left_graphs == False:
                def my_autopct_a_1(pct):
                    return '{:.1f}%\n({:.0f})'.format(pct, pct * sum(sizes_a_1) / 100) if pct > threshold_a_1 else '*'

                def my_autopct_a_2(pct):
                    index = sizes_a_2_sorted.index(
                        round(pct * sum(sizes_a_2_sorted) / 100))
                    pair_sum = sizes_a_2_sorted[index] + sizes_a_2_sorted[index +
                                                                          1] if index % 2 == 0 else sizes_a_2_sorted[index-1] + sizes_a_2_sorted[index]
                    percent = round(
                        pct * sum(sizes_a_2_sorted) / 100)/pair_sum*100
                    prefix = 'L: ' if index % 2 == 0 else 'W: '
                    return prefix + '{:.1f}%\n({:.0f})'.format(percent, pct * sum(sizes_a_2_sorted) / 100) if pct > threshold_a_2 else '*'
            if no_right_graphs == False:
                def my_autopct_b(pct):
                    return '{:.1f}%\n({:.0f})'.format(pct, pct * (sum(sizes_b) - keys_order['kills_using_missiles']) / 100) if pct > threshold_b else '*'

            def get_new_labels(sizes, labels, threshold):
                new_labels = [
                    label if size / sum(sizes) * 100 > threshold else '' for size, label in zip(sizes, labels)]
                return new_labels

            left_ax_a, right_ax_a, right_ax_b, left_ax_b, right_ax_c = ax0, ax1, ax2, ax3, ax4

            if no_left_graphs == False:
                # A: 'Games Played by Game Mode' - nested donut charts
                # Left inner
                left_ax_a.set_title(
                    "Games Played by Game Mode",
                    color="#FFFFFF",
                    fontsize=14,
                    pad=15,
                    weight='bold',
                )
                wedges_a, texts_a, autotexts_a = left_ax_a.pie(
                    sizes_a_1_sorted,
                    labels=get_new_labels(
                        sizes_a_1_sorted, labels_a_1_sorted, threshold_a_1),
                    autopct=my_autopct_a_1,
                    startangle=90,
                    textprops={
                        'color': "#FFFFFF",
                        'fontsize': 9
                    },
                    wedgeprops={
                        "edgecolor": "#FFFFFF",
                        'linewidth': 1,
                        'antialiased': True,
                        'width': .5
                    },
                    radius=1,
                    pctdistance=0.63,
                    labeldistance=1.05,
                    colors=colors_a_1_sorted,
                )

                left_ax_a.axis('equal')
                left_ax_a.text(
                    0.5,
                    0.5,
                    f'Total Games\n{total_games_played:,}\n\nTotal Wins\n{total_games_won:,}\n({total_games_won/total_games_played*100:.1f}%)',
                    transform=left_ax_a.transAxes,
                    va='center',
                    ha='center',
                    size=12,
                    color='white',
                    weight='bold',
                )

                # Left outer
                wedges_a_2, texts_a_2, autotexts_a_2 = left_ax_a.pie(
                    sizes_a_2_sorted,
                    autopct=my_autopct_a_2,
                    startangle=90,
                    textprops={
                        'color': "#FFFFFF",
                        'fontsize': 8
                    },
                    wedgeprops={
                        "edgecolor": "#FFFFFF",
                        'linewidth': 1,
                        'antialiased': True,
                        'width': .25
                    },
                    radius=1,
                    pctdistance=0.87,
                    colors=colors_a_2_sorted,
                )

                # Put small values to legends if necessary
                h_a, l_a = (), ()
                try:
                    h_a_1, l_a_1 = zip(*[(h, lab) for h, lab, i in zip(
                        wedges_a, legends_a_1_sorted, sizes_a_1_normsizes) if i < threshold_a_1][::-1])
                    h_a += h_a_1
                    l_a += l_a_1
                except:
                    pass
                try:
                    h_a_2, l_a_2 = zip(*[(h, lab) for h, lab, i in zip(wedges_a_2,
                                                                       legends_a_2_sorted, sizes_a_2_normsizes) if i < threshold_a_2][::-1])
                    h_a += h_a_2
                    l_a += l_a_2
                except:
                    pass
                try:
                    l_a_sorted, h_a_sorted = (list(t)
                                              for t in zip(*sorted(zip(l_a, h_a))))
                    l_a_sorted = [i[2:].replace('\n', ' ') for i in l_a_sorted]

                    left_ax_a.legend(
                        h_a_sorted,
                        l_a_sorted,
                        loc="upper right",
                        prop={'size': 9},
                        bbox_to_anchor=(1.15, 1),
                        ncol=1,
                    )
                except:
                    pass

                # C: 'Win Rate by Game Mode' - bar chart
                win_rates, game_modes, colors = df_left_sorted_c[
                    "sizes_c"], df_left_sorted_c["labels_a_1"], df_left_sorted_c["colors_a_1"]
                y_index = [i for i in range(len(game_modes))]

                left_ax_b.barh(game_modes, win_rates, height=.8,
                               align="center", color=colors)
                left_ax_b.set_facecolor("#222222")
                left_ax_b.set_xlabel('Win Rate (%)', size=10, color='white')
                left_ax_b.set_yticks(y_index, color='white')
                left_ax_b.set_yticklabels(game_modes, size=10, color='white')
                left_ax_b.tick_params(axis='both', colors='white')
                left_ax_b.set_axisbelow(True)
                left_ax_b.grid(axis='x', color='white', lw=1, alpha=.25)
                left_ax_b.set_title("Win Rate by Game Mode",
                                    color="#FFFFFF", fontsize=14, weight='bold')

                # Add text
                for name, count, y_pos in zip(game_modes, win_rates, y_index):
                    # Threshold to put it outside of bar
                    x_pos = float(count) + \
                        1 if float(count) < 7 else float(count)/2-2.5
                    left_ax_b.text(
                        x_pos, y_pos, f"{count}%",
                        color='white', fontsize=10, va='center',
                    )

            if no_right_graphs == False:
                # B: 'Kills by Weapon' - donut chart
                # Right
                right_ax_a.set_title(
                    "Kills by Weapon",
                    color="#FFFFFF",
                    fontsize=14,
                    pad=15,
                    weight='bold',
                    x=.75
                )
                wedges_b, texts_b, autotexts_b = right_ax_a.pie(
                    sizes_b_sorted,
                    labels=get_new_labels(
                        sizes_b_sorted, labels_b_sorted, threshold_b),
                    autopct=my_autopct_b,
                    startangle=90,
                    textprops={
                        'color': "#FFFFFF",
                        'fontsize': 10
                    },
                    wedgeprops={
                        "edgecolor": "#FFFFFF",
                        'linewidth': 1,
                        'antialiased': True,
                        'width': .5,
                    },
                    pctdistance=0.75,
                    labeldistance=1.05,
                    colors=colors_b_sorted
                )

                # Put small values to legends if necessary
                try:
                    h_b, l_b = zip(*[(h, lab) for h, lab, i in zip(wedges_b,
                                                                   legends_b_sorted, sizes_b_normsizes) if i < threshold_b])
                    right_ax_a.legend(
                        h_b,
                        l_b,
                        loc="upper right",
                        prop={'size': 10},
                        ncol=1,
                    )
                except:
                    pass
                right_ax_a.axis('equal')
                right_ax_a.text(
                    0.5,
                    0.5,
                    f"Total Kills\n{keys_order['total_kills']:,}\n\nNon-missile Kills\n{kills_not_using_missiles:,}\n({kills_not_using_missiles_ratio*100:.1f}%)",
                    transform=right_ax_a.transAxes,
                    va='center',
                    ha='center',
                    size=12,
                    color='white',
                    weight='bold',
                )

                # Missiles/Non-missiles distribution bar chart
                ratios = [kills_using_missiles_ratio,
                          kills_not_using_missiles_ratio]
                labels_inside, labels_legends = [], []
                if kills_using_missiles_ratio * 100 < 8:
                    labels_inside.append('*')
                    labels_legends.append(
                        f"{kills_using_missiles_ratio*100:.1f}%\n({keys_order['kills_using_missiles']})")
                else:
                    labels_inside.append(
                        f"{kills_using_missiles_ratio*100:.1f}%\n({keys_order['kills_using_missiles']})")

                if kills_not_using_missiles_ratio * 100 < 8:
                    labels_inside.append('*')
                    labels_legends.append(
                        f"{kills_not_using_missiles_ratio*100:.1f}%\n({kills_not_using_missiles})")
                else:
                    labels_inside.append(
                        f"{kills_not_using_missiles_ratio*100:.1f}%\n({kills_not_using_missiles})")

                colors = [LIGHT_DARKER_GREY, DARK_DARKER_GREY]
                labels_outside = ["Missiles", "Other\nWeapons"]
                bottom = 1

                for i, (ratio, label_inside, color, label_outside) in enumerate(reversed([*zip(ratios, labels_inside, colors, labels_outside)])):
                    bottom -= ratio
                    bc = right_ax_b.bar(0, ratio, .2, bottom=bottom,
                                        color=color, edgecolor='white', linewidth=1.25, label=labels_legends if label_inside == '*' else '')
                    right_ax_b.bar_label(
                        bc, labels=[f"{label_inside}"], label_type='center', color='white', size=10)
                    right_ax_b.text(-.2, bottom+ratio/2, label_outside,
                                    ha='center', va='center', size=10, color='white')
                if labels_legends != []:
                    right_ax_b.legend(
                        loc="upper center",
                        prop={'size': 9},
                        bbox_to_anchor=(.5, 1.08),
                        ncol=1,
                    )
                right_ax_b.axis('off')
                right_ax_b.set_xlim(-.2, .2)

                # D: 'Kill Rate by Weapon' - bar chart
                kill_rates, weapons, colors = df_right_sorted_d[
                    "sizes_d"], df_right_sorted_d["labels_b"], df_right_sorted_d["colors_b"]
                y_index = [i for i in range(len(weapons))]

                right_ax_c.barh(weapons, kill_rates, height=.8,
                                align="center", color=colors)
                right_ax_c.set_facecolor("#222222")
                right_ax_c.set_xlabel('Kill Rate (%)', size=10, color='white')
                right_ax_c.set_yticks(y_index, color='white')
                right_ax_c.set_yticklabels(weapons, size=10, color='white')
                right_ax_c.tick_params(axis='both', colors='white')
                right_ax_c.set_axisbelow(True)
                right_ax_c.grid(axis='x', color='white', lw=1, alpha=.25)
                right_ax_c.set_title("Kill Rate by Weapon",
                                     color="#FFFFFF", fontsize=14, weight='bold')

                # Add text
                for count, y_pos in zip(kill_rates, y_index):
                    # Threshold to put it outside of bar
                    x_pos = float(count) + \
                        .5 if float(count) < 4 else float(count)/2-1
                    right_ax_c.text(
                        x_pos, y_pos, f"{count}%",
                        color='white', fontsize=10, va='center',
                    )

            # Footer
            current_timestamp = (
                f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
            )
            plt.figtext(
                0.98,
                0.03,
                "Generated at " + current_timestamp,
                ha="right",
                color="w",
                fontsize=8,
            )
            plt.figtext(
                0.02,
                0.03,
                "Friend Code: " + friend_code,
                ha="left",
                color="w",
                fontsize=8,
            )
            plt.tight_layout()
            plt.subplots_adjust(left=None, bottom=0.1, right=None,
                                top=None, wspace=None, hspace=None)
            plt.savefig(data_stream, format='png', dpi=200)  # 3840x2160 pixels
            plt.close()

        if section != "🍩 Graphs only":
            # Avoid divided by zero error (continued)
            try:
                five_kills_pct = keys_order["5_kills"] / total_games_played
            except:
                five_kills_pct = 0
            try:
                player_kills_pct = keys_order["player_kills"] / \
                    keys_order["total_kills"]
            except:
                player_kills_pct = 0
            try:
                bot_kills_pct = keys_order["bot_kills"] / \
                    keys_order["total_kills"]
            except:
                bot_kills_pct = 0
            try:
                KDR = round(keys_order["total_kills"] /
                            keys_order["deaths"], 2)
            except:
                KDR = 0
            try:
                assists_pct = keys_order["assists"] / total_games_played
            except:
                assists_pct = 0
            try:
                dunk_tanks_pct = keys_order["dunk_tanks"] / total_games_played
            except:
                dunk_tanks_pct = 0
            try:
                first_bloods_pct = keys_order["first_bloods"] / \
                    total_games_played
            except:
                first_bloods_pct = 0
            try:
                snipers_pct = keys_order["snipers"] / total_games_played
            except:
                snipers_pct = 0
            try:
                two_birdss_pct = keys_order["two_birdss"] / total_games_played
            except:
                two_birdss_pct = 0
            try:
                yardsales_pct = keys_order["yardsales"] / total_games_played
            except:
                yardsales_pct = 0
            try:
                double_kills_pct = keys_order["double_kills"] / \
                    total_games_played
            except:
                double_kills_pct = 0
            try:
                triple_kills_pct = keys_order["triple_kills"] / \
                    total_games_played
            except:
                triple_kills_pct = 0
            try:
                quad_kills_pct = keys_order["quad_kills"] / total_games_played
            except:
                quad_kills_pct = 0
            try:
                top_5_pct = keys_order["top_5"] / keys_order["games_played"]
            except:
                top_5_pct = 0
            try:
                blocks_using_proj_pct = keys_order["blocks_using_proj"] / (
                    keys_order["blocks_using_proj"] + keys_order["blocks_using_shield"])
            except:
                blocks_using_proj_pct = 0
            try:
                blocks_using_shield_pct = keys_order["blocks_using_shield"] / (
                    keys_order["blocks_using_proj"] + keys_order["blocks_using_shield"])
            except:
                blocks_using_shield_pct = 0

            keys_order["meters_driven"] = "{:.1f}".format(
                keys_order["meters_driven"] / 1000) + " km"
            keys_order["5_kills"] = "{:<6}".format(
                keys_order["5_kills"]) + "(" + f"{five_kills_pct*100:>2.0f}" + "%) †"
            keys_order["player_kills"] = "{:<6}".format(
                keys_order["player_kills"]
            ) + "(" + f"{player_kills_pct*100:>2.0f}" + "%)"
            keys_order["bot_kills"] = "{:<6}".format(
                keys_order["bot_kills"]) + "(" + f"{bot_kills_pct*100:>2.0f}" + "%)"
            keys_order["K/D Ratio"] = KDR
            keys_order["assists"] = "{:<6}".format(
                keys_order["assists"]) + "(" + f"{assists_pct*100:>2.0f}" + "%) †"
            keys_order["dunk_tanks"] = "{:<6}".format(
                keys_order["dunk_tanks"]) + "(" + f"{dunk_tanks_pct*100:>2.0f}" + "%) †"
            keys_order["first_bloods"] = "{:<6}".format(
                keys_order["first_bloods"]
            ) + "(" + f"{first_bloods_pct*100:>2.0f}" + "%) †"
            keys_order["snipers"] = "{:<6}".format(
                keys_order["snipers"]) + "(" + f"{snipers_pct*100:>2.0f}" + "%) †"
            keys_order["two_birdss"] = "{:<6}".format(
                keys_order["two_birdss"]) + "(" + f"{two_birdss_pct*100:>2.0f}" + "%) †"
            keys_order["yardsales"] = "{:<6}".format(
                keys_order["yardsales"]) + "(" + f"{yardsales_pct*100:>2.0f}" + "%) †"
            keys_order["double_kills"] = "{:<6}".format(
                keys_order["double_kills"]
            ) + "(" + f"{double_kills_pct*100:>2.0f}" + "%) †"
            keys_order["triple_kills"] = "{:<6}".format(
                keys_order["triple_kills"]
            ) + "(" + f"{triple_kills_pct*100:>2.0f}" + "%) †"
            keys_order["quad_kills"] = "{:<6}".format(
                keys_order["quad_kills"]) + "(" + f"{quad_kills_pct*100:>2.0f}" + "%) †"
            keys_order["games_won"] = "{:<6}".format(
                keys_order["games_won"]) + "(" + f"{games_won_pct*100:>2.0f}" + "%)"
            keys_order["top_5"] = "{:<6}".format(
                keys_order["top_5"]) + "(" + f"{top_5_pct*100:>2.0f}" + "%)"
            keys_order["deathmatch_won"] = "{:<6}".format(
                keys_order["deathmatch_won"]
            ) + "(" + f"{deathmatch_won_pct*100:>2.0f}" + "%)"
            keys_order["squads_won"] = "{:<6}".format(
                keys_order["squads_won"]) + "(" + f"{squads_won_pct*100:>2.0f}" + "%)"
            keys_order["teams_won"] = "{:<6}".format(
                keys_order["teams_won"]) + "(" + f"{teams_won_pct*100:>2.0f}" + "%)"
            keys_order["minemayhem_won"] = "{:<6}".format(
                keys_order["minemayhem_won"]
            ) + "(" + f"{minemayhem_won_pct*100:>2.0f}" + "%)"
            keys_order["total_games_played"] = f"{total_games_played:<11} †"
            keys_order["total_games_won"] = "{:<6}".format(
                keys_order["total_games_won"]
            ) + "(" + f"{total_games_won_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_drill"] = "{:<6}".format(
                keys_order["kills_using_drill"]
            ) + "(" + f"{kills_using_drill_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_flak"] = "{:<6}".format(
                keys_order["kills_using_flak"]
            ) + "(" + f"{kills_using_flak_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_grenade"] = "{:<6}".format(
                keys_order["kills_using_grenade"]
            ) + "(" + f"{kills_using_grenade_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_homing"] = "{:<6}".format(
                keys_order["kills_using_homing"]
            ) + "(" + f"{kills_using_homing_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_mine"] = "{:<6}".format(
                keys_order["kills_using_mine"]
            ) + "(" + f"{kills_using_mine_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_nuke"] = "{:<6}".format(
                keys_order["kills_using_nuke"]
            ) + "(" + f"{kills_using_nuke_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_poison"] = "{:<6}".format(
                keys_order["kills_using_poison"]
            ) + "(" + f"{kills_using_poison_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_shield"] = "{:<6}".format(
                keys_order["kills_using_shield"]
            ) + "(" + f"{kills_using_shield_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_triple-shot"] = "{:<6}".format(
                keys_order["kills_using_triple-shot"]
            ) + "(" + f"{kills_using_triple_shot_pct*100:>2.0f}" + "%)"
            keys_order["kills_using_missiles"] = "{:<6}".format(
                keys_order['kills_using_missiles']
            ) + "(" + f"{kills_using_missiles_pct*100:>2.0f}" + "%)"
            keys_order["blocks_using_proj"] = "{:<6}".format(
                keys_order["blocks_using_proj"]
            ) + "(" + f"{blocks_using_proj_pct*100:>2.0f}" + "%)"
            keys_order["blocks_using_shield"] = "{:<6}".format(
                keys_order["blocks_using_shield"]
            ) + "(" + f"{blocks_using_shield_pct*100:>2.0f}" + "%)"

            first_title = " General "
            stat_list += f"\u001b[1;2m{first_title.center(45, '—')}\u001b[0m\n"
            keys = [
                "deaths", "snipers", "two_birdss", "games_played", "games_won", "top_5",
                "deathmatch_played", "deathmatch_won", "teams_played", "teams_won",
                "triple-shots_used", "kills_using_triple-shot", "blocks_using_proj"
            ]
            rennamed_keys = [
                "total_deaths", "long_shot", "two_birdses", "solo_played", "solo_won",
                "solo_top_5", "squads_deathmatch_played", "squads_deathmatch_won",
                "Red_VS_Blue_played", "Red_VS_Blue_won", "rapidfire_used",
                "kills_using_rapidfire", "blocks_using_missile"
            ]
            for key in keys_order:
                if key in keys:
                    renamed_key = rennamed_keys[keys.index(key)]
                else:
                    renamed_key = key
                stat_list += f"{renamed_key.replace('_', ' ').title():>24}: {keys_order[key]}\n"
                remaining_titles = [" Medals ", " Games Played ", " Weapons "]
                key_cutoff = ["K/D Ratio", "quad_kills", "total_games_won"]
                if key in key_cutoff:
                    stat_list += f"\n\u001b[1;2m{remaining_titles[key_cutoff.index(key)].center(44, '—')}\u001b[0m\n"

            stat_list += "```"

            # Add to embed
            message4 = ""
            message4 += f"🗒️ ***Stats***:\n{stat_list}\n"

        # Send
        data_stream.seek(0)
        chart = discord.File(
            data_stream, filename=f"{friend_code}_info_charts.png")
        if section != "🍩 Graphs only":
            embed1 = discord.Embed(description=message4, color=0x00C6FE)
            embed1.set_image(url=f"attachment://{friend_code}_info_charts.png")

        if section == "🍩 Graphs only":
            await interaction.followup.send(file=chart)
        else:
            await interaction.followup.send(embed=embed1, file=chart)

    if section in {"with 🥅 Current Goals", "All"}:
        # Create goal list
        goal_list = "```\n"

        for goal in metadata["goals"]:
            selected_goal = goals_config.get(goal["goal_id"], default_goal)
            goal_name = selected_goal["name"]
            goal_progress = f"{goal['count']:>4.0f}/{selected_goal['count']:<4}"
            goal_xp = f"{selected_goal['xp']}XP"

            if len(goal_name) > 34:
                lines = textwrap.wrap(goal_name, 34, break_long_words=False)
                goal_list += (
                    f"- {lines[0]:<34} {goal_progress:<9}{goal_xp:>6}\n  {lines[1]}\n"
                )
            else:
                goal_list += f"- {goal_name:<34} {goal_progress:<9}{goal_xp:>6}\n"
        goal_list += "```"

        # Add to embed
        message5 = ""
        message5 += f"🥅 ***Current Goals***:\n{goal_list}\n"

        # Send
        await interaction.followup.send(
            embed=discord.Embed(description=message5, color=0x00C6FE)
        )

    if section in {
        "with 📦 Items Collected",
        "with 🪖 Tanks",
        "with 🪂 Parachutes",
        "with 🌟 Trails",
        "with All Cosmetics",
        "All",
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
                    if value["hidden"] != True:
                        pass
                    else:
                        if value["name"] == "Moai":
                            tank_legendary_total += 1

                except:
                    if value["type"] == "skin_set":
                        if value["rarity"] == "common":
                            tank_common_total += 1
                        elif value["rarity"] == "rare":
                            tank_rare_total += 1
                        elif value["rarity"] == "legendary":
                            tank_legendary_total += 1
                        elif value["rarity"] == "purchased":
                            tank_purchased_total += 1
                        elif value["rarity"] == "earned":
                            tank_earned_total += 1
                    elif value["type"] == "parachute":
                        if value["rarity"] == "common":
                            parachute_common_total += 1
                        elif value["rarity"] == "rare":
                            parachute_rare_total += 1
                        elif value["rarity"] == "legendary":
                            parachute_legendary_total += 1
                        elif value["rarity"] == "purchased":
                            parachute_purchased_total += 1
                        elif value["rarity"] == "earned":
                            parachute_earned_total += 1
                    elif value["type"] == "trail":
                        if value["rarity"] == "common":
                            trail_common_total += 1
                        elif value["rarity"] == "rare":
                            trail_rare_total += 1
                        elif value["rarity"] == "legendary":
                            trail_legendary_total += 1
                        elif value["rarity"] == "purchased":
                            trail_purchased_total += 1
                        elif value["rarity"] == "earned":
                            trail_earned_total += 1
            except:
                pass

        tank_list_duplicated = []
        for tank in metadata["awards"]:
            award = awards_config.get(tank, default_award)
            type = award["type"]

            if type == "skin":
                tank_list_duplicated.append(award["skin_name"])

        tank_list_counter = Counter(tank_list_duplicated)
        for unique_tank in tank_list_counter:
            try:
                if awards_config.get(unique_tank)["rarity"] == "common":
                    tank_common_owned += 1
                elif awards_config.get(unique_tank)["rarity"] == "rare":
                    tank_rare_owned += 1
                elif awards_config.get(unique_tank)["rarity"] == "legendary":
                    tank_legendary_owned += 1
                elif awards_config.get(unique_tank)["rarity"] == "purchased":
                    tank_purchased_owned += 1
                elif awards_config.get(unique_tank)["rarity"] == "earned":
                    tank_earned_owned += 1
            except:
                pass

        # Create parachute list
        parachute_list = f"```\n{'Rarity:':<7} {'Name:':<17}\n{'—'*25}\n"

        # Create trail list
        trail_list = f"```\n{'Rarity:':<7} {'Name:':<17}\n{'—'*25}\n"

        for award in metadata["awards"]:
            skin = awards_config.get(award, default_award)

            try:
                if skin["name"] == "No trail":
                    trail_list += "        " + skin["name"] + "\n"
                else:
                    type = skin["type"]
                    rarity = skin["rarity"]
                    if type == "parachute":
                        if rarity == "common":
                            parachute_common_owned += 1
                            parachute_list += "     ⭐ " + skin["name"] + "\n"
                        elif rarity == "rare":
                            parachute_rare_owned += 1
                            parachute_list += "   ⭐⭐ " + skin["name"] + "\n"
                        elif rarity == "legendary":
                            parachute_legendary_owned += 1
                            parachute_list += " ⭐⭐⭐ " + skin["name"] + "\n"
                        elif rarity == "purchased":
                            parachute_purchased_owned += 1
                            parachute_list += "     💰 " + skin["name"] + "\n"
                        elif rarity == "earned":
                            parachute_earned_owned += 1
                            parachute_list += "     🏅 " + skin["name"] + "\n"
                    if type == "trail":
                        if rarity == "common":
                            trail_common_owned += 1
                            trail_list += "     ⭐ " + skin["name"] + "\n"
                        elif rarity == "rare":
                            trail_rare_owned += 1
                            trail_list += "   ⭐⭐ " + skin["name"] + "\n"
                        elif rarity == "legendary":
                            trail_legendary_owned += 1
                            trail_list += " ⭐⭐⭐ " + skin["name"] + "\n"
                        elif rarity == "purchased":
                            trail_purchased_owned += 1
                            trail_list += "     💰 " + skin["name"] + "\n"
                        elif rarity == "earned":
                            trail_earned_owned += 1
                            trail_list += "     🏅 " + skin["name"] + "\n"
            except:
                pass

        parachute_list += "```"
        trail_list += "```"

        common_owned = tank_common_owned + parachute_common_owned + trail_common_owned
        common_total = tank_common_total + parachute_common_total + trail_common_total
        rare_owned = tank_rare_owned + parachute_rare_owned + trail_rare_owned
        rare_total = tank_rare_total + parachute_rare_total + trail_rare_total
        legendary_owned = (
            tank_legendary_owned + parachute_legendary_owned + trail_legendary_owned
        )
        legendary_total = (
            tank_legendary_total + parachute_legendary_total + trail_legendary_total
        )
        purchased_owned = (
            tank_purchased_owned + parachute_purchased_owned + trail_purchased_owned
        )
        purchased_total = (
            tank_purchased_total + parachute_purchased_total + trail_purchased_total
        )
        earned_owned = tank_earned_owned + parachute_earned_owned + trail_earned_owned
        earned_total = tank_earned_total + parachute_earned_total + trail_earned_total

        tank_owned = (
            tank_common_owned
            + tank_rare_owned
            + tank_legendary_owned
            + tank_purchased_owned
            + tank_earned_owned
        )
        tank_total = (
            tank_common_total
            + tank_rare_total
            + tank_legendary_total
            + tank_purchased_total
            + tank_earned_total
        )
        parachute_owned = (
            parachute_common_owned
            + parachute_rare_owned
            + parachute_legendary_owned
            + parachute_purchased_owned
            + parachute_earned_owned
        )
        parachute_total = (
            parachute_common_total
            + parachute_rare_total
            + parachute_legendary_total
            + parachute_purchased_total
            + parachute_earned_total
        )
        trail_owned = (
            trail_common_owned
            + trail_rare_owned
            + trail_legendary_owned
            + trail_purchased_owned
            + trail_earned_owned
        )
        trail_total = (
            trail_common_total
            + trail_rare_total
            + trail_legendary_total
            + trail_purchased_total
            + trail_earned_total
        )

        owned = tank_owned + parachute_owned + trail_owned
        total = tank_total + parachute_total + trail_total

        # Items Collected table
        s = f"```\n┌{'─'*17}┬{'─'*7}┬{'─'*10}┬{'─'*6}┬{'─'*9}┐\n│{'Rarity':^17}│{'Tanks':^7}│{'Parachutes':^10}│{'Trails':^6}│{'Sub-total':^9}│\n├{'─'*17}┼{'─'*7}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│     * {'Common':<10}│{str(tank_common_owned):>3}/{str(tank_common_total):<3}│{str(parachute_common_owned):>4}/{str(parachute_common_total):<5}│{str(trail_common_owned):>2}/{str(trail_common_total):<3}│{str(common_owned):>4}/{str(common_total):<4}│\n├{'─'*17}┼{'─'*7}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│    ** {'Rare':<10}│{str(tank_rare_owned):>3}/{str(tank_rare_total):<3}│{str(parachute_rare_owned):>4}/{str(parachute_rare_total):<5}│{str(trail_rare_owned):>2}/{str(trail_rare_total):<3}│{str(rare_owned):>4}/{str(rare_total):<4}│\n├{'─'*17}┼{'─'*7}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│   *** {'Legendary':<10}│{str(tank_legendary_owned):>3}/{str(tank_legendary_total):<3}│{str(parachute_legendary_owned):>4}/{str(parachute_legendary_total):<5}│{str(trail_legendary_owned):>2}/{str(trail_legendary_total):<3}│{str(legendary_owned):>4}/{str(legendary_total):<4}│\n├{'─'*17}┼{'─'*7}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│     $ {'Purchased':<10}│{str(tank_purchased_owned):>3}/{str(tank_purchased_total):<3}│{str(parachute_purchased_owned):>4}/{str(parachute_purchased_total):<5}│{str(trail_purchased_owned):>2}/{str(trail_purchased_total):<3}│{str(purchased_owned):>4}/{str(purchased_total):<4}│\n├{'─'*17}┼{'─'*7}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│     Ꙋ {'Earned':<10}│{str(tank_earned_owned):>3}/{str(tank_earned_total):<3}│{str(parachute_earned_owned):>4}/{str(parachute_earned_total):<5}│{str(trail_earned_owned):>2}/{str(trail_earned_total):<3}│{str(earned_owned):>4}/{str(earned_total):<4}│\n├{'─'*17}┼{'─'*7}┼{'─'*10}┼{'─'*6}┼{'─'*9}┤\n"
        s += f"│ {'Sub-total':^16}│{str(tank_owned):>3}/{str(tank_total):<3}│{str(parachute_owned):>4}/{str(parachute_total):<5}│{str(trail_owned):>2}/{str(trail_total):<3}│{str(owned):>4}/{str(total):<4}│\n└{'─'*17}┴{'─'*7}┴{'─'*10}┴{'─'*6}┴{'─'*9}┘```"

        if section in {"with 📦 Items Collected", "with All Cosmetics", "All"}:
            # Add to embed
            message6 = ""
            message6 += f"📦 ***Items Collected***:\n{s}\n"

            # Send
            await interaction.followup.send(
                embed=discord.Embed(description=message6, color=0x00C6FE)
            )

        if section in {"with 🪖 Tanks", "with All Cosmetics", "All"}:
            # Create tank list
            tank_list = f"```\n{'Rarity:':<7} {'Name:':<17} {'Colors:':}\n{'—'*33}\n"

            for unique_tank in tank_list_counter:
                try:
                    if (
                        awards_config.get(unique_tank, default_award)["rarity"]
                        == "common"
                    ):
                        tank_list += f"     ⭐ {awards_config.get(unique_tank, default_award)['name']:<19} {str(tank_list_counter[unique_tank])}\n"
                    elif (
                        awards_config.get(unique_tank, default_award)["rarity"]
                        == "rare"
                    ):
                        tank_list += f"   ⭐⭐ {awards_config.get(unique_tank, default_award)['name']:<19} {str(tank_list_counter[unique_tank])}\n"
                    elif (
                        awards_config.get(unique_tank, default_award)["rarity"]
                        == "legendary"
                    ):
                        tank_list += f" ⭐⭐⭐ {awards_config.get(unique_tank, default_award)['name']:<19} {str(tank_list_counter[unique_tank])}\n"
                    elif (
                        awards_config.get(unique_tank, default_award)["rarity"]
                        == "purchased"
                    ):
                        tank_list += f"     💰 {awards_config.get(unique_tank, default_award)['name']:<19} {str(tank_list_counter[unique_tank])}\n"
                    elif (
                        awards_config.get(unique_tank, default_award)["rarity"]
                        == "earned"
                    ):
                        tank_list += f"     🏅 {awards_config.get(unique_tank, default_award)['name']:<19} {str(tank_list_counter[unique_tank])}\n"
                except:
                    pass

            tank_list += "```"

        if section in {"with 🪖 Tanks", "with All Cosmetics", "All"}:
            # Add to embed
            message7 = ""
            message7 += f"🪖 ***Tanks***:\n{tank_list}\n"

            # Send
            await interaction.followup.send(
                embed=discord.Embed(description=message7, color=0x00C6FE)
            )

        if section in {"with 🪂 Parachutes", "with All Cosmetics", "All"}:
            # Add to embed
            message8 = ""
            message8 += f"🪂 ***Parachutes***:\n{parachute_list}\n"

            # Send
            await interaction.followup.send(
                embed=discord.Embed(description=message8, color=0x00C6FE)
            )

        if section in {"with 🌟 Trails", "with All Cosmetics", "All"}:
            # Add to embed
            message9 = ""
            message9 += f"🌟 ***Trails***:\n{trail_list}\n"

            # Send
            await interaction.followup.send(
                embed=discord.Embed(description=message9, color=0x00C6FE)
            )


@tree.command()
async def bot_info(interaction: discord.Interaction):
    """Get info about this bot."""

    await interaction.response.defer(ephemeral=False, thinking=True)

    embed = discord.Embed()
    embed.title = "Bot info:"
    embed.description = "Community discord bot, being hosted on repl.it\n\nFor more info visit https://github.com/Blakiemon/Winterpixel-Community-Bot.\n\n All pull requests will be reviewed, and appreciated."
    await interaction.followup.send(embed=embed)


@tree.command()
async def battle(interaction: discord.Interaction):
    """Have a battle with a random bot!"""

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
        'The missile vanishes off the screen, seemingly lost to the water.\nSuddenly, you hear a flurry of *ping*s! The words "Long Shot!" splash across your monitor, followed by "Two Birds", "Double Kill", "Triple Kill", and finally "Quad Kill". This is it. This is the moment you thought would never happen. The "Get a quad kill" and "Destroy two tanks with one explosion" goals you\'ve had for two months are finally complete. As the flood of joy and relief washes over you, so does the rising water over your tank. You\'ve lost the match, but you don\'t care. The war is already won. In a hurry you leave the match and click to the Goals tab, overcome with anticipation to see those beautiful green *Collect!* buttons. You slide your cursor over.\nBAM! The moment before you click, the screen goes black. All you can see is "Connecting...". The loading indicator never goes away.': 0.1,
        "You get a quad kill, four birds one stone! It was four bots doing the same exact movement. They drop 4 coins. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264>": 0.1,
        "🗿 Moyai God comes down from the heavens and blocks your missile. You bow down (as a tank) and repent for your sins.": 0.1,
        "Before your bullet hits the bot you were aiming at, a shiny green bot jumps up and takes the hit. Suddenly a green gem appears where it died, floating in midair. JACKPOT<:gem:910247413695016970>": 0.1,
    }
    event = (
        "You fire a missile at a bot. <:rocketmint:910253491019202661>\n"
        + random.choices(population=list(events.keys()), weights=events.values(), k=1)[
            0
        ]
    )

    if "<R>" in event:
        # Get random name from leaderboard
        response = await rocketbot_client.query_leaderboard(
            curr_season, "tankkings_trophies", 50
        )
        records = json.loads(response["payload"])["records"]
        rand_player = random.choice(records)["username"]

        # Formulate response with random name
        event = event.replace("<R>", rand_player)
    else:
        # Otherwise wait half a second
        await asyncio.sleep(0.5)

    await interaction.followup.send(event)


@tree.command()
async def build_a_bot(interaction: discord.Interaction):
    """Bear the responsibility of creating new life... I mean bot"""
    bot_name = generate_random_name()
    response = f"***Meet your lovely new bot!***\n\n`{bot_name}`"
    if len(bots) >= 5:
        response += f"\n\n`{bot_name}` can't join because 5 bots have already joined"
    else:
        response += f"\n\n`{bot_name}` is joining the next game"
        players.append(bot_name)
        bots.append(bot_name)
    await interaction.response.send_message(response)


@tree.command()
async def join_game(interaction: discord.Interaction):
    """Join the current game"""
    if playing:
        await interaction.response.send_message(
            "Can't join because a game is already in progress"
        )
        return
    response = ""
    if interaction.user.mention not in players:
        players.append(interaction.user.mention)
        response += "{} joined".format(interaction.user.mention)
    else:
        response += "{} you cant join twice".format(interaction.user.mention)

    await interaction.response.send_message(response)


@tree.command(guild=discord.Object(id=989993645006536704))
async def get_config(interaction: discord.Interaction):
    file = io.StringIO(json.dumps(server_config))
    await interaction.response.send_message(
        file=discord.File(fp=file, filename="server_config.json")
    )


@tree.command()
async def start_game(interaction: discord.Interaction):
    """Start a game with the people joined"""
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
    embed1 = discord.Embed(color=0xA80022)
    embed1.add_field(name="Players: ", value=response, inline=False)
    await interaction.response.send_message(response)
    msg = await interaction.channel.send("Starting game")
    #     await asyncio.sleep(0)
    moneys = OrderedDict()
    while len(players) >= 1:
        embed = discord.Embed(color=0xA80022)
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

        action_choice = random.choices(
            population=list(action_types.keys()), weights=action_types.values(), k=1
        )[0]

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
                "THE POWER OF MOYAI 🗿": 0.1,
            }
            event = random.choices(
                population=list(kill_messages.keys()),
                weights=kill_messages.values(),
                k=1,
            )[0]
            event = event.replace("<A>", player_a)
            event = event.replace("<B>", player_b)
            if "<U>" in event:
                event = event.replace(
                    "<U>",
                    random.choices(
                        population=list(weapons.keys()), weights=weapons.values(), k=1
                    )[0],
                )
            # B-E die for kills, if we need a non dying player use F
            event += (
                "\n\n"
                + player_a
                + " got "
                + str(coin_num)
                + " <:coin:910247623787700264>"
            )
            event += (
                " and "
                + player_b
                + " lost "
                + str(coin_num)
                + " <:coin:910247623787700264>"
            )
            if "@" in player_a:  # Not a bot
                player_a_id = convert_mention_to_id(player_a)
                player_a_object = await interaction.guild.query_members(
                    user_ids=[player_a_id]
                )
                if player_a_object[0].nick == None:  # No nickname is found
                    player_a_name = str(player_a_object[0])[
                        :-5]  # Use username
                else:
                    player_a_name = player_a_object[0].nick  # Use nickname
                change_player_coin(player_a_id, player_a_name, coin_num)
            if "@" in player_b:  # Not a bot
                player_b_id = convert_mention_to_id(player_b)
                player_b_object = await interaction.guild.query_members(
                    user_ids=[player_b_id]
                )
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
                "On <A>'s screen an error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>": 1,
            }
            event = random.choices(
                population=list(kill_messages.keys()),
                weights=kill_messages.values(),
                k=1,
            )[0]
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


@tree.command()
async def my_balance(interaction: discord.Interaction):
    """Find out how much coins you have in discord"""
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
@app_commands.describe(
    amount="Amount of coins to be transfered", recipient="User who receive the coins"
)
async def transfer_coins(interaction: discord.Interaction, amount: int, recipient: str):
    """Transfer some coins to another user"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    # Check how many coins the sender has
    id_sender = convert_mention_to_id(interaction.user.mention)
    user_object = await interaction.guild.query_members(user_ids=[id_sender])
    if user_object[0].nick == None:  # No nickname is found
        name = str(user_object[0])[:-5]  # Use username
    else:
        name = user_object[0].nick  # Use nickname
    sender_coin_before = change_player_coin(id_sender, name, 0, True)

    id_recipient = convert_mention_to_id(recipient)

    if id_sender == id_recipient:
        await interaction.followup.send(
            "You can't transfer <:coin1:910247623787700264> to yourself"
        )

    elif amount > sender_coin_before:
        await interaction.followup.send(
            "You don't have enough <:coin1:910247623787700264>"
        )

    else:
        change_player_coin(id_sender, name, -amount, request=False)
        try:
            user_object = await interaction.guild.query_members(user_ids=[id_recipient])
            if user_object[0].nick == None:  # No nickname is found
                name = str(user_object[0])[:-5]  # Use username
            else:
                name = user_object[0].nick  # Use nickname
            change_player_coin(id_recipient, name, amount, request=False)
            await interaction.followup.send(
                f"You've transfered {amount} <:coin1:910247623787700264> to {recipient}"
            )
        except:
            change_player_coin(id_sender, name, amount, request=False)
            await interaction.followup.send("Recipient not found")


@tree.command()
@app_commands.describe(
    changes="Changes since last command used, takes longer to compute"
)
async def discord_coins_leaderboard(
    interaction: discord.Interaction, changes: typing.Literal["Shown", "Hidden"]
):
    """Return the discord coins leaderboard"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in [
            "◀️",
            "▶️",
            "⏪",
            "⏹️",
        ]

    # This makes sure nobody except the command sender can interact with the "menu"

    # Create a new dictionary
    rank_dict = dict()
    for id in db["discord_coins"]:
        if id != "last_update_time":
            rank_dict[id] = db["discord_coins"][id]["coins"]

    # Sort the new dictionary
    sorted_rank_dict = sorted(
        rank_dict.items(), key=itemgetter(1), reverse=True)

    if changes == "Shown":
        # Using f-string spacing to pretty print the leaderboard labels (bold)
        label = f"```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<28} {'Coins:'}\n\u001b[0m{'─' * 52}\n"

        # Using f-string spacing to pretty print the leaderboard
        leaderboard = ""
        for i in sorted_rank_dict:
            # Rank difference
            try:
                rank_diff = (sorted_rank_dict.index(i) + 1) - db["discord_coins"][i[0]][
                    "rank"
                ]  # New rank - old rank
                if rank_diff > 0:
                    rank_diff_2 = f"\u001b[2;31m▼{abs(rank_diff):<3}\u001b[0m"
                elif rank_diff < 0:
                    rank_diff_2 = f"\u001b[2;32m▲{abs(rank_diff):<3}\u001b[0m"
                else:
                    rank_diff_2 = f"{'-':^4}"
            except:
                rank_diff_2 = f"{'':4}"  # Not found in repl.it's database

            # Coins difference
            coins_diff = db["discord_coins"][i[0]]["coins_change"]
            if coins_diff < 0:
                coins_diff_2 = f"\u001b[2;31m-{abs(coins_diff):<4}\u001b[0m"
            elif coins_diff > 0:
                coins_diff_2 = f"\u001b[2;32m+{abs(coins_diff):<4}\u001b[0m"
            else:
                coins_diff_2 = f"{'-':^5}"

            # A single all-in-one record
            leaderboard += f"{rank_diff_2}\u001b[1m{'#' + str(sorted_rank_dict.index(i) + 1):<6}\u001b[0m{db['discord_coins'][i[0]]['name']:<28}🪙 {i[1]:<6,.0f}{coins_diff_2}\n"

            # Store new 'rank'
            db["discord_coins"][i[0]]["rank"] = sorted_rank_dict.index(i) + 1

            # Reset 'coins_change'
            db["discord_coins"][i[0]]["coins_change"] = 0

            # Store 'last_update_time'
            db["discord_coins"][
                "last_update_time"
            ] = f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"

    elif changes == "Hidden":
        # Using f-string spacing to pretty print the leaderboard labels (bold)
        label = f"```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<28} {'Coins:'}\n\u001b[0m{'─' * 45}\n"

        # Using f-string spacing to pretty print the leaderboard
        leaderboard = ""
        for i in sorted_rank_dict:
            # A single all-in-one record
            leaderboard += f"\u001b[1m{'#' + str(sorted_rank_dict.index(i) + 1):<6}\u001b[0m{db['discord_coins'][i[0]]['name']:<28}🪙 {i[1]:<6,.0f}\n"

    # Split the message every 25 records
    leaderboard_split = re.compile(
        "(?:^.*$\n?){1,25}", re.M).findall(leaderboard)
    leaderboard_split_dict = dict()
    for i in leaderboard_split:
        leaderboard_split_dict[leaderboard_split.index(i) + 1] = i
    cur_page = 1
    message = label + leaderboard_split_dict[cur_page]
    message += "```"

    embed_first = discord.Embed(
        title="Discord Coins Leaderboard <:coin:910247623787700264>",
        description=message,
    )
    embed_first.set_footer(
        text=f"Page {cur_page:<2}: {'1':<4} to {'25':<4}"
        + f" | Changes since {db['discord_coins']['last_update_time']}"
        if changes == "Shown"
        else ""
    )
    msg = await interaction.followup.send(embed=embed_first)
    msg2 = await interaction.followup.send(
        embed=discord.Embed(description="To be edited...")
    )

    # Wait for reaction
    for reaction_emoji in ["◀️", "▶️", "⏪", "⏹️"]:
        await msg.add_reaction(reaction_emoji)

    while True:
        try:
            reaction, user = await client.wait_for(
                "reaction_add", timeout=15, check=check
            )
            # Waiting for a reaction to be added - times out after 15 seconds

            if (
                str(reaction.emoji) == "▶️"
                and cur_page < len(leaderboard_split_dict) - 1
            ):  # Next page
                cur_page += 1
                next_message = label + leaderboard_split_dict[cur_page] + "```"
                embed_next = discord.Embed(
                    title="Discord Coins Leaderboard <:coin:910247623787700264>",
                    description=next_message,
                )
                start = 25 * cur_page - 24
                if cur_page == len(leaderboard_split_dict) - 1:
                    end = len(sorted_rank_dict)
                else:
                    end = 25 * cur_page
                embed_next.set_footer(
                    text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    + f" | Changes since {db['discord_coins']['last_update_time']}"
                    if changes == "Shown"
                    else ""
                )
                await msg.edit(embed=embed_next)
                await msg.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                cur_page -= 1
                next_message = label + leaderboard_split_dict[cur_page] + "```"
                embed_prev = discord.Embed(
                    title="Discord Coins Leaderboard <:coin:910247623787700264>",
                    description=next_message,
                )
                start = 25 * cur_page - 24
                end = 25 * cur_page
                embed_prev.set_footer(
                    text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                    + f" | Changes since {db['discord_coins']['last_update_time']}"
                    if changes == "Shown"
                    else ""
                )
                await msg.edit(embed=embed_prev)
                await msg.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                cur_page = 1
                await msg.edit(embed=embed_first)
                await msg.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                first_message = label + leaderboard_split_dict[1] + "```"
                embed_first = discord.Embed(
                    title="Discord Coins Leaderboard <:coin:910247623787700264>",
                    description=first_message,
                )
                await msg.edit(embed=embed_first)
                second_message = "```ansi\n" + \
                    leaderboard_split_dict[2] + "```"
                embed_second = discord.Embed(description=second_message)
                embed_second.set_footer(
                    text=f"Changes since {db['discord_coins']['last_update_time']}"
                    if changes == "Shown"
                    else ""
                )
                await msg2.edit(embed=embed_second)
                await msg.clear_reactions()
                break
            else:
                await msg.remove_reaction(reaction, user)
                # Removes reactions if invalid
        except asyncio.TimeoutError:
            first_message = label + leaderboard_split_dict[1] + "```"
            embed_first = discord.Embed(
                title="Discord Coins Leaderboard <:coin:910247623787700264>",
                description=first_message,
            )
            await msg.edit(embed=embed_first)
            second_message = "```ansi\n" + leaderboard_split_dict[2] + "```"
            embed_second = discord.Embed(description=second_message)
            embed_second.set_footer(
                text=f"Changes since {db['discord_coins']['last_update_time']}"
                if changes == "Shown"
                else ""
            )
            await msg2.edit(embed=embed_second)
            await msg.clear_reactions()
            break
            # Ending the loop if user doesn't react after 15 seconds


@tree.command()
async def random_tank(interaction: discord.Interaction):
    """Get a random tank"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    chosen_tank = random.choice(tanks)

    # Get emoji's source url stored in Discord
    # Png for static emojis and Gif for animated emojis
    if "a:" in chosen_tank:
        emoji_code_split = chosen_tank[3:-1].split(":")
        img_link = "https://cdn.discordapp.com/emojis/" + \
            emoji_code_split[1] + ".gif"
        tank_name = emoji_code_split[0].replace("_", " ")[:-7].title()
    else:
        emoji_code_split = chosen_tank[2:-1].split(":")
        img_link = "https://cdn.discordapp.com/emojis/" + \
            emoji_code_split[1] + ".png"
        tank_name = emoji_code_split[0].replace("_", " ")[:-5].title()

    # Manual rename to avoid error
    if tank_name == "Default":
        tank_name = "Tank"
    elif tank_name == "Ufo Evolved":
        tank_name = "UFO Evolved"
    elif tank_name == "Ufo":
        tank_name = "UFO"
    elif tank_name == "128Bit":
        tank_name = "128bit"
    elif tank_name == "32Bit":
        tank_name = "32bit"
    elif tank_name == "16Bit":
        tank_name = "16bit"
    elif tank_name == "8Bit":
        tank_name = "8bit"
    elif tank_name == "Dualmini Ht":
        tank_name = "Dual-Mini HT"
    elif tank_name == "Dualwide Ht":
        tank_name = "Dual-Wide HT"
    elif tank_name == "Evolved Triline":
        tank_name = "Evolved Tri-Line"
    elif tank_name == "Triline Ht":
        tank_name = "Tri-Line HT"

    # Get tank info
    awards_config = server_config["awards"]
    for key, value in awards_config.items():
        try:
            if value["type"] == "skin_set":
                if value["name"] == tank_name:
                    description = value["description"]
                    if value["rarity"] == "common":
                        rarity_icon = "⭐"
                        color = 0x49C8FF
                    elif value["rarity"] == "rare":
                        rarity_icon = "⭐⭐"
                        color = 0xCB6DFF
                    elif value["rarity"] == "legendary":
                        rarity_icon = "⭐⭐⭐"
                        color = 0xFFDC5E
                    elif value["rarity"] == "purchased":
                        rarity_icon = "💰"
                        color = 0x80FF7C
                    elif value["rarity"] == "earned":
                        rarity_icon = "🏅"
                        color = 0xF1689D
            elif value["type"] == "skin":
                if value["name"] == tank_name:  # 3 bot skins
                    rarity_icon = ""
                    description = value["description"]
                    color = 0x000000
                    break
        except:
            pass

    # Send
    embed = discord.Embed(
        title=f"{rarity_icon} {tank_name}", description=description, color=color
    )
    embed.set_image(url=img_link)
    await interaction.followup.send(embed=embed)


@tree.command()
@app_commands.describe(
    length="Length of the tank", barrel="Number of barrels to be equipped"
)
async def long(interaction: discord.Interaction, length: int, barrel: int = 1):
    """Build your supercalifragilisticexpialidocious long tank equipped with as many barrels as you want!"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    long_emoji = [
        "<:longtank_part1:991838180699541504>",
        "<:longtank_part2:991838184910626916>",
        "<:longtank_part3:991838189591470130>",
        "<:longtank_part4:991838192145793125>",
    ]
    if length < 0:
        length = 0
    if barrel < 0:
        barrel = 0
    if barrel > length:
        barrel = length

    def even_space(n, k):
        a = [n // k for i in range(k)]
        for i in range(n % k):
            a[i] += 1
        b = list(OrderedDict.fromkeys(a))
        global x, y
        x, y = b[0], b[1] if len(b) > 1 else ""
        for i in range(len(a)):
            a[i] = "x" if a[i] == b[0] else "y"
        s = "".join(str(i) for i in a)
        return s

    def palindrome_check(str):
        return sum(map(lambda i: str.count(i) % 2, set(str))) <= 1

    def palindrome_rearrange(str):
        hmap = defaultdict(int)
        for i in range(len(str)):
            hmap[str[i]] += 1

        odd_count = 0

        for x in hmap:
            if hmap[x] % 2 != 0:
                odd_count += 1
                odd_char = x

        first_half = ""
        second_half = ""

        for x in sorted(hmap.keys()):
            s = (hmap[x] // 2) * x
            first_half = first_half + s
            second_half = s + second_half

        return (
            (first_half + odd_char + second_half)
            if (odd_count == 1)
            else (first_half + second_half)
        )

    even_space_encode = even_space(length - barrel, barrel + 1)
    even_space_encode_palindrome = (
        palindrome_rearrange(even_space_encode)
        if palindrome_check(even_space_encode)
        else even_space_encode
    )

    even_space_encode_palindrome_decode = [
        i for i in even_space_encode_palindrome]
    for i in range(len(even_space_encode_palindrome_decode)):
        even_space_encode_palindrome_decode[i] = (
            x if even_space_encode_palindrome_decode[i] == "x" else y
        )

    output_middle = ""
    for i in range(len(even_space_encode_palindrome_decode) - 1):
        output_middle += (
            long_emoji[1] *
            even_space_encode_palindrome_decode[i] + long_emoji[2]
        )
    output_middle += long_emoji[1] * even_space_encode_palindrome_decode[-1]
    msg = f"{long_emoji[0]}{output_middle}{long_emoji[3]}"
    quote = await interaction.followup.send(
        "```\nBuilding your tank, please wait...```"
    )
    try:
        await interaction.followup.send(msg)
        await quote.edit(
            content=f"```ansi\nThis is your \u001b[2;32ml\u001b[1;32m{'o'*length}\u001b[0m\u001b[2;32mng\u001b[0m tank!```"
        )
    except:
        await quote.edit(content="```\nThe tank is too long to build!```")


@tree.command()
@app_commands.describe(bet="The minimum bet is 1 coin")
async def slot(interaction: discord.Interaction, bet: int):
    """Play the slot machine game!"""
    await interaction.response.defer(ephemeral=False, thinking=True)
    coin = [
        "<:coin1:910247623787700264>",
        "<:coin2:991444836869754950>",
        "<:coin3:976289335844434000>",
        "<:coin4:976289358200049704>",
        "<:coin5:976288324266373130>",
    ]

    # Check how many coins the player has
    id = convert_mention_to_id(interaction.user.mention)
    user_object = await interaction.guild.query_members(user_ids=[id])
    if user_object[0].nick == None:  # No nickname is found
        name = str(user_object[0])[:-5]  # Use username
    else:
        name = user_object[0].nick  # Use nickname
    player_coin_before = change_player_coin(id, name, 0, True)

    if bet > player_coin_before:
        await interaction.followup.send(
            embed=discord.Embed(
                color=discord.Color.red(),
                title="SLOT MACHINE :slot_machine:",
                description=f"You don't have enough {coin[0]}",
            )
        )
    elif bet <= 0:
        await interaction.followup.send(
            embed=discord.Embed(
                color=discord.Color.red(),
                title="SLOT MACHINE :slot_machine:",
                description=f"The minimum bet is 1 {coin[0]}",
            )
        )

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
        if id in [
            "152080881220059136",
            "381074897083826176",
            "610369943967629340",
            "970784448633258054",
        ]:
            print(f"Unrigging slots for user: {id}")
            events = {
                coin[0]: 0.2,
                coin[1]: 0.2,
                coin[2]: 0.2,
                coin[3]: 0.2,
                coin[4]: 0.2,
            }

        slots = [
            random.choices(population=list(events.keys()),
                           weights=events.values())[0]
            for i in range(3)
        ]

        slot_embed = discord.Embed(
            color=0xFFD700,
            title="SLOT MACHINE :slot_machine:",
            description=f"**{'-' * 18}\n|{' {} |'.format(coins_loop) * 3}\n{'-' * 18}**",
        )

        sent_embed = await interaction.followup.send(embed=slot_embed)
        current_slot_pics = [coins_loop] * 3
        for i in range(len(slots)):
            await asyncio.sleep(1.5)
            current_slot_pics[i] = slots[i]
            slot_results_str = f"**{'-' * 18}\n|"
            for thisSlot in current_slot_pics:
                slot_results_str += f" {thisSlot} |"
            new_slot_embed = discord.Embed(
                color=0xFFD700,
                title="SLOT MACHINE :slot_machine:",
                description=f"{slot_results_str}\n{'-' * 18}**",
            )
            await sent_embed.edit(embed=new_slot_embed)

        if slots[0] == slots[1]:
            if slots[1] == slots[2]:
                multiplier = multiplier3[coin.index(slots[0])]
            else:
                multiplier = multiplier2[coin.index(slots[0])]
            win = True
        else:
            multiplier = 0
            win = False

        res_2 = "-- **YOU WON** --" if win == True else "-- **YOU LOST** --"
        net_change = -bet + bet * multiplier

        player_coin_after = change_player_coin(id, name, net_change, True)

        embed = discord.Embed(
            color=0xFFD700,
            title="SLOT MACHINE :slot_machine:",
            description=f"{slot_results_str}\n{'-' * 18}**\n{res_2}",
        )
        embed.add_field(name="Bet", value=f"{bet} {coin[0]}", inline=True)
        embed.add_field(
            name="Multiplier",
            value=f"{bet * multiplier} {coin[0]} ({multiplier}x)",
            inline=True,
        )
        embed.add_field(
            name="Balance", value=f"{player_coin_after} {coin[0]}", inline=True
        )
        embed.add_field(
            name="Pay Table",
            value=f"{'{}'.format(coin[4]) * 3} - 32x\n{'{}'.format(coin[3]) * 3} - 16x\n{'{}'.format(coin[2]) * 3} - 12x\n{'{}'.format(coin[1]) * 3} - 8x\n{'{}'.format(coin[4]) * 2}:grey_question: - 8x\n{'{}'.format(coin[0]) * 3} - 4x\n{'{}'.format(coin[3]) * 2}:grey_question: - 4x\n{'{}'.format(coin[2]) * 2}:grey_question: - 3x\n{'{}'.format(coin[1]) * 2}:grey_question: - 2x\n{'{}'.format(coin[0]) * 2}:grey_question: - 1x",
            inline=False,
        )
        await sent_embed.edit(embed=embed)


@tree.command()
async def memory(interaction: discord.Interaction):
    """Test your memory by matching 2 tanks!"""
    await interaction.response.defer(ephemeral=False, thinking=True)
    b = [":white_large_square:" for i in range(16)]
    c = [
        "a1",
        "b1",
        "c1",
        "d1",
        "a2",
        "b2",
        "c2",
        "d2",
        "a3",
        "b3",
        "c3",
        "d3",
        "a4",
        "b4",
        "c4",
        "d4",
    ]
    a = random.sample(tanks, 8) * 2
    random.shuffle(a)
    board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
    answer = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {a[0]} {a[1]} {a[2]} {a[3]}\n:two: {a[4]} {a[5]} {a[6]} {a[7]}\n:three: {a[8]} {a[9]} {a[10]} {a[11]}\n:four: {a[12]} {a[13]} {a[14]} {a[15]}\n"

    def check(m):
        return m.channel.id == interaction.channel.id and m.author == interaction.user

    embed = discord.Embed(
        color=0xFFD700,
        title="MEMORY GAME :brain:",
        description="Test your memory by matching 2 tanks!",
    )
    embed.add_field(name="Time", value="<80s\n<100s\n≥100s", inline=True)
    embed.add_field(
        name="Reward",
        value="20 <:coin1:910247623787700264>\n10 <:coin1:910247623787700264>\n5 <:coin1:910247623787700264>",
        inline=True,
    )
    embed.add_field(
        name="Controls",
        value="Type `s` to start the game\nType `q` to quit the game",
        inline=False,
    )
    message = await interaction.followup.send(embed=embed)

    global gamestart
    gamestart = False

    while gamestart == False:
        try:
            msg = await client.wait_for("message", check=check, timeout=15)
            if str(msg.content.lower()) == "q":
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title="MEMORY GAME :brain:",
                    description="You have quit the game",
                )
                await message.edit(embed=embed)
                break
            if (
                (str(msg.content.lower()) == "s") or (
                    str(msg.content.lower()) == "q")
            ) == False:
                warn = await interaction.followup.send(
                    ":x: Invalid input has been entered :x:"
                )
                await asyncio.sleep(2)
                await warn.delete()
            if str(msg.content.lower()) == "s":
                gamestart = True
                embed = discord.Embed(
                    color=0xFFD700, title="MEMORY GAME :brain:", description=board
                )
                embed.add_field(
                    name="Controls",
                    value="Type `a1` / `A1` to flip the card\nType `q` to quit the game",
                    inline=False,
                )
                await message.edit(embed=embed)
                start = timer()
        except asyncio.TimeoutError:
            embed = discord.Embed(
                color=discord.Color.red(),
                title="MEMORY GAME :brain:",
                description="You did not start the game",
            )
            await message.edit(embed=embed)
            break

        pair = 0
        flag = False
        while gamestart == True:
            try:
                msg = await client.wait_for("message", check=check, timeout=15)
                if str(msg.content.lower()) == "q":
                    board = answer
                    embed = discord.Embed(
                        color=discord.Color.red(),
                        title="MEMORY GAME :brain:",
                        description=f"{board}\nYou have quit the game",
                    )
                    await message.edit(embed=embed)
                    break
                if (str(msg.content.lower()) in c) == False:
                    warn2 = await interaction.followup.send(
                        ":x: Invalid coordinate has been entered :x:"
                    )
                    await asyncio.sleep(2)
                    await warn2.delete()
                elif b[c.index(str(msg.content.lower()))] == ":white_large_square:":
                    if flag == False:
                        x = c.index(str(msg.content.lower()))
                        b[x] = a[x]
                        flag = not flag
                        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                        embed = discord.Embed(
                            color=0xFFD700,
                            title="MEMORY GAME :brain:",
                            description=board,
                        )
                        embed.add_field(
                            name="Controls",
                            value="Type `a1` / `A1` to flip the card\nType `q` to quit the game",
                            inline=False,
                        )
                        await message.edit(embed=embed)
                    else:
                        y = c.index(str(msg.content.lower()))
                        b[y] = a[y]
                        flag = not flag
                        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                        embed = discord.Embed(
                            color=0xFFD700,
                            title="MEMORY GAME :brain:",
                            description=board,
                        )
                        embed.add_field(
                            name="Controls",
                            value="Type `a1` / `A1` to flip the card\nType `q` to quit the game",
                            inline=False,
                        )
                        await message.edit(embed=embed)
                        await asyncio.sleep(1)
                        if a[x] == a[y]:
                            pair += 1
                        else:
                            b[x] = ":white_large_square:"
                            b[y] = ":white_large_square:"
                            board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                            embed = discord.Embed(
                                color=0xFFD700,
                                title="MEMORY GAME :brain:",
                                description=board,
                            )
                            embed.add_field(
                                name="Controls",
                                value="Type `a1` / `A1` to flip the card\nType `q` to quit the game",
                                inline=False,
                            )
                            await message.edit(embed=embed)
                    if pair == 8:
                        end = timer()
                        time_diff = end - start
                        if time_diff < 360:
                            reward = 20
                        elif 360 <= time_diff < 720:
                            reward = 10
                        else:
                            reward = 5
                        gamestart = False

                        id = convert_mention_to_id(interaction.user.mention)
                        user_object = await interaction.guild.query_members(
                            user_ids=[id]
                        )
                        if user_object[0].nick == None:  # No nickname is found
                            name = str(user_object[0])[:-5]  # Use username
                        else:
                            name = user_object[0].nick  # Use nickname

                        player_coin_after = change_player_coin(
                            id, name, reward, True)
                        embed = discord.Embed(
                            color=0xFFD700,
                            title="MEMORY GAME :brain:",
                            description=f"{board}\n:tada: **YOU WON** :tada:",
                        )
                        embed.add_field(
                            name="Time", value=f"{time_diff:.2f}s", inline=True
                        )
                        embed.add_field(
                            name="Reward",
                            value=f"{reward} <:coin1:910247623787700264>",
                            inline=True,
                        )
                        embed.add_field(
                            name="Balance",
                            value=f"{player_coin_after} <:coin1:910247623787700264>",
                            inline=True,
                        )
                        await message.edit(embed=embed)
                        break
                    await message.edit(embed=embed)
                else:
                    warn3 = await interaction.followup.send(
                        ":x: The card has already been flipped :x:"
                    )
                    await asyncio.sleep(2)
                    await warn3.delete()
            except asyncio.TimeoutError:
                board = answer
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title="MEMORY GAME :brain:",
                    description=f"{board}\nThe game has timed out :hourglass:",
                )
                await message.edit(embed=embed)
                break
        break


@tree.command()
@app_commands.describe(
    one_star="Number of one-star skin(s) owned",
    two_star="Number of two-star skin(s) owned",
    three_star="Number of three-star skin(s) owned",
)
async def get_crate_stats(
    interaction: discord.Interaction, one_star: int, two_star: int, three_star: int
):
    """Optimize the use of in game crates and Estimate the amount of coins"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    one_star_total = 0
    two_star_total = 0
    three_star_total = 0

    for key, value in server_config["awards"].items():
        try:
            if value["rarity"] == "common":
                one_star_total += 1
            elif value["rarity"] == "rare":
                two_star_total += 1
            elif value["rarity"] == "legendary":
                three_star_total += 1
        except:
            pass

    total = one_star_total + two_star_total + three_star_total
    one_star_weight, two_star_weight, three_star_weight = (
        server_config["lootbox_rarity_odds"]["common"],
        server_config["lootbox_rarity_odds"]["rare"],
        server_config["lootbox_rarity_odds"]["legendary"],
    )
    total_weight = (
        one_star_total * one_star_weight
        + two_star_total * two_star_weight
        + three_star_total * three_star_weight
    )
    one_star_prob, two_star_prob, three_star_prob = (
        one_star_weight / total_weight,
        two_star_weight / total_weight,
        three_star_weight / total_weight,
    )

    basic_crate_price = server_config["lootbox_coin_cost"]
    elite_crate_price = server_config["unique_lootbox_coin_cost"]

    population_crate = list(range(1, total + 1))
    weights_crate = []
    for i in range(1, one_star_total + 1):
        weights_crate.append(one_star_prob)
    for j in range(1, two_star_total + 1):
        weights_crate.append(two_star_prob)
    for k in range(1, three_star_total + 1):
        weights_crate.append(three_star_prob)

    def basic_or_elite(a, b, c):
        time = 1 / (1 - one_star_prob * a -
                    two_star_prob * b - three_star_prob * c)
        expected_basic_crate_coin = basic_crate_price * time
        if expected_basic_crate_coin < elite_crate_price:
            return (
                f":one: The **OPTIMAL** way to unlock **A NEW UNIQUE SKIN** is **EXPECTED** by using **{time:.2f} BASIC CRATE"
                + ("S" if time > 1 else "")
                + f" <:crate:988520294132088892>**, which "
                + ("are" if time > 1 else "is")
                + f" worth a **TOTAL** of **{expected_basic_crate_coin:,.0f} COINS <:coin:910247623787700264>**\n"
            )
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
            for k in range(
                one_star_total + two_star_total + 1,
                one_star_total + two_star_total + 1 + c,
            ):
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
                        elif (
                            (one_star_total + 1)
                            <= int(i)
                            <= (one_star_total + two_star_total)
                        ):
                            prob -= two_star_prob
                        else:
                            prob -= three_star_prob
            elite_crates = total - len(collected)
            coins_spent = (
                basic_crates * basic_crate_price + elite_crates * elite_crate_price
            )
            expected_basic_crate.append(basic_crates)
            expected_elite_crate.append(elite_crates)
            expected_coins_spent.append(coins_spent)
            remaining = total - a - b - c
            expected_basic_crate_mean = mean(expected_basic_crate)
            expected_elite_crate_mean = mean(expected_elite_crate)
        return (
            f":two: The **OPTIMAL** way to unlock **ALL {remaining} REMAINING UNIQUE SKIN"
            + ("S" if remaining > 1 else "")
            + "** is **EXPECTED** by using "
            + (
                (
                    f"**{expected_basic_crate_mean:,.2f} BASIC CRATE"
                    + ("S" if expected_basic_crate_mean > 1 else "")
                    + " <:crate:988520294132088892>** and "
                )
                if expected_basic_crate_mean != 0
                else ""
            )
            + f"**{expected_elite_crate_mean:,.2f} ELITE CRATE"
            + ("S" if expected_elite_crate_mean > 1 else "")
            + f" <:elitecrate:989954419846184970>**, which "
            + (
                "are"
                if (expected_basic_crate_mean + expected_elite_crate_mean) > 1
                else "is"
            )
            + f" worth a **TOTAL** of **{expected_basic_crate_mean * basic_crate_price + expected_elite_crate_mean * elite_crate_price:,.0f} COINS <:coin:910247623787700264>**"
        )

    def all(a, b, c):
        total_owned = a + b + c
        if (
            (1 <= a <= one_star_total)
            and (0 <= b <= two_star_total)
            and (0 <= c <= three_star_total)
        ):
            if total_owned != total:
                return (
                    f"**1,000 SIMULATIONS** have been done based on the number of **{a} ONE-STAR :star:**, **{b} TWO-STAR :star::star:** and **{c} THREE-STAR :star::star::star: SKIN"
                    + ("S" if total_owned > 1 else "")
                    + f"** you have already owned:\n"
                    + basic_or_elite(a, b, c)
                    + basic_and_elite_simulate(a, b, c)
                )
            else:
                return f"You have already unlocked **ALL {total} UNIQUE SKINS**! :tada:"
        else:
            return ":x: **INVALID** data has been entered. Please try again. :x:"

    await interaction.followup.send(all(one_star, two_star, three_star))


@tree.command()
@app_commands.describe(season="Season 1 or later, default current")
async def season(interaction: discord.Interaction, season: int = -1):
    """Return the season info, default current"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    if season < 1 or season > curr_season:
        season = curr_season
    embed = discord.Embed()
    embed.title = "Rocket Bot Royale 🚀"
    embed.add_field(
        name="📓 ***Season Info***",
        value=f"```ansi\n{'Season: ':>10}{str(season)}\n{'Start: ':>10}{season_info(season)[0]}\n{'End: ':>10}{season_info(season)[1]}\n{'Duration: ':>10}{season_info(season)[2]}\n{'Status: ':>10}{season_info(season)[3]}\n"
        + (
            f"{'Ends in: ':>10}{season_info(season)[4]}"
            if season == curr_season
            else ""
        )
        + "```",
    )
    await interaction.followup.send(embed=embed)


@tree.command()
async def random_bot_name(interaction: discord.Interaction):
    """Generate a random bot name."""

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
        "zenith",
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
        "curtain",
    ]

    generated_random_bot_name = random.choice(noun).capitalize() + random.choice(
        adjective
    )
    await interaction.response.send_message(generated_random_bot_name)


@tree.command()
@app_commands.describe(
    article="The article you want to look up. Make sure capitalization is correct!"
)
async def fandom(interaction: discord.Interaction, article: str):
    """Fetch any articles from Rocket Bot Royale fandom wiki here!"""
    await interaction.response.defer(ephemeral=False, thinking=True)
    p = rocketbotroyale.page(article)
    try:
        page1 = page(title=article)
        sent_embed = await interaction.followup.send(
            embed=discord.Embed(description="Fetching page...")
        )
        output = discord.Embed(
            color=0xFFD700,
            title=page1.title,
            description=page1.summary,
            url=f"https://rocketbotroyale.fandom.com/wiki/{page1.title}".replace(
                " ", "_"
            ),
            timestamp=datetime.datetime.utcnow(),
        )
        list_of_images = p.images
        png_or_gif = [x for x in list_of_images if ".png" in x or ".gif" in x]
        set_image = (
            "https://static.wikia.nocookie.net/rocketbotroyale/images/c/c4/Slide1_mainpage.png/revision/latest?cb=20220712121433"
            if len(png_or_gif) == 0
            else png_or_gif[0]
        )
        output.set_image(url=set_image)
        output.set_thumbnail(
            url="https://static.wikia.nocookie.net/rocketbotroyale/images/e/e6/Site-logo.png"
        )
        output.set_footer(
            text="All information is gathered through fandom.com")
        await sent_embed.edit(embed=output)
    except:
        await interaction.followup.send(
            embed=discord.Embed(
                color=0xFF0000,
                description=f':x: "{article}" is not found. Make sure capitalization is correct!',
                timestamp=datetime.datetime.utcnow(),
            )
        )


@tree.command()
@app_commands.describe(
    graph="Box Plot: Top 100 players' records / League Trophies Range",
    mode="🏆 Trophies / 🧊 Points / 🎉 Wins / 💀 Player Kills / 🤖 Bot Kills",
    start_season="🏆 Trophies: Season 11 or later / Others: Season 1 or later, default all",
    end_season=">= start_season, default all",
)
async def plot_season(
    interaction: discord.Interaction,
    graph: typing.Literal["Box Plot", "League Trophies Range"],
    mode: typing.Literal[
        "🏆 Trophies", "🧊 Points", "🎉 Wins", "💀 Player Kills", "🤖 Bot Kills"
    ],
    start_season: int = 1,
    end_season: int = -1,
):
    """Plot statistics graph and table by various modes in season(s)"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    # For footer and filename
    current_timestamp = (
        f"{datetime.datetime.utcfromtimestamp(time.time()):%Y-%m-%d %H:%M:%S} UTC"
    )

    # Reassign parameters if unreasonable
    if graph == "League Trophies Range":
        mode = "🏆 Trophies"

    if start_season < (11 if mode == "🏆 Trophies" else 1):
        start_season = 11 if mode == "🏆 Trophies" else 1
    if start_season > curr_season:
        start_season = curr_season

    if end_season < (11 if mode == "🏆 Trophies" else 1):
        start_season = 11 if mode == "🏆 Trophies" else 1
    if end_season > curr_season or end_season == -1:
        end_season = curr_season
    if end_season < start_season:
        end_season = start_season

    # Singular or plural form for legends
    if (start_season == curr_season - 1 and end_season == curr_season) or (
        start_season == end_season and start_season != curr_season
    ):
        one_past_season = True
    else:
        one_past_season = False

    # Get leaderboard info and update replit's database if necessary
    last_update_season = 0
    for season in range(
        max(start_season, db["plot"]["last_update_season"]),
        min(end_season, curr_season) + 1,
    ):
        if season > last_update_season:
            last_update_season = season

        if str(season) not in db["plot"]:
            db["plot"][str(season)] = dict()
            db["plot"][str(season)]["days"] = season_info(season)[2][:-5]

        if (
            season < curr_season
        ):  # past seasons (store for first time / overwrite for last season)
            update_modes = ["points", "trophies", "wins", "kills", "bot_kills"]
            if season < 11:
                update_modes.remove("trophies")

            for update_mode in update_modes:
                response = await rocketbot_client.query_leaderboard(
                    season, f"tankkings_{update_mode}", 100
                )
                records = json.loads(response["payload"])["records"]

                db["plot"][str(season)][f"top_100_{update_mode}"] = [
                    record["score"] for record in records
                ]

                season_records = db["plot"][str(
                    season)][f"top_100_{update_mode}"]
                db["plot"][str(season)][f"top_100_{update_mode}_stats"] = (
                    [min(season_records)]
                    + [
                        int(round(boxplot_stats(season_records)[0][i]))
                        for i in ["q1", "med", "q3"]
                    ]
                    + [max(season_records)]
                    + [int(round(mean(season_records)))]
                )

            if season >= 11:
                response = await rocketbot_client.query_leaderboard(
                    season, "tankkings_trophies", 8002
                )
                records = json.loads(response["payload"])["records"]

                db["plot"][str(season)]["League Trophies Range"] = [
                    records[range - 1]["score"] for range in league_range
                ]

        else:  # current season
            limit = 100 if graph == "Box Plot" else 8002
            response = await rocketbot_client.query_leaderboard(
                season,
                f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                limit,
            )
            records = json.loads(response["payload"])["records"]

            global enough_records
            enough_records = len(records) >= limit

            if enough_records:
                if graph == "Box Plot":
                    db["plot"][str(season)][
                        f"top_100_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}"
                    ] = [record["score"] for record in records]

                    season_records = db["plot"][str(season)][
                        f"top_100_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}"
                    ]
                    db["plot"][str(season)][
                        f"top_100_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_stats"
                    ] = (
                        [min(season_records)]
                        + [
                            int(round(boxplot_stats(season_records)[0][i]))
                            for i in ["q1", "med", "q3"]
                        ]
                        + [max(season_records)]
                        + [int(round(mean(season_records)))]
                    )

                if graph == "League Trophies Range":
                    db["plot"][str(season)]["League Trophies Range"] = [
                        records[range - 1]["score"] for range in league_range
                    ]

    if db["plot"]["first_10_seasons_added"] == False:
        db["plot"]["first_10_seasons_added"] = True

        for season in range(1, 11):
            if str(season) not in db["plot"]:
                db["plot"]["first_10_seasons_added"] = False
                break

    if (
        db["plot"]["first_10_seasons_added"]
        and last_update_season > db["plot"]["last_update_season"]
    ):
        db["plot"]["last_update_season"] = last_update_season

    if end_season == curr_season and not (enough_records):
        end_season = curr_season - 1
        if start_season == curr_season:
            start_season = curr_season - 1

    # Get data
    if graph == "Box Plot":
        data_a, data_b = [], []  # A and B
    if graph == "League Trophies Range":
        data_c, data_d = [], []  # C and D
    xlabels_a_c_1, xlabels_a_c_2 = [], []  # A and C

    for season in range(start_season, end_season + 1):
        if graph == "Box Plot":  # A and B
            data_a.append(
                db["plot"][str(season)][
                    f"top_100_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}"
                ]
            )  # A
            data_b.append(
                [season, db["plot"][str(season)]["days"]]
                + list(
                    db["plot"][str(season)][
                        f"top_100_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_stats"
                    ]
                )
            )  # B
        if graph == "League Trophies Range":  # C and D
            # season data
            sd = db["plot"][str(season)]["League Trophies Range"]
            data_c.append(sd)  # C
            data_d.append(
                [season, db["plot"][str(season)]["days"],
                 f"{0:>4}-{sd[::-1][0]:<4}"]
                + [f"{sd[::-1][i]:>4}-{sd[::-1][i+1]:<4}" for i in range(1, 22, 2)]
                + [sd[::-1][23]]
            )  # D
        xlabels_a_c_1.append(str(season))  # A and C
        xlabels_a_c_2.append(str(db["plot"][str(season)]["days"]))  # A and C

    if graph == "Box Plot":
        # A: Plot graph
        # Initialize IO
        data_stream_a = io.BytesIO()

        # Plot Box Plot chart
        def Box_Plot(data, edge_color, fill_color):
            bp = ax_a_1.boxplot(
                data,
                patch_artist=True,
                flierprops=dict(
                    markerfacecolor=fill_color,
                    markeredgecolor=edge_color,
                    markeredgewidth=1.5,
                ),
            )

            for element in ["boxes", "whiskers", "fliers", "medians", "caps"]:
                plt.setp(bp[element], color=edge_color, linewidth=1.5)
                if end_season == curr_season:
                    plt.setp(bp[element][-1:], color="#FA4D56")
                    if element in ["whiskers", "caps"]:
                        plt.setp(bp[element][-2], color="#FA4D56")
                    elif element == "fliers":
                        plt.setp(
                            bp[element][-1],
                            markerfacecolor="#FED6D9",
                            markeredgecolor="#FA4D56",
                            markeredgewidth=1.5,
                        )

            for patch in bp["boxes"]:
                patch.set(
                    facecolor="#FED6D9"
                    if end_season == curr_season and patch == bp["boxes"][-1]
                    else fill_color
                )

            return bp

        fig, ax_a_1 = plt.subplots(
            facecolor="#2F3137", figsize=(8, 6), edgecolor="w", linewidth=3
        )
        ax_a_1.set_facecolor("#222222")
        bp = Box_Plot(data_a, "#1392E8", "#BBE6FD")

        # Legends
        legends_color = []
        legends_name = []

        if end_season != curr_season or (
            start_season != end_season and end_season == curr_season
        ):
            legends_color.append(bp["boxes"][0])
            legends_name.append(
                "Past Season" + ("" if one_past_season else "s"))
        if end_season == curr_season:
            legends_color.append(bp["boxes"][-1])
            legends_name.append("Current Season")

        ax_a_1.legend(
            legends_color,
            legends_name,
            loc="upper left",
            framealpha=1,
        )

        # Bottom axis
        ax_a_1.set_xticks(
            list(range(1, len(xlabels_a_c_1) + 1)), labels=xlabels_a_c_1)
        ax_a_1.set_title(
            f"Rocket Bot Royale - Box Plot of Top 100 Players' {mode[2:]} by Season"
            + ("" if one_past_season else "s"),
            color="w",
            weight="bold",
            pad=12,
        )
        ax_a_1.set_xlabel("Season", color="w", weight="bold")
        ax_a_1.set_ylabel(
            f"{mode[2:]}",
            color="w",
            weight="bold",
        )
        ax_a_1.tick_params(axis="both", which="both", colors="w")
        ax_a_1.xaxis.grid(True, alpha=0.5)
        if mode == "🧊 Points":
            multiple_locator = 100000
        elif mode == "💀 Player Kills":
            multiple_locator = 1000
        else:
            multiple_locator = 500
        ax_a_1.yaxis.set_major_locator(MultipleLocator(multiple_locator))
        ax_a_1.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax_a_1.yaxis.grid(which="major", alpha=0.5)
        ax_a_1.yaxis.grid(which="minor", alpha=0.2)

        # Top axis
        ax_a_2 = ax_a_1.secondary_xaxis("top")
        ax_a_2.set_xticks(
            list(range(1, len(xlabels_a_c_2) + 1)), labels=xlabels_a_c_2)
        ax_a_2.set_xlabel("Duration (days)", color="w", weight="bold")
        ax_a_2.tick_params(axis="both", colors="w")

        # Footer
        plt.figtext(
            0.98,
            0.03,
            "Generated at " + current_timestamp,
            ha="right",
            color="w",
            fontsize=8,
        )

        plt.tight_layout()
        plt.savefig(data_stream_a, format="png", dpi=250)
        plt.close()

        # Send the first graph
        data_stream_a.seek(0)
        chart_a = discord.File(
            data_stream_a,
            filename=f"Rocket Bot Royale - Box Plot of Top 100 Players' {mode[2:]} by Season (Season {start_season}"
            + (f" to {end_season}" if start_season != end_season else "")
            + f") {current_timestamp}.png",
        )
        await interaction.followup.send(file=chart_a)

        # B: Plot table
        # Initialize IO
        data_stream_b = io.BytesIO()

        column_headers = [
            "Season",
            "Duration (days)",
            "Min",
            "Lower Quartile",
            "Median",
            "Upper Quartile",
            "Max",
            "Mean",
        ]

        # Dynamic height
        fig_height = int(ceil((end_season - start_season + 1) / 3))
        if fig_height < 2:
            fig_height = 2  # Minimum height
        plt.figure(
            linewidth=3,
            facecolor="#2F3137",
            tight_layout={"pad": 2},
            figsize=(8, fig_height),
            edgecolor="w",
        )

        table = plt.table(
            cellText=[row for row in data_b],
            rowLoc="center",
            colLabels=column_headers,
            cellLoc="center",
            loc="center",
        )
        table.auto_set_font_size(False)

        # Hide axes
        ax_b = plt.gca()
        ax_b.get_xaxis().set_visible(False)
        ax_b.get_yaxis().set_visible(False)

        # Customize rows and cells
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor("w")
            cell.set_text_props(color="w")
            cell.set_text_props(
                fontproperties=FontProperties(weight="bold", size="x-small")
            )
            if row % 2 == 1:
                cell.set_facecolor("#1155CC")  # odd row
            elif row == 0:
                cell.set_facecolor("#222222")  # first row
            else:
                cell.set_facecolor("#3C78D8")  # even row
            if end_season == curr_season:
                if row == (end_season - start_season + 1):
                    cell.set_facecolor("#CC0000")  # current season row

        # Title
        ax_b.set_title(
            f"Rocket Bot Royale - Box Plot of Top 100 Players' {mode[2:]} by Season\nStats Table",
            color="w",
            weight="bold",
            pad=0,
        )

        # Hide axes border
        plt.box(on=None)
        plt.tight_layout()

        # Legends
        legends_name = []

        if end_season != curr_season or (
            start_season != end_season and end_season == curr_season
        ):
            legends_name.append(
                "Past Season" + ("" if one_past_season else "s"))
            bbox_to_anchor_x = 0.085
        if end_season == curr_season:
            legends_name.append("Current Season")
        bbox_to_anchor_x = 0.165 if start_season != end_season else 0.085

        for row in range(len(legends_name)):
            plt.bar(
                legends_name,
                0,
                label=legends_name[::-1][row],
            )  # Set width 0 to hide the bars

        (dark_blue,) = ax_b.plot(
            [],
            [],
            color="#1155CC",
            marker="s",
            markersize=8,
            fillstyle="top",
            linestyle="none",
            markeredgecolor="white",
            markeredgewidth=0,
        )

        (light_blue,) = ax_b.plot(
            [],
            [],
            color="#1155CC" if one_past_season == True else "#3C78D8",
            marker="s",
            markersize=8,
            fillstyle="bottom",
            linestyle="none",
            markeredgecolor="white",
            markeredgewidth=0,
        )

        (red,) = ax_b.plot(
            [],
            c="#CC0000",
            marker="s",
            markersize=8,
            linestyle="none",
            markeredgecolor="white",
            markeredgewidth=0,
        )

        handles, labels = ax_b.get_legend_handles_labels()
        ax_b.legend(
            ((dark_blue, light_blue), (red))[::-1]
            if start_season == end_season == curr_season
            else ((dark_blue, light_blue), (red)),
            labels[::-1],
            loc="lower center",
            bbox_to_anchor=(bbox_to_anchor_x, 0.85),
            ncol=2,
            fontsize=8,
            framealpha=1,
        )

        # Footer
        plt.figtext(
            0.98,
            0.03,
            "Generated at " + current_timestamp,
            ha="right",
            color="w",
            fontsize=8,
        )

        plt.tight_layout()
        plt.savefig(data_stream_b, format="png", dpi=250)
        plt.close()

        # Send the second graph
        data_stream_b.seek(0)
        chart_b = discord.File(
            data_stream_b,
            filename=f"Rocket Bot Royale - Box Plot of Top 100 Players' {mode[2:]} by Season (Season {start_season}"
            + (f" to {end_season}" if start_season != end_season else "")
            + f") {current_timestamp}.png",
        )
        await interaction.followup.send(file=chart_b)

    if graph == "League Trophies Range":
        # C: Plot League Trophies Range graph
        # Initialize IO
        data_stream_c = io.BytesIO()

        # Data
        # Use a transposed 2D-array to store range for all leagues in all seasons
        all_league_range = np.column_stack(tuple(data_c))

        if start_season == end_season:  # special fix for one season
            all_league_range = np.hstack(
                (all_league_range, all_league_range, all_league_range)
            )  # special fix for one season

        # Smooth curve
        season = np.arange(end_season - start_season + 1)
        if start_season == end_season:
            season = np.arange(end_season - start_season + 3)

        x_axis_lower_bound = season.min()
        x_axis_upper_bound = season.max()

        if start_season == end_season:
            x_axis_upper_bound += 2
        if end_season == curr_season:
            dotted_line_space = np.linspace(
                x_axis_lower_bound, x_axis_upper_bound, 500
            )  # 500 = smoothness
        solid_line_space = np.linspace(
            x_axis_lower_bound,
            x_axis_upper_bound - (1 if end_season == curr_season else 0),
            500,
        )  # 500 = smoothness

        dot = np.linspace(
            x_axis_lower_bound + (2 if start_season == end_season else 0),
            x_axis_upper_bound - (1 if start_season == end_season else 0),
            end_season - start_season + 1,
        )

        if end_season == curr_season:
            dotted_line_smooth = [
                np.exp(
                    PchipInterpolator(season, np.log(all_league_range[league]))(
                        dotted_line_space
                    )
                )
                for league in range(len(league_names) * 2 - 2)
            ]
        solid_line_smooth = [
            np.exp(
                PchipInterpolator(season, np.log(all_league_range[league]))(
                    solid_line_space
                )
            )
            for league in range(len(league_names) * 2 - 2)
        ]
        dot_smooth = [
            np.exp(PchipInterpolator(season, np.log(
                all_league_range[league]))(dot))
            for league in range(len(league_names) * 2 - 2)
        ]

        # Initialize figure and axis
        fig, ax_c_1 = plt.subplots(
            facecolor="#2F3137", figsize=(8, 6), edgecolor="w", linewidth=3
        )
        ax_c_1.set_facecolor("#222222")

        # Plot lines
        if end_season == curr_season:
            for league in range(len(league_names) * 2 - 2):
                ax_c_1.plot(
                    dotted_line_space,
                    dotted_line_smooth[::-1][league],
                    color=league_colors[::-1][league],
                    linewidth=2,
                    linestyle="--",
                    dashes=(3, 3),
                )  # full-length dotted parts
        if not (start_season == end_season == curr_season):
            for league in range(len(league_names) * 2 - 2):
                ax_c_1.plot(
                    solid_line_space,
                    solid_line_smooth[::-1][league],
                    color=league_colors[::-1][league],
                    linewidth=2,
                )  # partial-length solid parts above dotted parts

        # Plot dots
        for league in range(len(league_names) * 2 - 2):
            ax_c_1.plot(
                dot,
                dot_smooth[::-1][league],
                ".",
                color=league_colors[::-1][league],
                markersize=10,
            )

        # Fill colors
        line_space = (
            dotted_line_space if end_season == curr_season else solid_line_space
        )
        line_smooth = (
            dotted_line_smooth if end_season == curr_season else solid_line_smooth
        )

        for league in range(len(league_names)):
            ax_c_1.fill_between(
                line_space,
                line_smooth[0 if league == 0 else league * 2 - 1],
                0 if league == len(league_names) -
                1 else line_smooth[league * 2],
                color=league_colors[0 if league == 0 else league * 2 - 1],
                alpha=0.5,
                label=league_names[league],
                linewidth=0,
            )

        # Legends
        leg = ax_c_1.legend(
            loc="upper center",
            ncol=7,
            facecolor="#BBBBBB",
            labelcolor="black",
            framealpha=1,
            fontsize=8,
        )

        for legobj in leg.legendHandles:
            legobj.set_linewidth(1)

        # Bottom axis
        ax_c_1.set_xticks(
            list(
                range(
                    (2 if start_season == end_season else 0),
                    len(xlabels_a_c_1) +
                    (2 if start_season == end_season else 0),
                )
            ),
            labels=xlabels_a_c_1,
        )
        ax_c_1.set_title(
            "Rocket Bot Royale - League Trophies Range by Season",
            color="w",
            weight="bold",
            pad=12,
        )
        ax_c_1.set_xlabel("Season", color="w", weight="bold")
        ax_c_1.set_ylabel("Trophies", color="w", weight="bold")
        ax_c_1.tick_params(axis="both", which="both", colors="w")
        ax_c_1.xaxis.grid(True, alpha=0.5)
        ax_c_1.yaxis.set_major_locator(MultipleLocator(500))
        ax_c_1.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax_c_1.yaxis.grid(which="major", alpha=0.5)
        ax_c_1.yaxis.grid(which="minor", alpha=0.2)

        # Top axis
        ax_c_2 = ax_c_1.secondary_xaxis("top")
        ax_c_2.set_xticks(
            list(
                range(
                    (2 if start_season == end_season else 0),
                    len(xlabels_a_c_1) +
                    (2 if start_season == end_season else 0),
                )
            ),
            labels=xlabels_a_c_2,
        )
        ax_c_2.set_xlabel("Duration (days)", color="w", weight="bold")
        ax_c_2.tick_params(axis="both", colors="w")

        # Footer
        plt.figtext(
            0.98,
            0.03,
            "Generated at " + current_timestamp,
            ha="right",
            color="w",
            fontsize=8,
        )
        x0, x1, y0, y1 = plt.axis()
        dynamic_x_adjust = (
            1 if start_season == end_season else 0.02 *
            (end_season - start_season + 1)
        )
        plt.axis(
            (x0 + dynamic_x_adjust, x1 - dynamic_x_adjust, y0 + 100, y1 + 250)
        )  # Adjust margins

        plt.tight_layout()
        plt.savefig(data_stream_c, format="png", dpi=250)
        plt.close()

        # Send the first graph
        data_stream_c.seek(0)
        chart_c = discord.File(
            data_stream_c,
            filename=f"Rocket Bot Royale - League Trophies Range by Season (Season {start_season}"
            + (f" to {end_season}" if start_season != end_season else "")
            + f") {current_timestamp}.png",
        )
        await interaction.followup.send(file=chart_c)

        # D: Plot League Trophies Range table
        # Initialize IO
        data_stream_d = io.BytesIO()

        column_headers = ["Season", "Duration (days)"] + league_names[::-1]

        # Dynamic height
        fig_height = int(ceil((end_season - start_season + 1) / 3))
        if fig_height < 2:
            fig_height = 2  # Minimum height
        plt.figure(
            linewidth=3,
            facecolor="#2F3137",
            tight_layout={"pad": 2},
            figsize=(14, fig_height),
            edgecolor="w",
        )

        table = plt.table(
            cellText=[row for row in data_d],
            rowLoc="center",
            colLabels=column_headers,
            cellLoc="center",
            loc="center",
        )
        table.auto_set_font_size(False)

        # Hide axes
        ax_d = plt.gca()
        ax_d.get_xaxis().set_visible(False)
        ax_d.get_yaxis().set_visible(False)

        # Customize rows and cells
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor("w")
            cell.set_text_props(color="w")
            cell.set_text_props(
                fontproperties=FontProperties(weight="bold", size="x-small")
            )
            if col < 2:  # season and duration (days) columns
                if row % 2 == 1:
                    cell.set_facecolor("#1155CC")  # odd row(s)
                else:
                    cell.set_facecolor("#3C78D8")  # even row(s)
                if end_season == curr_season:
                    if row == (end_season - start_season + 1):
                        cell.set_facecolor("#CC0000")  # current season row
            else:  # league columns
                for i in range(2, 15):
                    if col == i:
                        cell.set_facecolor(
                            league_colors_orig[::-1][i - 2]
                            # odd and even row(s)
                            + ("88" if row % 2 == 1 else "CC")
                        )
                        if end_season == curr_season:
                            if row == (end_season - start_season + 1):
                                cell.set_facecolor(
                                    league_colors_orig[::-1][i - 2] + ("44")
                                )  # current season row
            if row == 0:
                cell.set_facecolor("#222222")  # first row

        # Title
        ax_d.set_title(
            "Rocket Bot Royale - League Trophies Range by Season",
            color="w",
            weight="bold",
            pad=0,
        )

        # Hide axes border
        plt.box(on=None)
        plt.tight_layout()

        # Legends
        legends_name = []

        if end_season != curr_season or (
            start_season != end_season and end_season == curr_season
        ):
            legends_name.append(
                "Past Season" + ("" if one_past_season else "s"))
            bbox_to_anchor_x = 0.05
        if end_season == curr_season:
            legends_name.append("Current Season")
            bbox_to_anchor_x = 0.1 if start_season != end_season else 0.05

        for row in range(len(legends_name)):
            plt.bar(
                legends_name,
                0,
                label=legends_name[::-1][row],
            )  # Set width 0 to hide the bars

        (dark_blue,) = ax_d.plot(
            [],
            [],
            color="#1155CC",
            marker="s",
            markersize=8,
            fillstyle="top",
            linestyle="none",
            markeredgecolor="white",
            markeredgewidth=0,
        )

        (light_blue,) = ax_d.plot(
            [],
            [],
            color="#1155CC" if one_past_season == True else "#3C78D8",
            marker="s",
            markersize=8,
            fillstyle="bottom",
            linestyle="none",
            markeredgecolor="white",
            markeredgewidth=0,
        )

        (red,) = ax_d.plot(
            [],
            c="#CC0000",
            marker="s",
            markersize=8,
            linestyle="none",
            markeredgecolor="white",
            markeredgewidth=0,
        )

        handles, labels = ax_d.get_legend_handles_labels()
        ax_d.legend(
            ((dark_blue, light_blue), (red))[::-1]
            if start_season == end_season == curr_season
            else ((dark_blue, light_blue), (red)),
            labels[::-1],
            loc="lower center",
            bbox_to_anchor=(bbox_to_anchor_x, 0.85),
            ncol=2,
            fontsize=8,
            framealpha=1,
        )

        # Footer
        plt.figtext(
            0.98,
            0.03,
            "Generated at " + current_timestamp,
            ha="right",
            color="w",
            fontsize=8,
        )

        plt.tight_layout()
        plt.savefig(data_stream_d, format="png", dpi=250)
        plt.close()

        # Send the second graph
        data_stream_d.seek(0)
        chart_d = discord.File(
            data_stream_d,
            filename=f"Rocket Bot Royale - League Trophies Range by Season (Season {start_season}"
            + (f" to {end_season}" if start_season != end_season else "")
            + f") {current_timestamp}.png",
        )
        await interaction.followup.send(file=chart_d)


@tree.command()
@app_commands.describe(
    reason="The reason of gain/loss trophies",
    your_trophies="How many trophies do you have",
    opponents_trophies="How many trophies does your opponent have",
    format="Ways to present (text/graph)"
)
async def trophies_calculator(
    interaction: discord.Interaction,
    reason: typing.Literal["Outranked", "Outranked by", "Killed", "Killed by"],
    your_trophies: int,
    opponents_trophies: int,
    format: typing.Literal["Text", "Graph"],
):
    """Calculate trophies gain/loss by reasons and plot the graph (optional)"""

    await interaction.response.defer(ephemeral=False, thinking=True)

    # Limit trophies range
    def clamp(n, minn, maxn):
        return max(min(maxn, n), minn)

    your_trophies = clamp(your_trophies, 0, 10000)
    opponents_trophies = clamp(opponents_trophies, 0, 10000)

    # Adjust variables depend on reason
    k_factor = 1 if "Outranked" in reason else 16
    score_a = 0 if "by" in reason else 1

    # Main multivariable-function (f(x,y) = z)
    def f(x, y):
        boost_factor = x/400 if x < 400 else 1
        boosted_k_factor = k_factor * boost_factor if score_a < 1 else k_factor
        trophies_change = boosted_k_factor * \
            (score_a-(10**(x/800))/(10**(x/800)+10**(y/800)))
        return trophies_change

    # Main graph
    if format == "Graph":
        fig, ax = plt.subplots(1, 1, facecolor=(
            "#2F3137"), figsize=(10, 8), edgecolor="w", linewidth=3)
        division = int(-(k_factor/2)+10)
        if "by" in reason:
            levels = [-i/division for i in range(k_factor*division+1)][::-1]
        else:
            levels = [i/division for i in range(k_factor*division+1)]

        # x, y, z values for contour plot
        extra_x, extra_y = 0, 0
        if your_trophies > 2800:
            extra_x = your_trophies - 2800 + 1400
        if opponents_trophies > 2800:
            extra_y = opponents_trophies - 2800 + 1400
        x, y = np.meshgrid(np.linspace(0+extra_x, 2800+extra_x, 100),
                           np.linspace(0+extra_y, 2800+extra_y, 100))
        v_func = np.vectorize(f)
        cf = ax.contourf(x, y, v_func(x, y), levels,
                         cmap='Reds_r' if "by" in reason else "Greens")

        ax.xaxis.set_major_locator(MultipleLocator(400))
        ax.xaxis.set_minor_locator(AutoMinorLocator(8))
        ax.yaxis.set_major_locator(MultipleLocator(400))
        ax.yaxis.set_minor_locator(AutoMinorLocator(8))
        ax.grid(which="major", alpha=0.5)
        ax.grid(which="minor", alpha=0.2)
        ax.set_title(
            f"Trophies {'Loss' if 'by' in reason else 'Gain'} ({reason})", color="#FFFFFF", weight="bold")
        ax.set_xlabel('Your Trophies', c="#FFFFFF", weight="bold")
        ax.set_ylabel("Opponent's Trophies", c="#FFFFFF", weight="bold")
        ax.tick_params(axis="both", which="both", colors="w")

        # Colorbar graph
        cb = fig.colorbar(cf)
        cb.set_label(
            f"Trophies {'Loss' if 'by' in reason else 'Gain'}", color="w", weight="bold")
        cb.set_ticks(levels)
        cb.ax.tick_params(axis="both", which="both", colors="w")

        # Boost Target vertical dotted line
        if 'by' in reason and your_trophies <= 2800:
            plt.axvline(x=400, color='k', ls='--')
            plt.text(200, 2600, 'Boost Target\n(400)', color='k', ha='center')

        # Plot dot and annotate
        x_adjust = 550 if your_trophies > 2200 else 0
        y_adjust = 200 if opponents_trophies > 2600 else 0
        plt.text(your_trophies+25-x_adjust, opponents_trophies+75-y_adjust,
                 f'f({your_trophies},{opponents_trophies})={f(your_trophies, opponents_trophies):.2f}', color='white', bbox=dict(facecolor='black', edgecolor='white', boxstyle='round'), size="10")
        plt.scatter(your_trophies, opponents_trophies,
                    facecolor='black', edgecolor='white', zorder=3)

        plt.tight_layout()

        # Save the graph
        data_stream = io.BytesIO()
        plt.savefig(data_stream, format="png", dpi=250)
        plt.close()

        # Send the graph
        data_stream.seek(0)
        chart = discord.File(
            data_stream,
            filename=f"{reason.lower()}_{your_trophies}_{opponents_trophies}.png",
        )
        await interaction.followup.send(file=chart)
    else:
        embed = discord.Embed()
        embed.title = "Rocket Bot Royale 🚀"
        title = "Opponent's Trophies: "
        embed.add_field(
            name="🧮 ***Trophies Calculator***",
            value=f"```ansi\n{'Reason: ':>21}{reason}\n{'Your Trophies: ':>21}{'🏆 '+str(your_trophies)}\n{title:>21}{'🏆 '+str(opponents_trophies)}\n{'Trophies Change: ':>21}\u001b[2;{'31' if 'by' in reason else '32'}m{f(your_trophies, opponents_trophies):.2f}\u001b[0m```"
        )
        await interaction.followup.send(embed=embed)


@tree.command(guild=discord.Object(id=989993645006536704))
async def sync_commands(interaction: discord.Interaction):
    await tree.sync()
    await tree.sync(guild=discord.Object(id=989993645006536704))
    await interaction.response.send_message("Commands synced.")


def main():
    try:
        client.run(discord_token)
    except:
        os.system("kill 1")


if __name__ == "__main__":
    main()
""
