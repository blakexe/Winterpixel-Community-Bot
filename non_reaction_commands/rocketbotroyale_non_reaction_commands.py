import random
import discord
import json
import os
import io
import textwrap
import typing
import aiohttp
import datetime
import timeago
import itertools
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from replit import db
from matplotlib.cbook import boxplot_stats
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from scipy.interpolate import PchipInterpolator
from fandom import set_wiki, page
from mediawiki import MediaWiki
from statistics import mean
from matplotlib.gridspec import GridSpec
from math import ceil
from collections import Counter
from discord import app_commands
from misc.random_tank_get import get_a_random_tank
from clients.rocketbotroyale_client import RocketBotRoyaleClient


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
rocket_bot_royale_server_config = {}


# Initialize rocket bot royale client
rocket_bot_royale_client = RocketBotRoyaleClient(rbr_mm_email_password, rbr_mm_email_password)


async def refresh_config():
  """Refresh Rocket Bot Royale game configuration"""

  global rocket_bot_royale_server_config

  response = await rocket_bot_royale_client.get_config()
  rocket_bot_royale_server_config = json.loads(response["payload"])

  global rocket_bot_royale_current_season, league_range_orig, league_range, league_names, league_colors_orig, league_colors
  rocket_bot_royale_current_season = rocket_bot_royale_server_config["season"]
  league_range_orig = [
    rocket_bot_royale_server_config["trophy_tiers"][league]["maximum_rank"]
      for league in range(len(rocket_bot_royale_server_config["trophy_tiers"]) - 1)
  ]
  league_range = [
      league_range_orig[i] if j == 0 else league_range_orig[i] + 1
      for i in range(len(league_range_orig))
      for j in range(min(len(league_range_orig) - i + 1, 2))
  ]
  league_names = [
    rocket_bot_royale_server_config["trophy_tiers"][league]["name"]
      for league in range(len(rocket_bot_royale_server_config["trophy_tiers"]))
  ]
  league_colors_orig = [
      f"#{rocket_bot_royale_server_config['trophy_tiers'][league]['color']}"
      for league in range(len(rocket_bot_royale_server_config["trophy_tiers"]))
  ]
  league_colors = [
      color for color in league_colors_orig for _ in (0, 1)][1:-1]


def rocket_bot_royale_season_info(season):
    season_durations, season_start_numbers, season_start_timestamps = (
        [] for i in range(3)
    )
    for key in rocket_bot_royale_server_config["season_definitions"]:
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
    
    if season == rocket_bot_royale_current_season:
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
    
    rocket_bot_royale_all_season_info = [season_start, season_end,
                       season_days, status, time_remaining]
    return rocket_bot_royale_all_season_info
    

