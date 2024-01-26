import discord
import json
import os
import io
import aiohttp
import datetime
import timeago
import typing
import numpy as np
import time
import flag
import pycountry
from math import ceil
from discord import app_commands
from clients.gooberdash_client import GooberDashClient


try:
    discord_token = os.environ["discord_token"]
    gd_email = os.environ["gd_email"]
    gd_password = os.environ["gd_password"]
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
goober_dash_server_config = {}


# Initialize goober dash client
goober_dash_client = GooberDashClient(gd_email, gd_password)


async def refresh_config():
  """Refresh Goober Dash game configuration"""

  global goober_dash_server_config

  response = await goober_dash_client.get_config()
  goober_dash_server_config = response

  global goober_dash_current_season
  
  duration, start_number, start_time = (
      [] for i in range(3)
  )
  for key in goober_dash_server_config["metadata"]["seasons"]["season_templates"]:
      duration.append(key["duration"])
      start_number.append(key["start_number"])
      start_time.append(key["start_time"])

  def get_current_season(current_timestamp):
      index = np.searchsorted(start_time, current_timestamp)
      accumulate_start_time = start_time[index-1]
      count = 0
      while accumulate_start_time <= current_timestamp:
          accumulate_start_time += duration[index-1]
          count += 1
      current_season = start_number[index-1] + count - 1
      return current_season

  goober_dash_current_season = get_current_season(time.time())


def goober_dash_season_info(season, mode):
    duration, start_number, start_time = (
        [] for i in range(3)
    )
    for key in goober_dash_server_config["metadata"]["seasons"]["season_templates"]:
        duration.append(key["duration"])
        start_number.append(key["start_number"])
        start_time.append(key["start_time"])
    
    season_index = np.searchsorted(start_number, season + 1) - 1
    
    season_start_timestamp = (
        start_time[season_index]
        + (season - start_number[season_index]
           ) * duration[season_index]
    )
    season_start = f"{datetime.datetime.utcfromtimestamp(season_start_timestamp):%Y-%m-%d %H:%M:%S} UTC"
    
    season_end_timestamp = season_start_timestamp + \
        duration[season_index]
    season_end = f"{datetime.datetime.utcfromtimestamp(season_end_timestamp):%Y-%m-%d %H:%M:%S} UTC"
    
    season_duration = duration[season_index]
    
    if mode == "long":
        season_days = f"{season_duration // (24 * 3600)} days {season_duration % (24 * 3600) // 3600} hours"
    elif mode == "short":
        s = season_duration / (24 * 3600)
        season_days = f"{'{:.2f}'.format(s) if s%1 != 0 else int(s)} days"
    
    current_timestamp = time.time()
    if current_timestamp > season_end_timestamp:
        status = "\u001b[2;31mEnded\u001b[0m"
    else:
        status = f"\u001b[2;32mIn progress\u001b[0m ({((current_timestamp - season_start_timestamp)/season_duration)*100:.0f} %)"
    
    if season == goober_dash_current_season:
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
    
    goober_dash_all_season_info = [season_start, season_end,
                       season_days, status, time_remaining]
    return goober_dash_all_season_info


