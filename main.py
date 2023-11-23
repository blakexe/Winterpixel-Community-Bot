import discord
import json
import asyncio
import typing
import os
import datetime
import random
import time
import re
import numpy as np
import flag
import pycountry
import aiohttp
from timeit import default_timer as timer
from math import ceil
from operator import itemgetter
from replit import db
from discord import app_commands
from misc.random_tank_get import get_a_random_tank
from clients.gooberdash_client import GooberDashClient
from clients.moonrockminers_client import MoonrockMinersClient
from clients.rocketbotroyale_client import RocketBotRoyaleClient
from non_reaction_commands.gooberdash_non_reaction_commands import GooberDash # GD_NRC
from non_reaction_commands.moonrockminers_non_reaction_commands import MoonrockMiners # MM_NRC
from non_reaction_commands.rocketbotroyale_non_reaction_commands import RocketBotRoyale # RBR_NRC
from non_reaction_commands.server_non_reaction_commands import ServerMisc # Server_NRC

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
    rbr_mm_email_password = os.environ["rbr_mm_email_password"]
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
rocket_bot_royale_server_config = {}
goober_dash_server_config = {}

# Initialize rocketbot client
moonrock_miners_client = MoonrockMinersClient(rbr_mm_email_password, rbr_mm_email_password)
rocket_bot_royale_client = RocketBotRoyaleClient(rbr_mm_email_password, rbr_mm_email_password)
goober_dash_client = GooberDashClient(gd_email, gd_password)

os.system("clear")


###################### GOOBER-DASH REACTION COMMANDS START ######################
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
        season_days = f"{'{:.2f}'.format(s) if type(s) == float else s} days"

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