class RocketBotRoyale(app_commands.Group): # RBR_NRC
    """Rocket Bot Royale non-reaction commands"""
    
    def __init__(self, bot: discord.client):
        super().__init__()
    
    
    # @tree.command()
    # async def dump(self, interaction: discord.Interaction,
    #     mode: typing.Literal[
    #          "trophies", "points", "wins", "kills", "bot_kills"
    #     ],
    #     limit: int = 10000,
    #     cursor: str = "",
    #     season: int = 1,
    # ):
    #     """🟡 Dump the full Rocket Bot Royale season leaderboard insdie repl"""

    #     await refresh_config()
        
    #     await interaction.response.defer(ephemeral=False, thinking=True)

    #     if season < 11 and mode == "trophies":
    #         mode = "points"
    #     all_records = []
    #     next_cursor = cursor
    #     have_next_cursor = True
    #     while have_next_cursor == True:
    #         response = await rocket_bot_royale_client.query_leaderboard(
    #             season,
    #             f"tankkings_{mode.lower()}",
    #             limit,
    #             next_cursor
    #         )
    #         payload = json.loads(response["payload"])
    #         records = payload['records']
    #         try:
    #             next_cursor = payload["next_cursor"]
    #         except:
    #             have_next_cursor = False
    #         first, last = records[0]['rank'], records[-1]['rank']
    #         print(first, last)
    #         all_records.append(records)
    #         if last >= 999999:
    #             break
    #     all_records_list = [
    #         single_record
    #         for grouped_single_records in all_records
    #         for single_record in grouped_single_records
    #     ]
    #     print(len(all_records_list))
    #     output_json = open(f"tankkings_{mode}_{season}.json", "w")
    #     output_json.write(json.dumps(all_records_list))
    #     df = pd.read_json(f"tankkings_{mode}_{season}.json")
    #     df.to_csv(f"tankkings_{mode}_{season}.csv")

    #     await interaction.followup.send("Done. Check inside Repl.")

    
    @tree.command()
    @app_commands.describe(
        user_type="Use either User ID or Friend Code of the user",
        id_or_code="User ID or Friend Code of the user",
        section="Section(s) to be shown",
    )
    async def user_info(
        self,
        interaction: discord.Interaction,
        user_type: typing.Literal["User ID", "Friend Code"],
        id_or_code: str,
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
        """🟡 Return info about a specified Rocket Bot Royale user with optional section(s)"""

        await refresh_config()
        
        await interaction.response.defer(ephemeral=False, thinking=True)

        # If the user specified a friend code we need to query the server for their ID.
        try:
            if user_type == "Friend Code":
                id_response = await rocket_bot_royale_client.friend_code_to_id(id_or_code)
                id = json.loads(id_response["payload"])["user_id"]
            else:
                id = id_or_code
            
            # Get user data
            response = await rocket_bot_royale_client.user_info(id)
            user_data = json.loads(response["payload"])[0]
            metadata = user_data["metadata"]
        except aiohttp.ClientResponseError:
            # The code is wrong, send an error response
            await interaction.followup.send(
                embed=discord.Embed(color=0xFF0000,
                                    title="❌ Player not found ❌")
            )
            return

        # Get award config
        awards_config = rocket_bot_royale_server_config["awards"]
        default_award = {"type": "Unknown", "name": "Unknown"}

        # Get goal config
        goals_config = rocket_bot_royale_server_config["player_goals"]
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
            has_season_pass = rocket_bot_royale_server_config["season"] in metadata["season_passes"]
        except:
            has_season_pass = False
        try:
            has_made_a_purchase = metadata["has_made_a_purchase"]
        except:
            has_made_a_purchase = False
        level = metadata["progress"]["level"]
        XP = metadata["progress"]["xp"]
        friend_code = metadata["friend_code"]
        id = user_data["user_id"]

        if section != "🍩 Graphs only":
            # Add general player info
            general_info = "```ansi\n"
            general_info += f"Username: {username}\n"
            dt_create_time = f"{datetime.datetime.fromtimestamp(create_time):%Y-%m-%d %H:%M:%S}"
            general_info += f"Create Time: {dt_create_time} UTC ({timeago.format(dt_create_time, datetime.datetime.now())})\n"
            try:
                dt_timed_bonus = f"{datetime.datetime.fromtimestamp(timed_bonus_last_collect):%Y-%m-%d %H:%M:%S}"
            except Exception:
                dt_timed_bonus = "N.A."
            general_info += "Last Bonus: " + (
                f"{dt_timed_bonus} UTC ({timeago.format(dt_timed_bonus, datetime.datetime.now())})\n"
                if timed_bonus_last_collect != "N.A." else "N.A.\n")
            general_info += f"Current Tank: {current_tank}\n"
            general_info += f"Current Trail: {current_trail}\n"
            general_info += f"Current Parachute: {current_parachute}\n"
            general_info += f"Current Badge: {current_badge}\n"
            general_info += f"Level: {level}\n"
            max_level = len(rocket_bot_royale_server_config["player_progression"]["xp_levels"])
            try:
                XP_target = rocket_bot_royale_server_config["player_progression"]["xp_levels"][level][
                    str(level + 1)
                ]["xp_target"]
                reach_max_level = False
            except IndexError:
                XP_target = rocket_bot_royale_server_config["player_progression"]["xp_levels"][-1][
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
            general_info += (
                "Has Season Pass: \u001b[2;"
                + ("32" if has_season_pass else "31")
                + f"m{has_season_pass}\u001b[0m\n"
            )
            general_info += (
                "Monetary Purchase: \u001b[2;"
                + ("32" if has_made_a_purchase else "31")
                + f"m{has_made_a_purchase}\u001b[0m\n"
            )
            general_info += (
                "Online: \u001b[2;" + ("32" if is_online else "31") +
                f"m{is_online}\u001b[0m\n"
            )
            general_info += "```"

            # Add to embed
            message1 = ""
            message1 += f"📓 ***General Info***:\n{general_info}\n"

            # Send
            await interaction.followup.send(
                embed=discord.Embed(title="Rocket Bot Royale <:rocket_mint:910253491019202661>\nDetailed Player Info:", description=message1, color=0xFFFF00)
            )

        if section in {"with 📊 Seasons Records", "All"}:
            # Create seasons records list
            seasons_records_list = "```ansi\n"

            points_label = "\u001b[1;2mBy points (Season 1 to 10)\u001b[0m\n"
            points = f"{'Season:':<8}{'Days:':<6}{'Rank:':<10}{'Points:':<12}{'Games:':<7}{'Pass:'}\n{'─'*56}\n"
            trophies_label = (
                f"\u001b[1;2mBy trophies (Season 11 to {rocket_bot_royale_current_season})\u001b[0m\n"
            )
            trophies = f"{'Season:':<8}{'Days:':<6}{'Rank:':<10}{'Trophies:':<10}{'League:':<10}{'Games:':<7}{'Pass:'}\n{'─'*56}\n"
            points_record = False
            trophies_record = False

            for season in range(1, rocket_bot_royale_current_season + 1):  # From first season to current season
                response = await rocket_bot_royale_client.query_leaderboard(
                    season,
                    ("tankkings_points" if season <= 10 else "tankkings_trophies"),
                    1,
                    "",
                    id,
                )
                records = json.loads(response["payload"])["owner_records"]
                print(records)

                for record in records:
                    if record["rank"] == 0:
                        mode = "points" if season < 11 else "trophies"
                        df = pd.read_csv(f"Winterpixel-Community-Bot/old_season_leaderboard/tankkings_{mode}_{season}.csv")
                        try:
                            rank = df[df["owner_id"] == id]['rank'].values[0]
                        except:
                            pass
                    else:
                        rank = record["rank"]
    
                    if season >= 6:
                        try:
                            if season in metadata["season_passes"]:
                                season_pass = "\u001b[1;32mTrue\u001b[0m"
                            else:
                                season_pass = "\u001b[1;31mFalse\u001b[0m"
                        except KeyError:
                            season_pass = "\u001b[1;31mFalse\u001b[0m"
                    else:
                      season_pass = "N.A."
    
                    rank_emoji = "  "
                    if season != rocket_bot_royale_current_season:
                        if rank == 1:
                            rank_emoji = "🥇"
                        elif rank == 2:
                            rank_emoji = "🥈"
                        elif rank == 3:
                            rank_emoji = "🥉"
    
                    required_season_info = rocket_bot_royale_season_info(season)
    
                    if season <= 10:
                        points_record = True
                        points += f"{season:^8}{required_season_info[2][:-5]:<6}{rank_emoji:<1}{rank:<8,}🧊{record['score']:<10,}{record['num_score']:<7,}{season_pass}\n"
                    else:
                        trophies_record = True
                        trophies += (
                            (f"{'CURRENT SEASON'.center(56, '-')}\n" if season == rocket_bot_royale_current_season else "")
                            + f"{season:^8}{required_season_info[2][:-5]:<6}{rank_emoji:<1}{rank:<8,}🏆{record['score']:<9,}{league_names[np.searchsorted(league_range_orig, rank)]:<9}{record['num_score']:<7,}{season_pass}\n"
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
                embed=discord.Embed(description=message2, color=0xFFFF00)
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
                embed=discord.Embed(description=message3, color=0xFFFF00)
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
                "ranked_royale_played": 0,
                "ranked_royale_won": 0,
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
            ranked_royale_won_pct = 0
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
                    elif key == 'ranked_royale_played':
                        labels_a_1.append('Ranked\nRoyale')
                        sizes_a_1.append(keys_order['ranked_royale_played'])
                        colors_a_1.append(ORANGE)
                        sizes_a_2.append([keys_order['ranked_royale_played']-keys_order['ranked_royale_won'], keys_order['ranked_royale_won']])
                        colors_a_2.append([DARK_ORANGE, LIGHT_ORANGE])
                        ranked_royale_won_pct = keys_order["ranked_royale_won"] / \
                            keys_order["ranked_royale_played"]
                        sizes_c.append(float(f"{ranked_royale_won_pct*100:.1f}"))
                        total_games_played += keys_order['ranked_royale_played']
                        total_games_won += keys_order['ranked_royale_won']
                    elif key != 'total_games_played':  # In case of new game mode added
                        labels_a_1.append(key.replace('_played', '').title())
                        sizes_a_1.append(keys_order[key])
                        colors_a_1.append(DARKER_GREY)
                        sizes_a_2.append([keys_order[key]-keys_order[key.replace('_played',
                                                                                 '_won')], keys_order[key.replace('_played', '_won')]])
                        colors_a_2.append([DARK_DARKER_GREY, LIGHT_DARKER_GREY])
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
                    19.2, 10.8), edgecolor="#FFFF00" if section == "🍩 Graphs only" else "w", linewidth=3 if section == "🍩 Graphs only" else 0)  # 1920x1080 pixels

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
                try:
                    kills_using_missiles_pct *= 100
                except:
                    kills_using_missiles_pct = 0

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
                keys_order["ranked_royale_won"] = "{:<6}".format(
                    keys_order["ranked_royale_won"]) + "(" + f"{ranked_royale_won_pct*100:>2.0f}" + "%)"
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
                ) + "(" + f"{kills_using_missiles_pct:>2.0f}" + "%)"
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
                embed1 = discord.Embed(description=message4, color=0xFFFF00)
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
                embed=discord.Embed(description=message5, color=0xFFFF00)
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
                    embed=discord.Embed(description=message6, color=0xFFFF00)
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
                    embed=discord.Embed(description=message7, color=0xFFFF00)
                )

            if section in {"with 🪂 Parachutes", "with All Cosmetics", "All"}:
                # Add to embed
                message8 = ""
                message8 += f"🪂 ***Parachutes***:\n{parachute_list}\n"

                # Send
                await interaction.followup.send(
                    embed=discord.Embed(description=message8, color=0xFFFF00)
                )

            if section in {"with 🌟 Trails", "with All Cosmetics", "All"}:
                # Add to embed
                message9 = ""
                message9 += f"🌟 ***Trails***:\n{trail_list}\n"

                # Send
                await interaction.followup.send(
                    embed=discord.Embed(description=message9, color=0xFFFF00)
                )

    
    @tree.command()
    @app_commands.describe(
        one_star="Number of one-star skin(s) owned",
        two_star="Number of two-star skin(s) owned",
        three_star="Number of three-star skin(s) owned",
    )
    async def optimize_crate(
        self, interaction: discord.Interaction, one_star: int, two_star: int, three_star: int
    ):
        """🟡 Optimize the use of in game crates and Estimate the amount of coins in Rocket Bot Royale"""

        await refresh_config()
        
        await interaction.response.defer(ephemeral=False, thinking=True)

        one_star_total = 0
        two_star_total = 0
        three_star_total = 0

        for key, value in rocket_bot_royale_server_config["awards"].items():
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
            rocket_bot_royale_server_config["lootbox_rarity_odds"]["common"],
            rocket_bot_royale_server_config["lootbox_rarity_odds"]["rare"],
            rocket_bot_royale_server_config["lootbox_rarity_odds"]["legendary"],
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

        basic_crate_price = rocket_bot_royale_server_config["lootbox_coin_cost"]
        elite_crate_price = rocket_bot_royale_server_config["unique_lootbox_coin_cost"]

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
    @app_commands.describe(
        graph="Box Plot: Top 100 players' records / League Trophies Range",
        mode="🏆 Trophies / 🧊 Points / 🎉 Wins / 💀 Player Kills / 🤖 Bot Kills",
        start_season="🏆 Trophies: Season 11 or later / Others: Season 1 or later, default all",
        end_season=">= start_season, default all",
    )
    async def plot_season(
        self,
        interaction: discord.Interaction,
        graph: typing.Literal["Box Plot", "League Trophies Range"],
        mode: typing.Literal[
            "🏆 Trophies", "🧊 Points", "🎉 Wins", "💀 Player Kills", "🤖 Bot Kills"
        ],
        start_season: int = 1,
        end_season: int = -1,
    ):
        """🟡 Plot statistics graph and table by various modes in season(s) in Rocket Bot Royale"""

        await refresh_config()
        
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
        if start_season > rocket_bot_royale_current_season:
            start_season = rocket_bot_royale_current_season

        if end_season < (11 if mode == "🏆 Trophies" else 1):
            start_season = 11 if mode == "🏆 Trophies" else 1
        if end_season > rocket_bot_royale_current_season or end_season == -1:
            end_season = rocket_bot_royale_current_season
        if end_season < start_season:
            end_season = start_season

        # Singular or plural form for legends
        if (start_season == rocket_bot_royale_current_season - 1 and end_season == rocket_bot_royale_current_season) or (
            start_season == end_season and start_season != rocket_bot_royale_current_season
        ):
            one_past_season = True
        else:
            one_past_season = False

        # Get leaderboard info and update replit's database if necessary
        last_update_season = 0
        for season in range(
            max(start_season, db["plot"]["last_update_season"]),
            min(end_season, rocket_bot_royale_current_season) + 1,
        ):
            if season > last_update_season:
                last_update_season = season

            if str(season) not in db["plot"]:
                db["plot"][str(season)] = dict()
                db["plot"][str(season)]["days"] = rocket_bot_royale_season_info(season)[2][:-5]

            if (
                season < rocket_bot_royale_current_season
            ):  # past seasons (store for first time / overwrite for last season)
                update_modes = ["points", "trophies", "wins", "kills", "bot_kills"]
                if season < 11:
                    update_modes.remove("trophies")

                for update_mode in update_modes:
                    response = await rocket_bot_royale_client.query_leaderboard(
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
                    response = await rocket_bot_royale_client.query_leaderboard(
                        season, "tankkings_trophies", 8002
                    )
                    records = json.loads(response["payload"])["records"]

                    db["plot"][str(season)]["League Trophies Range"] = [
                        records[range - 1]["score"] for range in league_range
                    ]

            else:  # current season
                limit = 100 if graph == "Box Plot" else 8002
                response = await rocket_bot_royale_client.query_leaderboard(
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

        if end_season == rocket_bot_royale_current_season and not (enough_records):
            end_season = rocket_bot_royale_current_season - 1
            if start_season == rocket_bot_royale_current_season:
                start_season = rocket_bot_royale_current_season - 1

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
                    if end_season == rocket_bot_royale_current_season:
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
                        if end_season == rocket_bot_royale_current_season and patch == bp["boxes"][-1]
                        else fill_color
                    )

                return bp

            fig, ax_a_1 = plt.subplots(
                facecolor="#2F3137", figsize=(8, 6), edgecolor="#FFFF00", linewidth=3
            )
            ax_a_1.set_facecolor("#222222")
            bp = Box_Plot(data_a, "#1392E8", "#BBE6FD")

            # Legends
            legends_color = []
            legends_name = []

            if end_season != rocket_bot_royale_current_season or (
                start_season != end_season and end_season == rocket_bot_royale_current_season
            ):
                legends_color.append(bp["boxes"][0])
                legends_name.append(
                    "Past Season" + ("" if one_past_season else "s"))
            if end_season == rocket_bot_royale_current_season:
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
                edgecolor="#FFFF00",
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
                if end_season == rocket_bot_royale_current_season:
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

            if end_season != rocket_bot_royale_current_season or (
                start_season != end_season and end_season == rocket_bot_royale_current_season
            ):
                legends_name.append(
                    "Past Season" + ("" if one_past_season else "s"))
                bbox_to_anchor_x = 0.085
            if end_season == rocket_bot_royale_current_season:
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
                if start_season == end_season == rocket_bot_royale_current_season
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
            if end_season == rocket_bot_royale_current_season:
                dotted_line_space = np.linspace(
                    x_axis_lower_bound, x_axis_upper_bound, 500
                )  # 500 = smoothness
            solid_line_space = np.linspace(
                x_axis_lower_bound,
                x_axis_upper_bound - (1 if end_season == rocket_bot_royale_current_season else 0),
                500,
            )  # 500 = smoothness

            dot = np.linspace(
                x_axis_lower_bound + (2 if start_season == end_season else 0),
                x_axis_upper_bound - (1 if start_season == end_season else 0),
                end_season - start_season + 1,
            )

            if end_season == rocket_bot_royale_current_season:
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
                facecolor="#2F3137", figsize=(8, 6), edgecolor="#FFFF00", linewidth=3
            )
            ax_c_1.set_facecolor("#222222")

            # Plot lines
            if end_season == rocket_bot_royale_current_season:
                for league in range(len(league_names) * 2 - 2):
                    ax_c_1.plot(
                        dotted_line_space,
                        dotted_line_smooth[::-1][league],
                        color=league_colors[::-1][league],
                        linewidth=2,
                        linestyle="--",
                        dashes=(3, 3),
                    )  # full-length dotted parts
            if not (start_season == end_season == rocket_bot_royale_current_season):
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
                dotted_line_space if end_season == rocket_bot_royale_current_season else solid_line_space
            )
            line_smooth = (
                dotted_line_smooth if end_season == rocket_bot_royale_current_season else solid_line_smooth
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
                edgecolor="#FFFF00",
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
                    if end_season == rocket_bot_royale_current_season:
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
                            if end_season == rocket_bot_royale_current_season:
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

            if end_season != rocket_bot_royale_current_season or (
                start_season != end_season and end_season == rocket_bot_royale_current_season
            ):
                legends_name.append(
                    "Past Season" + ("" if one_past_season else "s"))
                bbox_to_anchor_x = 0.05
            if end_season == rocket_bot_royale_current_season:
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
                if start_season == end_season == rocket_bot_royale_current_season
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
    async def trophies_calc(
        self,
        interaction: discord.Interaction,
        reason: typing.Literal["Outranked", "Outranked by", "Killed", "Killed by"],
        your_trophies: int,
        opponents_trophies: int,
        format: typing.Literal["Text", "Graph"],
    ):
        """🟡 Calculate trophies gain/loss by reasons and plot the graph (optional) in RBR (*outdated)"""

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
                "#2F3137"), figsize=(10, 8), edgecolor="#FFFF00", linewidth=3)
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
            embed.title = "Rocket Bot Royale <:rocket_mint:910253491019202661>"
            embed.color = 0xFFFF00
            title = "Opponent's Trophies: "
            embed.add_field(
                name="🧮 ***Trophies Calculator***",
                value=f"```ansi\n{'Reason: ':>21}{reason}\n{'Your Trophies: ':>21}{'🏆 '+str(your_trophies)}\n{title:>21}{'🏆 '+str(opponents_trophies)}\n{'Trophies Change: ':>21}\u001b[2;{'31' if 'by' in reason else '32'}m{f(your_trophies, opponents_trophies):.2f}\u001b[0m```"
            )
            await interaction.followup.send(embed=embed)

    
    @tree.command()
    @app_commands.describe(
        article="The article you want to look up. Make sure capitalization is correct!"
    )
    async def fandom(self, interaction: discord.Interaction, article: str):
        """🟡 Fetch any articles from Rocket Bot Royale fandom here!"""

        await interaction.response.defer(ephemeral=False, thinking=True)

        # Set targeted fandom site's api for fandom command
        set_wiki("rocketbotroyale")
        rocketbotroyale = MediaWiki(url="https://rocketbotroyale.fandom.com/api.php")

        p = rocketbotroyale.page(article)
        try:
            page1 = page(title=article)
            sent_embed = await interaction.followup.send(
                embed=discord.Embed(description="Fetching page...")
            )
            output = discord.Embed(
                color=0xFFFF00,
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
    async def random_tank(self, interaction: discord.Interaction):
        """🟡 Get a random tank (*outdated)"""

        await refresh_config()

        await interaction.response.defer(ephemeral=False, thinking=True)

        chosen_tank = get_a_random_tank(False)

        # Get emoji's source url stored on Discord
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
        awards_config = rocket_bot_royale_server_config["awards"]
        for key, value in awards_config.items():
            try:
                if value["type"] == "skin_set":
                    if value["name"] == tank_name:
                        description = value["description"]
                        if value["rarity"] == "common":
                            rarity_icon = "⭐"
                            # color = 0x49C8FF
                        elif value["rarity"] == "rare":
                            rarity_icon = "⭐⭐"
                            # color = 0xCB6DFF
                        elif value["rarity"] == "legendary":
                            rarity_icon = "⭐⭐⭐"
                            # color = 0xFFDC5E
                        elif value["rarity"] == "purchased":
                            rarity_icon = "💰"
                            # color = 0x80FF7C
                        elif value["rarity"] == "earned":
                            rarity_icon = "🏅"
                            # color = 0xF1689D
                elif value["type"] == "skin":
                    if value["name"] == tank_name:  # 3 bot skins
                        rarity_icon = ""
                        description = value["description"]
                        # color = 0xFFFFFF
                        break
            except:
                pass

        # Send
        embed = discord.Embed(
            title=f"{rarity_icon} {tank_name}", description=description, color=0xFFFF00
        )
        embed.set_image(url=img_link)
        await interaction.followup.send(embed=embed)

    
    @tree.command()
    async def get_config(self, interaction: discord.Interaction):
        """🟡 Get the most updated Rocket Bot Royale server config"""

        await refresh_config()

        file = io.StringIO(json.dumps(rocket_bot_royale_server_config))
        await interaction.response.send_message(
            file=discord.File(fp=file, filename="rocket_bot_royale_server_config.json")
        )
    
