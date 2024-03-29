# Winterpixel-Community-Bot
 A discord bot for winterpixel games discord made by the community (This bot is not officially made by Winterpixel)

## Requirements:
Run `pip install -r requirements.txt` to install the dependencies. Currently I am using Rapptz discord.py rewrite beta 2.0 so this will NOT work with the most recent official release of discord.py as of April 2022

## Usage: 

Join the discord to use the bot!

**If you're trying to make your own bot I'm sure you can figure it out. It should be pretty easy if you know what you're doing. rocketbot_client.py will sure to come in handy.**

## Features:

### Discord Bot Itself:
- Made with the newest version of Rapptz discord.py, using slash commands.

### 🚀 Rocket Bot Royale:
- Get user profile either via friend code or user id.
- List the leaderboard of any season, sorted by trophies (season 10 or later) or points/wins/player kills/bot kills (season 0 or later).

### 🛸 Moonrock Miners:
- List the leaderboard of any season, sorted by trophies (beta season 14 or later).

## Commands:
| **Command** | **Description** |
| :--- |:---|
| **`/bot_info`** | Get info about this bot |
| **`/leaderboard_rocket_bot_royale`** `mode (Trophies/Points/Wins/Player Kills/Bot Kills)` `changes (Shown/Hidden)` `season`| Return the specified season leaderboard of Rocket Bot Royale by various modes, default current |
| **`/leaderboard_moonrock_miners`** `changes (Shown/Hidden)` `season`| Return the specified season leaderboard of Moonrock Miners, default current |
| **`/get_user`** `user_type (User ID/Friend ID)` `id` `section`| Return info about a specified user with optional section(s) |
| **`/battle`** | Have a battle with a random bot! |
| **`/build_a_bot`** | Bear the responsibility of creating new life... I mean bot |
| **`/join_game`** | Join the current game |
| **`/start_game`**  | Start a game with the people joined |
| **`/my_balance`**  | Find out how much coins you have in discord |
| **`/transfer_coins`** `amount` `recipient`  | Transfer some coins to another user |
| **`/discord_coins_leaderboard`** `changes (Shown/Hidden)` | Return the discord coins leaderboard |
| **`/random_tank`** | Get a random tank |
| **`/long`** `length` `(barrel)`  | Build your supercalifragilisticexpialidocious long tank equipped with as many barrels as you want! |
| **`/get_crate_stats`** `one_star` `two_star` `three_star` | Optimize the use of in game crates and Estimate the amount of coins |
| **`/slot`** `bet` | Play the slot machine game |
| **`/memory`** | Test your memory by matching 2 tanks! |
| **`/double_or_half`** | Helps you get out of a rut if your balance is negative |
| **`/season`** | Return the current season and remaining time |
| **`/random_bot_name`** | Generate a random bot name |
| **`/fandom`** `article` | Fetch any articles from Rocket Bot Royale fandom wiki here |
| **`/plot_season`** `graph (Box Plot/League Trophies Range)` `mode (Trophies/Points (Box Plot only))` `season_start` `season_end` | Plot statistics graph and table about trophies or points in season(s) |
| **`/trophies_calculator`** `reason (Outranked / Outranked by / Killed / Killed by)` `your_trophies` `opponents_trophies` `format (text / graph)` | Calculate trophies gain/loss by reasons and plot the graph (optional) |

Want to suggest something? Open up an issue with the enhancement tag. You may also feel free to make a pull request if you want to implement it on your own.