class goober_dash(app_commands.Group): # GD_RC
  """Goober Dash reaction commands"""

  def __init__(self, bot: discord.client):
      super().__init__()


  async def refresh_config():
    """Refresh Goober Dash game configuration every 10 minutes"""

    global goober_dash_server_config

    while True:
        response = await goober_dash_client.get_config()
        goober_dash_server_config = response

        # Remove past season keys
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

        for global_leaderboard in db.prefix("global"):
            if str(goober_dash_current_season) not in global_leaderboard:
                del db[global_leaderboard]
        for local_leaderboard in db.prefix("country"):
            if str(goober_dash_current_season) not in local_leaderboard:
                del db[local_leaderboard]

        await asyncio.sleep(600)


  async def public_levels_ratings_update():
    """Refresh Goober Dash public levels ratings every day"""

    global goober_dash_server_config

    while True:
        # Get a list of level_ids
        response = await goober_dash_client.official_levels()

        levels_info = json.loads(response)
        level_ids = [levels_info[level]["uuid"] for level in levels_info]

        # Get the rating of each level
        for level_id in level_ids:
            response2 = await goober_dash_client.level_info(level_id)
            map_data = json.loads(response2["payload"])
            if "goober_dash_public_levels_ratings_2" not in db.keys():
                db["goober_dash_public_levels_ratings_2"] = dict()
            try:
                player_count = 8 if map_data["player_count"] == 9 else map_data["player_count"]
                type = map_data["game_mode"] + str(player_count)
                rating = f"{map_data['rating']:.4f}"
                if type not in db["goober_dash_public_levels_ratings_2"]:
                    db["goober_dash_public_levels_ratings_2"][type] = dict()
                db["goober_dash_public_levels_ratings_2"][type][level_id] = rating
            except:
                if type not in db["goober_dash_public_levels_ratings_2"]:
                    db["goober_dash_public_levels_ratings_2"][type] = dict()
                db["goober_dash_public_levels_ratings_2"][type][level_id] = "N.A."
            time.sleep(2)

        await asyncio.sleep(86400)


  @app_commands.command()
  @app_commands.describe(
      type="Global Leaderboard / Country or Region Leaderboard",
      changes="Only available for Top 50 records of current season, changes since last command used",
      country_code="Alpha-2 Country Code (e.g. US = United States)(Local Leaderboard only), default US",
      season="Season 1 or later, default current season",
  )
  async def leaderboard(
      self,
      interaction: discord.Interaction,
      type: typing.Literal["🌎 Global", "🏳️ Local"],
      changes: typing.Literal["Shown", "Hidden"],
      country_code: str = "US",
      season: int = -1,
  ):
      """🔵 Return the specified season leaderboard of Goober Dash, default current season"""

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
      if season < 1 or season > goober_dash_current_season:
          season = goober_dash_current_season

      # Season Info
      required_season_info = goober_dash_season_info(season, "long")
      global all_required_season_info
      all_required_season_info = (
          f"📓 ***Season Info***:\n```ansi\n{'Start: ':>10}{required_season_info[0]}\n{'End: ':>10}{required_season_info[1]}\n{'Duration: ':>10}{required_season_info[2]}\n{'Status: ':>10}{required_season_info[3]}\n"
          + (
              f"{'Ends in: ':>10}{required_season_info[4]}\n"
              if season == goober_dash_current_season
              else ""
          )
          + "```"
      )

      # Hide changes for past seasons
      if season < goober_dash_current_season:
          changes = "Hidden"

      # Get leaderboard info
      invalid_country_code = False
      if type == "🌎 Global":
          leaderboard_id = "global"
          embed_title_bracket = type
      elif type == "🏳️ Local":
          try:
              leaderboard_id = f"country.{country_code.upper()}"
              country_flag = flag.flagize(f":{country_code.upper()}:")
              country_name = pycountry.countries.get(alpha_2=f"{country_code.upper()}").name
              embed_title_bracket = f"{country_flag} {country_code.upper()} - {country_name}"
          except AttributeError:
              invalid_country_code = True
      if invalid_country_code == False:
          embed_title = f"Goober Dash <:goober:1146508948325814402>\nSeason {season} Leaderboard ({embed_title_bracket}):"

      if changes == "Shown":
          limit = 100
      elif changes == "Hidden":
          limit = 25

      no_records = False
      try:
          response = await goober_dash_client.query_leaderboard(season, leaderboard_id, limit)
          records = response["records"]
      except aiohttp.ClientResponseError:
          no_records = True

      if invalid_country_code == False:
          if no_records == False:
              start = records[0]["rank"]
              end = records[len(records) - 1]["rank"]
              cursor_dict = dict()
              cursor_dict[1] = ""

              try:
                  cursor_dict[2] = response["next_cursor"]
                  next_cursor = True
              except:
                  next_cursor = False

              if changes == "Shown":
                  # Add to replit's database for new keys
                  new_key_flag = False
                  if f"{leaderboard_id}.{season}" not in db.keys():
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
                  label = f"{all_required_season_info}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<9}{'Name:':<21}{'Crowns:'}\u001b[0m\n{'—' * 50}\n"

                  # Using f-string spacing to pretty print the leaderboard
                  if len(records) < 50:  # Prevent index out of range error
                      records_range = len(records)
                  else:
                      records_range = 50

                  for i in range(records_range):
                      # Rank difference
                      try:
                          rank_diff = (
                              int(records[i]["rank"])
                              - int(db[records[i]["leaderboard_id"]
                                   ][records[i]["owner_id"]]["rank"])
                          )
                          if rank_diff < 0:
                              rank_diff_2 = f"\u001b[2;32m▲{abs(rank_diff):<3}\u001b[0m"
                          elif rank_diff > 0:
                              rank_diff_2 = f"\u001b[2;31m▼{abs(rank_diff):<3}\u001b[0m"
                          else:
                              rank_diff_2 = f"{'-':^4}"
                      except KeyError:
                          rank_diff_2 = f"{'':<4}"  # Not found ind repl.it's database

                      # Rank (bold)
                      message += (
                          f"{rank_diff_2}\u001b[1m{'#' + str(records[i]['rank']):<5}\u001b[0m "
                      )

                      # Country
                      message += flag.flagize(f":{json.loads(records[i]['metadata'])['country']}: ")

                      # Name
                      if "\n" in records[i]['username']:
                          response = goober_dash_client.non_async_user_info_2(records[i]['owner_id'])
                          user_info_2 = response["users"][0]
                          username = user_info_2["username"]
                      else:
                          username = records[i]['username']
                      message += f"{username:<21}"

                      # Crowns difference
                      try:
                          crowns_diff = (
                              int(records[i]["score"])
                              - int(db[records[i]["leaderboard_id"]
                                   ][records[i]["owner_id"]]["score"])
                          )
                          if crowns_diff < 0:
                              crowns_diff_2 = f"\u001b[2;31m-{abs(crowns_diff):<4}\u001b[0m"
                          elif crowns_diff > 0:
                              crowns_diff_2 = f"\u001b[2;32m+{abs(crowns_diff):<4}\u001b[0m"
                          else:
                              crowns_diff_2 = f"{'-':^5}"
                      except:
                          crowns_diff_2 = f"{'':<5}"

                      # Crowns
                      message += (
                          f"{'👑 ' + '{:<6,.0f}'.format(int(records[i]['score']))} {crowns_diff_2}\n"
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
                          title=embed_title,
                          description=label + message1 + "```",
                          color=0x55D3FD,
                      )
                      embed_init.set_footer(
                          text=f"Page 1/2:  1 to 25 | Changes since {db[f'{leaderboard_id}.{season}']['last_update_time']}"
                      )
                      msg = await interaction.followup.send(embed=embed_init)
                      msg2 = await interaction.followup.send(
                          embed=discord.Embed(description="To be edited...", color=0x55D3FD)
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
                                      title=embed_title,
                                      description="\n" + label + message2,
                                      color=0x55D3FD
                                  )
                                  embed_first.set_footer(
                                      text=f"Page 2/2: 26 to 50 | Changes since {db[f'{leaderboard_id}.{season}']['last_update_time']}"
                                  )
                                  await msg.edit(embed=embed_first)
                                  await msg.remove_reaction(reaction, user)

                              elif str(reaction.emoji) == "◀️" and cur_page == 2:  # Go to Page 1
                                  cur_page -= 1
                                  embed_second = discord.Embed(
                                      title=embed_title,
                                      description="\n" + label + message1 + "```",
                                      color=0x55D3FD
                                  )
                                  embed_second.set_footer(
                                      text=f"Page 1/2:  1 to 25 | Changes since {db[f'{leaderboard_id}.{season}']['last_update_time']}"
                                  )
                                  await msg.edit(embed=embed_second)
                                  await msg.remove_reaction(reaction, user)

                              elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                                  await msg.edit(
                                      embed=discord.Embed(
                                          title=embed_title,
                                          description=label + message1 + "```",
                                          color=0x55D3FD
                                      )
                                  )
                                  embed_second_timeout = discord.Embed(
                                      description="```ansi\n" + message2,
                                      color=0x55D3FD
                                  )
                                  embed_second_timeout.set_footer(
                                      text=f"Changes since {db[f'{leaderboard_id}.{season}']['last_update_time']}"
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
                                      title=embed_title,
                                      description=label + message1 + "```",
                                      color=0x55D3FD
                                  )
                              )
                              embed_second_timeout = discord.Embed(
                                  description="```ansi\n" + message2,
                                  color=0x55D3FD
                              )
                              embed_second_timeout.set_footer(
                                  text=f"Changes since {db[f'{leaderboard_id}.{season}']['last_update_time']}"
                              )
                              await msg2.edit(embed=embed_second_timeout)
                              await msg.clear_reactions()
                              break
                              # Ending the loop if user doesn't react after 15 seconds
                  elif cannot_split == True:  # Send in 1 message if there are too little records
                      embed=discord.Embed(
                          title=embed_title,
                          description=label + message + "```",
                          color=0x55D3FD,
                      )
                      embed.set_footer(text=f"Changes since {db[f'{leaderboard_id}.{season}']['last_update_time']}")
                      await interaction.followup.send(embed=embed)

                  # Update to replit's database for old keys
                  if (f"{leaderboard_id}.{season}" in db.keys()) and (new_key_flag == False):
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
                      message = f"{all_required_season_info}\n📊 ***Leaderboard***:```ansi\n\u001b[1m{'Rank:':<9}{'Name:':<21}{'Crowns:':<8}{'Rounds:':<8}{'C/R:'}\u001b[0m\n{'─' * 52}\n"

                      # Using f-string spacing to pretty print the leaderboard
                      for record in records:
                          # Rank (bold)
                          message += f"\u001b[1m{'#' + str(record['rank']):<5}\u001b[0m "

                          # Country
                          message += flag.flagize(f":{json.loads(record['metadata'])['country']}: ")

                          # Name
                          if "\n" in record['username']:
                              response = goober_dash_client.non_async_user_info_2(record['owner_id'])
                              user_info_2 = response["users"][0]
                              username = user_info_2["username"]
                          else:
                              username = record['username']
                          message += f"{username:<21}"

                          # Crowns
                          message += f"{'👑 ' + '{:,}'.format(int(record['score'])):<8}"

                          # Rounds
                          message += f"{record['num_score']:<7}"

                          # C/R
                          message += f"{int(record['score'])/int(record['num_score']):.2f}\n"
                      message += "```"
                      return message

                  # Send
                  cur_page = 1
                  embed_init = discord.Embed(
                      title=embed_title,
                      description=hidden(),
                      color=0x55D3FD
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
                              response = await goober_dash_client.query_leaderboard(
                                  season, leaderboard_id, limit, cursor_dict[cur_page]
                              )
                              records = response["records"]
                              start = records[0]["rank"]
                              end = records[len(records) - 1]["rank"]
                              try:
                                  cursor_dict[cur_page + 1] = response["next_cursor"]
                              except:
                                  next_cursor = False  # Does not exist
                              embed_next = discord.Embed(
                                  title=embed_title,
                                  description=hidden(),
                                  color=0x55D3FD
                              )
                              embed_next.set_footer(
                                  text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                              )
                              await msg.edit(embed=embed_next)
                              await msg.remove_reaction(reaction, user)

                          elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                              cur_page -= 1
                              response = await goober_dash_client.query_leaderboard(
                                  season, leaderboard_id, limit, cursor_dict[cur_page]
                              )
                              records = response["records"]
                              start = records[0]["rank"]
                              end = records[len(records) - 1]["rank"]
                              embed_prev = discord.Embed(
                                  title=embed_title,
                                  description=hidden(),
                                  color=0x55D3FD
                              )
                              embed_prev.set_footer(
                                  text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                              )
                              await msg.edit(embed=embed_prev)
                              await msg.remove_reaction(reaction, user)

                          elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                              cur_page = 1
                              next_cursor = True
                              response = await goober_dash_client.query_leaderboard(
                                  season, leaderboard_id, limit, cursor_dict[cur_page]
                              )
                              records = response["records"]
                              start = records[0]["rank"]
                              end = records[len(records) - 1]["rank"]
                              embed_first = discord.Embed(
                                  title=embed_title,
                                  description=hidden(),
                                  color=0x55D3FD
                              )
                              embed_first.set_footer(
                                  text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                              )
                              await msg.edit(embed=embed_first)
                              await msg.remove_reaction(reaction, user)

                          elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                              response = await goober_dash_client.query_leaderboard(
                                  season, leaderboard_id, 50
                              )
                              records = response["records"]
                              embed=discord.Embed(
                                  title=embed_title,
                                  description=hidden(),
                                  color=0x55D3FD
                              )
                              await msg.edit(embed=embed)
                              await msg.clear_reactions()
                              break

                          else:
                              await msg.remove_reaction(reaction, user)
                              # Removes reactions if invalid
                      except asyncio.TimeoutError:
                          response = await goober_dash_client.query_leaderboard(
                              season, leaderboard_id, 50
                          )
                          records = response["records"]
                          embed_2=discord.Embed(
                              title=embed_title,
                              description=hidden(),
                              color=0x55D3FD
                          )
                          await msg.edit(embed=embed_2)
                          await msg.clear_reactions()
                          break
                          # Ending the loop if user doesn't react after 15 seconds
          else:
              embed_init = discord.Embed(
                  title=embed_title,
                  description="```No records found```",
                  color=0x55D3FD
              )
              await interaction.followup.send(embed=embed_init)
      else:
          await interaction.followup.send(embed=discord.Embed(color=0xFF0000,title="❌ Invalid Country Code ❌"))


  @app_commands.command()
  @app_commands.describe(
      levels="View particular group of levels only or All levels",
      sorted_by="Sort the list of Goober Dash official levels by desired values (Rating updates daily)",
      order="Sorted by Ascending or Descending order"
  )
  async def official_levels(
      self,
      interaction: discord.Interaction,
      levels: typing.Literal["Lobby Levels only", "32-player Levels only", "16-player Levels only", "8-player Levels only", "Knockout Levels only", "All Levels"],
      sorted_by: typing.Literal["Name", "Game Mode (Mode)", "Player Count (#)",
      "Theme", "Rating (👍%)", "Update Time (Update)"],
      order: typing.Literal["🔺 Ascending", "🔻 Descending"],
  ):
      """🔵 Return the a list of offical levels of Goober Dash, sorted by various values"""

      await interaction.response.defer(ephemeral=False, thinking=True)

      def check(reaction, user):
          return user == interaction.user and str(reaction.emoji) in [
              "◀️",
              "▶️",
              "⏪",
              "⏹️",
          ]
          # This makes sure nobody except the command sender can interact with the "menu"

      response = await goober_dash_client.official_levels()

      sorted_by_list = ["Name", "Game Mode (Mode)", "Player Count (#)", "Theme", "Rating (👍%)", "Update Time (Update)"]
      levels_info = json.loads(response)
      level_ids, names, game_modes, player_counts, themes, ratings, update_times = ([] for i in range(7))
      for level in levels_info:
          game_mode = levels_info[level]["game_mode"]
          player_count = levels_info[level]["player_count"]
          player_count = 8 if player_count == 9 else player_count
          type = game_mode + str(player_count)
          levels_type = {
              "Lobby Levels only": "Lobby32",
              "32-player Levels only": "Race32",
              "16-player Levels only": "Race16",
              "8-player Levels only": "Race8",
              "Knockout Levels only": "Knockout4"
          }
          if levels != "All Levels" and levels_type[levels] != type:
              continue
          else:
              level_ids.append(levels_info[level]["uuid"])
              names.append(levels_info[level]["level_name"])
              game_modes.append(game_mode)
              player_counts.append(player_count)
              themes.append(levels_info[level]["level_theme"].title())
              try:
                  ratings.append(round((float(db["goober_dash_public_levels_ratings_2"][type][levels_info[level]["uuid"]])-1)*25))
              except:
                  ratings.append("-1")
              update_times.append(levels_info[level]["update_time"])
    
      a = np.stack((level_ids, names, game_modes, player_counts, themes, ratings, update_times), axis=1)  # 2d-array which stores all levels_info
      b = a.astype('object')
      b[:, 3] = b[:, 3].astype('int')  # fix player_counts data type issue
      b[:, 5] = b[:, 5].astype('int')  # fix level_rating data type issue
      column_index = sorted_by_list.index(sorted_by) + 1
      if levels == "Lobby Levels only": # filter levels
          b = b[np.in1d(b[:, 2], np.asarray(['Lobby']))]
      elif levels == "32-player Levels only":
          b = b[np.in1d(b[:, 2], np.asarray(['Race']))]
          b = b[np.in1d(b[:, 3], np.asarray([32]))]
      elif levels == "16-player Levels only":
          b = b[np.in1d(b[:, 3], np.asarray([16]))]
      elif levels == "8-player Levels only":
          b = b[np.in1d(b[:, 3], np.asarray([8]))]
      elif levels == "Knockout Levels only":
          b = b[np.in1d(b[:, 2], np.asarray(['Knockout']))]
      c = b[b[:, column_index].argsort(), :]  # sort by columns
      c = c[::-1] if order == "🔻 Descending" else c  # reverse order (if necessary)
      
      message = ""
      length = len(c)
      for i in c: # i = level
          message += f"{i[1]:<18}{i[2]:<9}{i[3]:<3}{i[4]:<8}"
          if i[5] != -1:
              if i[5] >= 0 and i[5] < 33: # Red
                  color_code = 31
              elif i[5] >= 33 and i[5] < 67: # Yellow
                  color_code = 33
              elif i[5] >= 67 and i[5] <= 100: # Green
                  color_code = 32
              message += f"\u001b[2;{color_code}m" + f"{i[5]:<5}" + "\u001b[0m"
          else:
              message += f"{'N.A.':<5}"
          message += f"{datetime.datetime.utcfromtimestamp(int(i[6])).strftime('%Y-%m-%d')}\n"
      
      # Split the message every 25 lines to a list
      message_list_25 = re.findall('((?:[^\n]+\n?){1,25})', message)
      message_list_25 = [message] if len(message_list_25) == 0 else message_list_25
      
      # Split the message every 50 lines to a list
      message_list_50 = re.findall('((?:[^\n]+\n?){1,50})', message)
      message_list_50 = [message] if len(message_list_50) == 0 else message_list_50
      
      # Title for embed
      if sorted_by == "Game Mode (Mode)":
          sorted_by_rennamed = "Game Mode"
      elif sorted_by == "Player Count (#)":
          sorted_by_rennamed = "Player Count"
      elif sorted_by == "Rating (👍%)":
          sorted_by_rennamed = "Rating"
      elif sorted_by == "Update Time (Update)":
          sorted_by_rennamed = "Update Time"
      else:
          sorted_by_rennamed = sorted_by
      embed_title = f"Goober Dash <:goober:1146508948325814402>\nOfficial Levels ({levels})\n(Sorted by {sorted_by_rennamed} - {order} order):"

      # Label for embed
      # General Info Section
      type_counts = dict()
      for key in db["goober_dash_public_levels_ratings_2"]:
          type_counts[key] = len(db["goober_dash_public_levels_ratings_2"][key])
      
      label = f"📓 ***General Info***:```ansi\n\u001b[1m{'Mode':^16}{'Players':^14}{'Number of Levels':^23}\u001b[0m\n{'—' * 53}\n"
      label += f"{'Lobby':^16}{'32':^14}{type_counts['Lobby32']:^23}\n"
      label += f"{'Race':^16}{'32':^14}{type_counts['Race32']:^23}\n"
      label += f"{'Race':^16}{'16':^14}{type_counts['Race16']:^23}\n"
      label += f"{'Race':^16}{'8':^14}{type_counts['Race8']:^23}\n"
      label += f"{'Knockout':^16}{'4':^14}{type_counts['Knockout4']:^23}\n"
      label += f" Total {sum(type_counts.values())} Levels ".center(53, '*')
      label += "\n```\n"

      # Levels Info Section
      label += f"🗒️ ***Levels Info***:```ansi\n\u001b[1m{'Name ':<18}{'Mode ':<9}{'# ':<3}{'Theme ':<8}{'👍% ':<4}{'Update '}\u001b[0m\n{'—' * 53}\n"
      if sorted_by == "Game Mode (Mode)":
          target = "Mode"
      elif sorted_by == "Player Count (#)":
          target = "#"
      elif sorted_by == "Rating (👍%)":
          target = "👍%"
      elif sorted_by == "Update Time (Update)":
          target = "Update"
      else:
          target = sorted_by
      index = label.index(target) + len(target)
      arrow = '\u001b[2;31m' + ('▼' if order == "🔻 Descending" else "▲") + '\u001b[0m'
      label = label[:index] + arrow + label[index + 1:]
      
      def hidden(i):
          # the labels and the genral info section
          message = label
          
          # the official map info list
          message += message_list_25[i]
          message += "```"

          return message

      # Send
      cur_page = 1
      embed_init = discord.Embed(
          title=embed_title,
          description=hidden(cur_page - 1),
          color=0x55D3FD
        )
      embed_init.set_footer(text=f"Page {cur_page:<2}: 1 to {length if cur_page*25 > length else cur_page*25}")
      msg = await interaction.followup.send(embed=embed_init)

      for reaction_emoji in ["◀️", "▶️", "⏪", "⏹️"]:
          await msg.add_reaction(reaction_emoji)

      global next_cursor
      next_cursor = True

      while True:
          try:
              reaction, user = await client.wait_for(
                  "reaction_add", timeout=15, check=check
              )
              # Waiting for a reaction to be added - times out after 15 seconds

              if str(reaction.emoji) == "▶️" and next_cursor != False:  # Next page
                  cur_page += 1
                  try:
                      description = hidden(cur_page - 1)
                  except IndexError:
                      cur_page -= 1
                      next_cursor = False
                  if next_cursor == True:
                      embed_next = discord.Embed(
                          title=embed_title,
                          description=description,
                          color=0x55D3FD
                      )
                      embed_next.set_footer(text=f"Page {cur_page:<2}: {(cur_page-1)*25+1} to {length if cur_page*25 > length else cur_page*25}")
                      await msg.edit(embed=embed_next)
                  await msg.remove_reaction(reaction, user)

              elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                  cur_page -= 1
                  embed_prev = discord.Embed(
                      title=embed_title,
                      description=hidden(cur_page - 1),
                      color=0x55D3FD
                  )
                  embed_prev.set_footer(text=f"Page {cur_page:<2}: {(cur_page-1)*25+1} to {length if cur_page*25 > length else cur_page*25}")
                  await msg.edit(embed=embed_prev)
                  await msg.remove_reaction(reaction, user)

              elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                  cur_page = 1
                  next_cursor = True
                  embed_first = discord.Embed(
                      title=embed_title,
                      description=hidden(cur_page - 1),
                      color=0x55D3FD
                  )
                  embed_first.set_footer(text=f"Page {cur_page:<2}: {(cur_page-1)*25+1} to {length if cur_page*25 > length else cur_page*25}")
                  await msg.edit(embed=embed_first)
                  await msg.remove_reaction(reaction, user)

              elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                  embed=discord.Embed(
                      title=embed_title,
                      description=label+message_list_50[0]+'```',
                      color=0x55D3FD
                  )
                  await msg.edit(embed=embed)
                  await msg.clear_reactions()
                  break
              else:
                  await msg.remove_reaction(reaction, user)
                  # Removes reactions if invalid
          except asyncio.TimeoutError:
              embed=discord.Embed(
                  title=embed_title,
                  description=label+message_list_50[0]+'```',
                  color=0x55D3FD
              )
              await msg.edit(embed=embed)
              await msg.clear_reactions()
              break
              # Ending the loop if user doesn't react after 15 seconds

      # Send the remaining levels (#51 onwards)
      for i in range(len(message_list_50)):
          try:
              embed=discord.Embed(
                description='```ansi\n' + message_list_50[i+1] + '```',
                color=0x55D3FD
              )
              await interaction.followup.send(embed=embed)
          except IndexError:
              break
####################### GOOBER-DASH REACTION COMMANDS END #######################


#################### MOONROCK-MINERS REACTION COMMANDS START ####################
def moonrock_miners_season_info(season):
    start_of_first_season = moonrock_miners_server_config["start_of_first_season"]
    season_duration = moonrock_miners_server_config["season_duration"]

    season_start_timestamp = start_of_first_season+season_duration*(season-1)
    season_start = f"{datetime.datetime.utcfromtimestamp(season_start_timestamp):%Y-%m-%d %H:%M:%S} UTC"

    season_end_timestamp = start_of_first_season+season_duration*season
    season_end = f"{datetime.datetime.utcfromtimestamp(season_end_timestamp):%Y-%m-%d %H:%M:%S} UTC"

    season_days = f"{season_duration/(60*60*24):.0f} days"

    current_timestamp = time.time()
    if current_timestamp > season_end_timestamp:
        status = "\u001b[2;31mEnded\u001b[0m"
    else:
        status = f"\u001b[2;32mIn progress\u001b[0m ({((current_timestamp - season_start_timestamp)/season_duration)*100:.0f} %)"

    if season == moonrock_miners_current_season:
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

    moonrock_miners_all_season_info = [season_start, season_end,
                       season_days, status, time_remaining]
    return moonrock_miners_all_season_info


class moonrock_miners(app_commands.Group): # MM_RC
    """Moonrock Miners reaction commands"""

    def __init__(self, bot: discord.client):
        super().__init__()


    async def refresh_config():
      """Refresh Moonrock Miners game configuration every 10 minutes"""

      global moonrock_miners_server_config

      while True:
          response = await moonrock_miners_client.get_config()
          moonrock_miners_server_config = json.loads(response["payload"])

          # Remove past season keys
          global moonrock_miners_current_season
          moonrock_miners_current_season = moonrock_miners_server_config["season"]
          for i in db.prefix("trophies"):
              if str(moonrock_miners_current_season) not in i:
                  del db[i]

          await asyncio.sleep(600)

    @app_commands.command()
    @app_commands.describe(
        changes="Only available for Top 50 records of current season, changes since last command used",
        season="Beta Season 14 or later, default current season",
    )
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        changes: typing.Literal["Shown", "Hidden"],
        season: int = -1,
    ):
        """🟢 Return the specified season leaderboard of Moonrock Miners, default current season"""

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
        if season > 0 and season < 14:
            season = 14
        elif season < 0 or season > moonrock_miners_current_season:
            season = moonrock_miners_current_season

        # Season Info
        required_season_info = moonrock_miners_season_info(season)
        global all_required_season_info
        all_required_season_info = (
            f"📓 ***Season Info***:\n```ansi\n{'Start: ':>10}{required_season_info[0]}\n{'End: ':>10}{required_season_info[1]}\n{'Duration: ':>10}{required_season_info[2]}\n{'Status: ':>10}{required_season_info[3]}\n"
            + (
                f"{'Ends in: ':>10}{required_season_info[4]}\n"
                if season == moonrock_miners_current_season
                else ""
            )
            + "```"
        )

        # Hide changes for past seasons
        if season < moonrock_miners_current_season:
            changes = "Hidden"

        # Get leaderboard info
        if changes == "Shown":
            limit = 100
        elif changes == "Hidden":
            limit = 25

        response = await moonrock_miners_client.query_leaderboard(season, "trophies", limit)
        no_records = False
        try:
            records = json.loads(response["payload"])["records"]
        except KeyError:
            no_records = True

        if no_records == False:
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
                label = f"{all_required_season_info}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'—' * 45}\n"

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
                    except KeyError:
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
                        color=0x00FF00
                    )
                    embed_init.set_footer(
                        text=f"Page 1/2:  1 to 25 | Changes since {db[f'trophies_{season}']['last_update_time']}"
                    )
                    msg = await interaction.followup.send(embed=embed_init)
                    msg2 = await interaction.followup.send(
                        embed=discord.Embed(description="To be edited...", color=0x00FF00)
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
                                    color=0x00FF00
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
                                    color=0x00FF00
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
                                        color=0x00FF00
                                    )
                                )
                                embed_second_timeout = discord.Embed(
                                    description="```ansi\n" + message2,
                                    color=0x00FF00
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
                                    color=0x00FF00
                                )
                            )
                            embed_second_timeout = discord.Embed(
                                description="```ansi\n" + message2,
                                color=0x00FF00
                            )
                            embed_second_timeout.set_footer(
                                text=f"Changes since {db[f'trophies_{season}']['last_update_time']}"
                            )
                            await msg2.edit(embed=embed_second_timeout)
                            await msg.clear_reactions()
                            break
                            # Ending the loop if user doesn't react after 15 seconds
                elif cannot_split == True:  # Send in 1 message if there are too little records
                    embed=discord.Embed(
                        title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                        description=label + message + "```",
                        color=0x00FF00,
                    )
                    embed.set_footer(
                        text=f"Changes since {db[f'trophies_{season}']['last_update_time']}"
                    )
                    await interaction.followup.send(embed=embed)

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
                    message = f"{all_required_season_info}\n📊 ***Leaderboard***:```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'─' * 37}\n"

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
                    color=0x00FF00
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
                            response = await moonrock_miners_client.query_leaderboard(
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
                                color=0x00FF00
                            )
                            embed_next.set_footer(
                                text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                            )
                            await msg.edit(embed=embed_next)
                            await msg.remove_reaction(reaction, user)

                        elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                            cur_page -= 1
                            response = await moonrock_miners_client.query_leaderboard(
                                season, "trophies", 25, cursor_dict[cur_page]
                            )
                            records = json.loads(response["payload"])["records"]
                            start = records[0]["rank"]
                            end = records[len(records) - 1]["rank"]
                            embed_prev = discord.Embed(
                                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                                description=hidden(),
                                color=0x00FF00
                            )
                            embed_prev.set_footer(
                                text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                            )
                            await msg.edit(embed=embed_prev)
                            await msg.remove_reaction(reaction, user)

                        elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                            cur_page = 1
                            next_cursor = True
                            response = await moonrock_miners_client.query_leaderboard(
                                season, "trophies", 25, cursor_dict[cur_page]
                            )
                            records = json.loads(response["payload"])["records"]
                            start = records[0]["rank"]
                            end = records[len(records) - 1]["rank"]
                            embed_first = discord.Embed(
                                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                                description=hidden(),
                                color=0x00FF00
                            )
                            embed_first.set_footer(
                                text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                            )
                            await msg.edit(embed=embed_first)
                            await msg.remove_reaction(reaction, user)

                        elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                            response = await moonrock_miners_client.query_leaderboard(
                                season, "trophies", 50
                            )
                            records = json.loads(response["payload"])["records"]
                            embed=discord.Embed(
                                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                                description=hidden(),
                                color=0x00FF00
                            )
                            embed.set_footer(
                              text=f"RIP Moonrock Miners")
                            await msg.edit(embed=embed)
                            await msg.clear_reactions()
                            break

                        else:
                            await msg.remove_reaction(reaction, user)
                            # Removes reactions if invalid
                    except asyncio.TimeoutError:
                        response = await moonrock_miners_client.query_leaderboard(
                            season, "trophies", 50
                        )
                        records = json.loads(response["payload"])["records"]
                        embed_2=discord.Embed(
                            title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                            description=hidden(),
                            color=0x00FF00
                        )
                        embed_2.set_footer(text=f"RIP Moonrock Miners")
                        await msg.edit(embed=embed_2)
                        await msg.clear_reactions()
                        break
                        # Ending the loop if user doesn't react after 15 seconds
        else:
            embed_init = discord.Embed(
                title=f"Moonrock Miners 🛸\nBeta Season {season} Leaderboard:",
                description="```No records found```",
                color=0x00FF00
            )
            embed_init.set_footer(
                text=f"RIP Moonrock Miners")
            await interaction.followup.send(embed=embed_init)