class GooberDash(app_commands.Group): # RBR_NRC
    """GooberDash non-reaction commands"""

    def __init__(self, bot: discord.client):
        super().__init__()


    # @tree.command()
    # @app_commands.describe(
    #     user_type="User either User ID or Username of the user",
    #     id_or_username="User ID / Username of the user (Not Guest)(Exact Capitalization)('&'='space' if necessary)"
    #     # section="Section(s) to be shown",
    # )
    # async def user_info(
    #     self,
    #     interaction: discord.Interaction,
    #     user_type: typing.Literal[
    #         "User ID",
    #         "Username"
    #     ],
    #     id_or_username: str,
    #     # section: typing.Literal[
    #     #     "📓 General Info only",
    #     #     "with 📊 Seasons Records",
    #     #     "with 🎖️ Medals",
    #     #     "with 🗒️ Stats",
    #     #     "All",
    #     # ],
    # ):
    #     """🔵 Return info about a specified Goober Dash user"""
    #     # """🔵 Return info about a specified Goober Dash user with optional section(s)"""

    #     await refresh_config()

    #     await interaction.response.defer(ephemeral=False, thinking=True)

    #     # Get User ID (if Username is provided), create time and online status
    #     try:
    #         if user_type == "User ID":
    #             response = await goober_dash_client.user_info_2(id_or_username)
    #         else:
    #             id_or_username = id_or_username.replace("&", " ")
    #             response = await goober_dash_client.user_info_2("", id_or_username)
    #         user_info_2 = response["users"][0]
    #         user_id = user_info_2["id"]
    #         username = user_info_2["username"]
    #         create_time = user_info_2["create_time"]
    #         try:
    #             is_online = user_info_2["online"]
    #         except:
    #             is_online = False
    #     except Exception:
    #         # The code is wrong, send an error response
    #         await interaction.followup.send(
    #             embed=discord.Embed(color=0xFF0000,
    #                                 title="❌ Player not found ❌")
    #         )
    #         return

    #     # Get user data
    #     response = await goober_dash_client.user_info(user_id)
    #     user_data = json.loads(response)

    #     # Get medals config
    #     awards_config = goober_dash_server_config["awards"]["awards"]
        
    #     # Get cosmetics config
    #     cosmetics_config = goober_dash_server_config["cosmetics"]

    #     # Get general player info
    #     level = user_data["level"]

    #     cosmetics_type_keys = ["body", "hat", "suit", "hand", "color"]
    #     cosmetics_dict = dict()
    #     for cosmetics_type in cosmetics_type_keys:
    #         try:
    #             cosmetics_type_all_info = ""
    #             cosmetics_type_all_info += f"{str(cosmetics_config.get(user_data['skin'][cosmetics_type])['name']):<20} "
    #             cosmetics_type_all_info += f"Level {str(cosmetics_config.get(user_data['skin'][cosmetics_type])['level']):<2} "
    #             try:
    #                 rarity = str(cosmetics_config.get(user_data['skin'][cosmetics_type])['rarity'])
    #                 if rarity == "common":
    #                     cosmetics_type_all_info += rarity.title()
    #                 elif rarity == "rare":
    #                     cosmetics_type_all_info += f"\u001b[2;32m{rarity.title()}\u001b[0m"
    #                 elif rarity == "epic":
    #                     cosmetics_type_all_info += f"\u001b[2;35m{rarity.title()}\u001b[0m"
    #                 elif rarity == "legendary":
    #                     cosmetics_type_all_info += f"\u001b[2;33m{rarity.title()}\u001b[0m"
    #             except KeyError: # Default
    #                 cosmetics_type_all_info += "Common"
    #         except:
    #             cosmetics_type_all_info = "N.A."
    #         cosmetics_dict[cosmetics_type] = cosmetics_type_all_info
              
                
    #     # Add general player info
    #     general_info = "```ansi\n"
    #     general_info += f"{'Username: ':>15}{username}\n"
    #     dt_create_time = datetime.datetime.strptime(create_time.translate(':-'), '%Y-%m-%dT%H:%M:%SZ')
    #     general_info += f"{'Create Time: ':>15}{dt_create_time} UTC ({timeago.format(dt_create_time, datetime.datetime.now())})\n"
    #     general_info += f"{'Level: ':>15}{level}\n"
    #     general_info += f"{'Current Body: ':>15}{cosmetics_dict['body']}\n"
    #     general_info += f"{'Current Hat: ':>15}{cosmetics_dict['hat']}\n"
    #     general_info += f"{'Current Suit: ':>15}{cosmetics_dict['suit']}\n"
    #     general_info += f"{'Current Hand: ':>15}{cosmetics_dict['hand']}\n"
    #     general_info += f"{'Current Color: ':>15}{cosmetics_dict['color']}\n"
    #     general_info += f"{'User ID: ':>15}{user_id}\n"
    #     general_info += f"{'Online: ':>15}" + "\u001b[2;" + ("32" if is_online else "31") + f"m{is_online}\u001b[0m\n"
    #     general_info += "```"

    #     # Add to embed
    #     message = ""
    #     message += f"📓 ***General Info***:\n{general_info}\n"
    #     # message1 = ""
    #     # message1 += f"📓 ***General Info***:\n{general_info}\n"

    #     # # Send
    #     # await interaction.followup.send(
    #     #     embed=discord.Embed(title="Goober Dash <:goober:1146508948325814402>\nDetailed Player Info:", description=message1, color=0x55D3FD)
    #     # )

    #     # if section in {"with 📊 Seasons Records", "All"}:
    #     # Create seasons records list
    #     seasons_records_list = "```ansi\n"

    #     crowns = f"{'Season:':<8}{'Days:':<9}{'Local:':<9}{'Global:':<9}{'Crowns:':<8}{'Games:':<7}{'C/G:'}\n{'─'*56}\n"
    #     crowns_record = False

    #     for season in range(1, goober_dash_current_season + 1):  # From first season to current season
    #         response_global = await goober_dash_client.query_leaderboard(
    #             season,
    #             "global",
    #             1,
    #             "",
    #             user_id,
    #         )
    #         try:  
    #             records_global = response_global["owner_records"]
    #         except KeyError:
    #             continue

    #         country_code = json.loads(records_global[0]['metadata'])['country']
    #         response_local = await goober_dash_client.query_leaderboard(
    #             season,
    #             f"country.{country_code.upper()}",
    #             1,
    #             "",
    #             user_id,
    #         )
    #         try:
    #             records_local = response_local["owner_records"]
    #         except KeyError:
    #             continue
            
    #         rank = int(records_global[0]["rank"])
            
    #         rank_emoji = "  "
    #         if season != goober_dash_current_season:
    #             if rank == 1:
    #                 rank_emoji = "🥇"
    #             elif rank == 2:
    #                 rank_emoji = "🥈"
    #             elif rank == 3:
    #                 rank_emoji = "🥉"

    #         required_season_info = goober_dash_season_info(season, "short")
            
    #         crowns_record = True
    #         crowns += (f"{'CURRENT SEASON'.center(56, '-')}\n" if season == goober_dash_current_season else "")
    #         crowns += f"{season:^8}" # Season
    #         crowns += f"{required_season_info[2].split(' ', 1)[0]:<6}" # Days
    #         crowns += flag.flagize(f":{country_code}: ") # Country Flag
    #         crowns += f"{rank_emoji:<1}{'{:,}'.format(int(records_local[0]['rank'])):<7}" # Local Rank
    #         crowns += f"{rank_emoji:<1}{'{:,}'.format(int(records_global[0]['rank'])):<7}" # Global Rank
    #         crowns += f"{'👑 ' + '{:,}'.format(int(records_global[0]['score'])):<7}" # Crowns
    #         crowns += f"{records_global[0]['num_score']:<7}" # Games
    #         crowns += f"{int(records_global[0]['score'])/int(records_global[0]['num_score']):.2f}\n" # Crowns / Games
              

    #     if crowns_record == False:
    #         seasons_records_list += "No records found"
    #     else:
    #         seasons_records_list += crowns
    #         country_name = pycountry.countries.get(alpha_2=f"{country_code.upper()}").name
    #         seasons_records_list += f"† Country/Region: {country_name} ({country_code})\n"
    #     seasons_records_list += "```"

    #     # Add to embed
    #     message += f"📊 ***Seasons Records***:\n{seasons_records_list}\n"
    #     # message2 = ""
    #     # message2 += f"📊 ***Seasons Records***:\n{seasons_records_list}\n"

    #     # # Send
    #     # await interaction.followup.send(
    #     #     embed=discord.Embed(description=message2, color=0x55D3FD)
    #     # )
            
    #     # if section in {"with 🎖️ Medals", "All"}:
    #     # Create medal list
    #     medal_list = "```\n"

    #     l1 = [] # medals_priority
    #     l2 = [] # medals_names
    #     l3 = [] # medals_count
        
    #     for medal in user_data["awards"]:
    #         l1.append(awards_config.get(medal)['priority'])
    #         l2.append(awards_config.get(medal)['name'])
    #         l3.append(user_data["awards"][medal]['count'])

    #     if len(l1) != 0:
    #         l1, l2, l3 = map(list, zip(*sorted(zip(l1, l2, l3)))) # Sort l2 and l3 according to l1
            
    #         for i in range(len(l1)):
    #             medal_list += f"{l2[i]:<20} x{l3[i]}\n"
    #     else:
    #         medal_list += "No medals found\n"
    #     medal_list += "```"
            
    #     # Add to embed
    #     message += f"🎖️ ***Medals***:\n{medal_list}\n"
    #     # message3 = ""
    #     # message3 += f"🎖️ ***Medals***:\n{medal_list}\n"

    #     # # Send
    #     # await interaction.followup.send(
    #     #     embed=discord.Embed(description=message3, color=0x55D3FD)
    #     # )

    #     # if section in {"with 🗒️ Stats", "All"}:
    #     # Create stats
    #     stats_list = "```ansi\n"
    #     stats = user_data["stats"]

    #     try:
    #         games_played = stats["GamesPlayed"]
    #     except KeyError:
    #         games_played = 0
    #     try:
    #         games_won = stats["GamesWon"]
    #     except KeyError:
    #         games_won = 0
    #     try:
    #         deaths = stats["Deaths"]
    #     except KeyError:
    #         deaths = 0
    #     try:
    #         deaths_per_games_played = f"{stats['Deaths']/stats['GamesPlayed']:.2f}"
    #     except KeyError:
    #         deaths_per_games_played = 0
    #     try:
    #         longest_winstreak = stats["Winstreak"]
    #     except KeyError:
    #         longest_winstreak = 0
    #     try:
    #         current_winstreak = stats["CurrentWinstreak"]
    #     except KeyError:
    #         current_winstreak = 0
    #     try:
    #         winrate = f"{games_won/games_played*100:.2f}"
    #     except:
    #         winrate = 0

    #     stats_dict = {
    #       "Games Played": games_played,
    #       "Winrate": f"{winrate}% - \u001b[2;32m{games_won}W\u001b[0m \u001b[2;31m{games_played-games_won}L\u001b[0m",
    #       "Deaths": deaths,
    #       "Deaths/Games Played": deaths_per_games_played,
    #       "Longest Winstreak": longest_winstreak,
    #       "Current Winstreak": current_winstreak,
    #     }
        
    #     for key in stats_dict:
    #         stats_list += f"{key:>19}: {stats_dict[key]}\n"
    #     stats_list += "```"
        
    #     # Add to embed
    #     message += f"🗒️ ***Stats***:\n{stats_list}\n"
    #     # message4 = ""
    #     # message4 += f"🗒️ ***Stats***:\n{stats_list}\n"

    #     # # Send
    #     # await interaction.followup.send(
    #     #     embed=discord.Embed(description=message4, color=0x55D3FD)
    #     # )
        
    #     # Send
    #     await interaction.followup.send(
    #         embed=discord.Embed(title="Goober Dash <:goober:1146508948325814402>\nDetailed Player Info:", description=message, color=0x55D3FD))

    
    @tree.command()
    @app_commands.describe(
        level_id="Level ID of the level / map",
    )
    async def level_info(
        self,
        interaction: discord.Interaction,
        level_id: str,
    ):
        """🔵 Return info about a specified Goober Dash level"""

        await interaction.response.defer(ephemeral=False, thinking=True)

        try:
            # Get map data
            response = await goober_dash_client.level_info(level_id)
        except aiohttp.ClientResponseError:
            # The code is wrong, send an error response
            await interaction.followup.send(
                embed=discord.Embed(color=0xFF0000,
                                    title="❌ Level not found ❌")
            )
            return
        
        map_data = json.loads(response["payload"])
        
        # Format the level info
        # Send
        embed=discord.Embed(
            title=f"{map_data['level_name']}",
            color=0x55D3FD,
            url=f"https://gooberdash.winterpixel.io/?play={level_id}"
        )
        embed.add_field(name="Game Mode", value=f"{map_data['game_mode']}")
        embed.add_field(name="Player Count", value=f"{map_data['player_count']}")
        embed.add_field(name="Level Theme", value=f"{map_data['level_theme'].title()}")
        embed.add_field(name="Rating", value=f"{map_data['rating']:.2f}/5")
        embed.add_field(name="Author Name", value=f"{map_data['author_name']}")
        embed.add_field(name="Author ID", value=f"{map_data['author_id']}")
        dt_create_time = f"{datetime.datetime.fromtimestamp(map_data['create_time']):%Y-%m-%d %H:%M:%S}"
        embed.add_field(name="Create Time", value=f"{dt_create_time} UTC ({timeago.format(dt_create_time, datetime.datetime.now())})")
        dt_update_time = f"{datetime.datetime.fromtimestamp(map_data['update_time']):%Y-%m-%d %H:%M:%S}"
        embed.add_field(name="Update Time", value=f"{dt_update_time} UTC ({timeago.format(dt_update_time, datetime.datetime.now())})")
        embed.add_field(name="Level ID", value=f"{level_id}")
        embed.set_author(name="Detailed Level Info", icon_url="https://i.imgur.com/ygqFGL6.png")
        embed.set_thumbnail(url="https://i.imgur.com/IVL3Jwg.png")
        await interaction.followup.send(embed=embed)
    
    
    @tree.command()
    async def get_config(self, interaction: discord.Interaction):
        """🔵 Get the most updated GooberDash server config"""

        await refresh_config()

        file = io.StringIO(json.dumps(goober_dash_server_config))
        await interaction.response.send_message(
            file=discord.File(fp=file, filename="goober_dash_server_config.json")
        )