##################### MOONROCK-MINERS REACTION COMMANDS END #####################


#################### ROCKET-BOT-ROYALE REACTION COMMANDS START ##################
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


class rocket_bot_royale(app_commands.Group): # RBR_RC
    """Rocket Bot Royale reaction commands"""

    def __init__(self, bot: discord.client):
        super().__init__()

    async def refresh_config():
      """Refresh Rocket Bot Royale game configuration every 10 minutes"""

      global rocket_bot_royale_server_config

      while True:
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

          # Remove past season keys
          for i in db.prefix("tankkings"):
              if str(rocket_bot_royale_current_season) not in i:
                  del db[i]

          await asyncio.sleep(600)


    @app_commands.command()
    @app_commands.describe(
        mode="Leaderboard by 🏆Trophies/🧊Points/🎉Wins/💀Player Kills/🤖Bot Kills",
        changes="Only available for Top 50 records of current season, changes since last command used",
        season="🏆 Trophies: Season 10 or later / Others: Season 0 or later, default current season",
    )
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        mode: typing.Literal[
            "🏆 Trophies", "🧊 Points", "🎉 Wins", "💀 Player Kills", "🤖 Bot Kills"
        ],
        changes: typing.Literal["Shown", "Hidden"],
        season: int = -1,
    ):
        """🟡 Return the specified season leaderboard of RBR by various modes, default current season"""

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

        rocket_bot_royale_current_season = rocket_bot_royale_server_config["season"]

        # Reassign season if unreasonable
        if mode == "🏆 Trophies":
            if season > 0 and season < 10:
                season = 10
        if season < 0 or season > rocket_bot_royale_current_season:
            season = rocket_bot_royale_current_season

        # Season Info
        required_season_info = rocket_bot_royale_season_info(season)
        global all_required_season_info
        all_required_season_info = (
            f"📓 ***Season Info***:\n```ansi\n{'Start: ':>10}{required_season_info[0]}\n{'End: ':>10}{required_season_info[1]}\n{'Duration: ':>10}{required_season_info[2]}\n{'Status: ':>10}{required_season_info[3]}\n"
            + (
                f"{'Ends in: ':>10}{required_season_info[4]}\n"
                if season == rocket_bot_royale_current_season
                else ""
            )
            + "```"
        )

        # Hide changes for past seasons
        if season < rocket_bot_royale_current_season:
            changes = "Hidden"

        # Get leaderboard info
        if changes == "Shown":
            limit = 100
        elif changes == "Hidden":
            limit = 25

        response = await rocket_bot_royale_client.query_leaderboard(
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
                    split.append(rocket_bot_royale_server_config["trophy_tiers"][i]["maximum_rank"])
                    tier.append(rocket_bot_royale_server_config["trophy_tiers"][i]["name"].upper())
                tier_color_code = ["35", "36", "33", "34", "31"]

                # Using f-string spacing to pretty print the leaderboard labels (bold)
                message = ""
                label = f"{all_required_season_info}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {'Trophies:'}\u001b[0m\n{'—' * 46}\n"

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
                label = f"{all_required_season_info}\n📊 ***Leaderboard***:```ansi\n\u001b[1m    {'Rank:':<5} {'Name:':<20} {mode[2:]}:\u001b[0m\n{'—' * 48}\n"

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
                    # Random string name bug hard code fix                    
                    if len(records[i]['username']) == 10 and records[i]['username'].isalpha():
                        response = rocket_bot_royale_client.non_async_user_info(records[i]['owner_id'])
                        user_data = json.loads(response["payload"])[0]
                        username = user_data["display_name"]
                    else:
                        username = records[i]['username']

                    try:  # For seasons without 'has season pass' key
                        message += (
                            (
                                "\u001b[1;33m"
                                if records[i]["metadata"]["has_season_pass"]
                                else ""
                            )
                            + f"{username:<20}"
                            + (
                                "\u001b[0m "
                                if records[i]["metadata"]["has_season_pass"]
                                else " "
                            )
                        )
                    except:
                        message += f"{username:<20} "  # Name only

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
                    except KeyError:
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
                    title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {'Player Kills' if mode == 'Kills' else mode.replace('_', ' ').title()}):",
                    description=label
                    + message1
                    + (
                        "\n\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n"
                        if mode == "🏆 Trophies"
                        else ""
                    )
                    + "```",
                    color=0xFFFF00
                )
                embed_init.set_footer(
                    text=f"""Page 1/2:  1 to 25 | Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
                )
                msg = await interaction.followup.send(embed=embed_init)
                msg2 = await interaction.followup.send(
                    embed=discord.Embed(description="To be edited...", color=0xFFFF00)
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
                                title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                                description="\n" + label + message2,
                                color=0xFFFF00
                            )
                            embed_first.set_footer(
                                text=f"""Page 2/2: 26 to 50 | Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
                            )
                            await msg.edit(embed=embed_first)
                            await msg.remove_reaction(reaction, user)

                        elif str(reaction.emoji) == "◀️" and cur_page == 2:  # Go to Page 1
                            cur_page -= 1
                            embed_second = discord.Embed(
                                title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                                description="\n"
                                + label
                                + message1
                                + (
                                    "\n\u001b[1;31m———————————————————— RUBY ———————————————————\u001b[0m\n"
                                    if mode == "🏆 Trophies"
                                    else ""
                                )
                                + "```",
                                color=0xFFFF00
                            )
                            embed_second.set_footer(
                                text=f"""Page 1/2:  1 to 25 | Changes since {db[f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}_{season}"]["last_update_time"]}"""
                            )
                            await msg.edit(embed=embed_second)
                            await msg.remove_reaction(reaction, user)

                        elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                            await msg.edit(
                                embed=discord.Embed(
                                    title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                                    description=label + message1 + "```",
                                    color=0xFFFF00
                                )
                            )
                            embed_second_timeout = discord.Embed(
                                description="```ansi\n" + message2,
                                color=0xFFFF00
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
                                title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                                description=label + message1 + "```",
                                color=0xFFFF00
                            )
                        )
                        embed_second_timeout = discord.Embed(
                            description="```ansi\n" + message2,
                            color=0xFFFF00
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
                        title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                        description=label + message + "```",
                        color=0xFFFF00
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
                            rocket_bot_royale_server_config["trophy_tiers"][i]["maximum_rank"])
                        tier.append(
                            rocket_bot_royale_server_config["trophy_tiers"][i]["name"].upper())
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
                    message = f"{all_required_season_info}\n📊 ***Leaderboard***:```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {'Trophies:':<9} {'Games:':<6} {'T/G:'}\u001b[0m\n{'─' * 49}\n"

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
                                f"{all_required_season_info}\n📊 ***Leaderboard***:"
                                if season != 0
                                else ""
                            )
                            + f"```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {mode[2:]+':'}\u001b[0m\n{'─' * 35}\n"
                        )
                    else:  # By Points/Player Kills/Bot Kills
                        message = (
                            (
                                f"{all_required_season_info}\n"
                                if season != 0
                                else ""
                            )
                            + f"📊 ***Leaderboard***:```ansi\n\u001b[1m{'Rank:':<5} {'Name:':<20} {mode[2:]+':':<11} {'Games:':<7} {'P/G:' if mode == '🧊 Points' else 'K/G:'}\u001b[0m\n{'─' * (53 if mode == '💀 Player Kills' else 52)}\n"
                        )

                    # Using f-string spacing to pretty print the leaderboard
                    for record in records:
                        # Rank (bold)
                        message += f"\u001b[1m{'#' + str(record['rank']):<5}\u001b[0m "

                        # Name and color for players with season pass
                        # Random string name bug hard code fix                    
                        if len(record['username']) == 10 and record['username'].isalpha():
                            response = rocket_bot_royale_client.non_async_user_info(record['owner_id'])
                            user_data = json.loads(response["payload"])[0]
                            username = user_data["display_name"]
                        else:
                            username = record['username']

                        try:  # For seasons without 'has season pass' key
                            message += (
                                (
                                    "\u001b[1;33m"
                                    if record["metadata"]["has_season_pass"]
                                    else ""
                                )
                                + f"{username:<20}"
                                + (
                                    "\u001b[0m "
                                    if record["metadata"]["has_season_pass"]
                                    else " "
                                )
                            )
                        except:
                            message += f"{username:<20} "  # Name only

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
                title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                description=(
                    trophies_hidden() if mode == "🏆 Trophies" else non_trophies_hidden()
                ),
                color=0xFFFF00
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
                        response = await rocket_bot_royale_client.query_leaderboard(
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
                            title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description=(
                                trophies_hidden()
                                if mode == "🏆 Trophies"
                                else non_trophies_hidden()
                            ),
                            color=0xFFFF00
                        )
                        embed_next.set_footer(
                            text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                        )
                        await msg.edit(embed=embed_next)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:  # Previous page
                        cur_page -= 1
                        response = await rocket_bot_royale_client.query_leaderboard(
                            season,
                            f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                            25,
                            cursor_dict[cur_page],
                        )
                        records = json.loads(response["payload"])["records"]
                        start = records[0]["rank"]
                        end = records[len(records) - 1]["rank"]
                        embed_prev = discord.Embed(
                            title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description=(
                                trophies_hidden()
                                if mode == "🏆 Trophies"
                                else non_trophies_hidden()
                            ),
                            color=0xFFFF00
                        )
                        embed_prev.set_footer(
                            text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                        )
                        await msg.edit(embed=embed_prev)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "⏪" and cur_page != 1:  # First page
                        cur_page = 1
                        next_cursor = True
                        response = await rocket_bot_royale_client.query_leaderboard(
                            season,
                            f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                            25,
                            cursor_dict[cur_page],
                        )
                        records = json.loads(response["payload"])["records"]
                        start = records[0]["rank"]
                        end = records[len(records) - 1]["rank"]
                        embed_first = discord.Embed(
                            title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description=(
                                trophies_hidden()
                                if mode == "🏆 Trophies"
                                else non_trophies_hidden()
                            ),
                            color=0xFFFF00
                        )
                        embed_first.set_footer(
                            text=f"Page {cur_page:<2}: {start:<4} to {end:<4}"
                        )
                        await msg.edit(embed=embed_first)
                        await msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "⏹️":  # Exit page view and end the loop
                        response = await rocket_bot_royale_client.query_leaderboard(
                            season,
                            f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                            50,
                        )
                        records = json.loads(response["payload"])["records"]
                        await msg.edit(
                            embed=discord.Embed(
                                title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                                description=(
                                    trophies_hidden(False, True)
                                    if mode == "🏆 Trophies"
                                    else non_trophies_hidden()
                                ),
                                color=0xFFFF00
                            )
                        )
                        await msg.clear_reactions()
                        break

                    else:
                        await msg.remove_reaction(reaction, user)
                        # Removes reactions if invalid
                except asyncio.TimeoutError:
                    response = await rocket_bot_royale_client.query_leaderboard(
                        season,
                        f"tankkings_{mode.replace('Player ', '').replace(' ', '_').lower()[2:]}",
                        50,
                    )
                    records = json.loads(response["payload"])["records"]
                    await msg.edit(
                        embed=discord.Embed(
                            title=f"Rocket Bot Royale <:rocket_mint:910253491019202661>\nSeason {season} Leaderboard (by {mode[2:]}):",
                            description=(
                                trophies_hidden(False, True)
                                if mode == "🏆 Trophies"
                                else non_trophies_hidden()
                            ),
                            color=0xFFFF00
                        )
                    )
                    await msg.clear_reactions()
                    break
                    # Ending the loop if user doesn't react after 15 second
##################### ROCKET-BOT-ROYALE REACTION COMMANDS END ###################


####################### SERVER-MISC REACTION COMMANDS START #####################
class server_misc(app_commands.Group): # Server_Misc_RC
    """Server Miscellaneous reaction commands"""

    def __init__(self, bot: discord.client):
        super().__init__()

    @app_commands.command()
    @app_commands.describe(
        changes="Changes since last command used, takes longer to compute"
    )
    async def discord_coins_leaderboard(
        self, interaction: discord.Interaction, changes: typing.Literal["Shown", "Hidden"]
    ):
        """⚪ Return the Discord coins leaderboard"""

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
            color=0xFFFFFF
        )
        embed_first.set_footer(
            text=f"Page {cur_page:<2}: {'1':<4} to {'25':<4}"
            + f" | Changes since {db['discord_coins']['last_update_time']}"
            if changes == "Shown"
            else ""
        )
        msg = await interaction.followup.send(embed=embed_first)
        msg2 = await interaction.followup.send(
            embed=discord.Embed(description="To be edited...", color=0xFFFFFF)
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
                        color=0xFFFFFF
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
                        color=0xFFFFFF
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
                        color=0xFFFFFF
                    )
                    await msg.edit(embed=embed_first)
                    second_message = "```ansi\n" + \
                        leaderboard_split_dict[2] + "```"
                    embed_second = discord.Embed(description=second_message, color=0xFFFFFF)
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
                    color=0xFFFFFF
                )
                await msg.edit(embed=embed_first)
                second_message = "```ansi\n" + leaderboard_split_dict[2] + "```"
                embed_second = discord.Embed(description=second_message, color=0xFFFFFF)
                embed_second.set_footer(
                    text=f"Changes since {db['discord_coins']['last_update_time']}"
                    if changes == "Shown"
                    else ""
                )
                await msg2.edit(embed=embed_second)
                await msg.clear_reactions()
                break
                # Ending the loop if user doesn't react after 15 seconds


    @app_commands.command()
    async def game_memory(self, interaction: discord.Interaction):
        """⚪ Test your memory by matching 2 tanks! (*outdated)"""

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
        a = random.sample(get_a_random_tank(True), 8) * 2
        random.shuffle(a)
        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
        answer = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {a[0]} {a[1]} {a[2]} {a[3]}\n:two: {a[4]} {a[5]} {a[6]} {a[7]}\n:three: {a[8]} {a[9]} {a[10]} {a[11]}\n:four: {a[12]} {a[13]} {a[14]} {a[15]}\n"

        def check(m):
            return m.channel.id == interaction.channel.id and m.author == interaction.user

        embed = discord.Embed(
            title="MEMORY GAME :brain:",
            description="Test your memory by matching 2 tanks!",
            color=0xFFFFFF,
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
                        title="MEMORY GAME :brain:",
                        description="You have quit the game",
                        color=0xFFFFFF,
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
                        color=0xFFFFFF, title="MEMORY GAME :brain:", description=board
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
                    color=0xFFFFFF,
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
                            color=0xFFFFFF,
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
                                color=0xFFFFFF,
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
                                color=0xFFFFFF,
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
                                    color=0xFFFFFF,
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
                                color=0xFFFFFF,
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
                        color=0xFFFFFF,
                        title="MEMORY GAME :brain:",
                        description=f"{board}\nThe game has timed out :hourglass:",
                    )
                    await message.edit(embed=embed)
                    break
            break
######################## SERVER-MISC REACTION COMMANDS END ######################


@client.event
async def on_message(message: discord.message):
    "React to messages on Discord"

    if (
        "moyai" in message.content.lower()
        or "🗿" in message.content.lower()
        or "moai" in message.content.lower()
    ):
        await message.add_reaction("🗿")
    if "!idea" in message.content.lower():
        await message.add_reaction("<:upvote:910250647264329728>")
        await message.add_reaction("<:downvote:910250215217459281>")


@client.event
async def on_ready():
    """Called when the Discord client is ready"""

    # Start up the 10 minute config refresher
    asyncio.create_task(goober_dash.refresh_config())
    asyncio.create_task(moonrock_miners.refresh_config())
    asyncio.create_task(rocket_bot_royale.refresh_config())

    # Goober Dash public levels ratings daily update
    asyncio.create_task(goober_dash.public_levels_ratings_update())

    # Check keys in repl.it's database
    matches_gd_global = db.prefix("global")
    matches_gd_local = db.prefix("country")
    matches_mm = db.prefix("trophies")
    matches_rbr = db.prefix("tankkings")
    print(matches_gd_global)
    print(matches_gd_local)
    print(matches_mm)
    print(matches_rbr)

    for key in db.keys():
        if key not in [matches_gd_global, matches_gd_local, matches_mm, matches_rbr]:
            print(key)

    print("Winterpixel community bot is ready.")


@tree.command(guild=discord.Object(id=962142361935314996))
async def sync_commands(interaction: discord.Interaction):
    """🔴 Synchronizes the slash commands for the bot test"""

    await tree.sync()
    await tree.sync(guild=discord.Object(id=962142361935314996))
    await interaction.response.send_message("Commands synced.")


tree.add_command(GooberDash(client)) # GB_NRC
tree.add_command(goober_dash(client)) # GB_RC
tree.add_command(MoonrockMiners(client)) # MM_NRC
tree.add_command(moonrock_miners(client)) # MM_RC
tree.add_command(RocketBotRoyale(client)) # RBR_NRC
tree.add_command(rocket_bot_royale(client)) # RBR_RC
tree.add_command(ServerMisc(client)) # Server_NRC
tree.add_command(server_misc(client)) # Server_RC


def main():
    try:
        client.run(discord_token)
    except:
        os.system("kill 1")


if __name__ == "__main__":
    main()
""
