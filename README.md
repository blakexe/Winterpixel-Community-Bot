<h1 align="center">Winterpixel-Community-Bot</h1>
<img src="https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/media/banner.png" alt="banner">

<div align="center">

[![Website](https://img.shields.io/website?url=https%3A%2F%2Fwinterpixel-community-bot-20-ktank8k.replit.app&up_message=Up&up_color=brightgreen&down_message=Down&down_color=FF0000&label=Bot&nbsp;Status)](https://winterpixel-community-bot-20-ktank8k.replit.app)
[![Static Badge](https://img.shields.io/badge/Hosted%20On%20Replit-_?logo=replit&labelColor=grey&color=orange)](https://replit.com/@kTaNk8k/Winterpixel-Community-Bot-20)
[![Static Badge](https://img.shields.io/badge/Winterpixel%20Games-_?logo=discord&labelColor=grey&color=7289da)](https://discord.gg/kdGuBhXz2r)

</div>

<div align="center">
  <a href="#ℹ️-about">About</a>
  <span> • </span>
  <a href="#-requirements">Requirements</a>
  <span> • </span>
  <a href="#-usage">Usage</a>
  <span> • </span>
  <a href="#-bot-commands">Bot Commands</a>
  <span> • </span>
  <a href="#-showcase">Showcase</a>
  <span> • </span>
  <a href="#-contributing">Contributing</a>
  <span> • </span>
  <a href="#-disclaimer">Disclaimer</a>
  <span> • </span>
  <a href="#-license">License</a>
  <p></p>
</div>

## ℹ️ About
- **A Discord Bot for [Winterpixel Games Discord server](https://discord.gg/kdGuBhXz2r) made by the community.**
- Made with the newest version of [Rapptz discord.py](https://github.com/Rapptz/discord.py), using [slash commands](https://support.discord.com/hc/en-us/articles/1500000368501-Slash-Commands-FAQ).

>[!Important]
>This bot is not officially made by [WinterpixelGames Inc.](https://www.winterpixel.com/)

>[!Note]
>The bot is in the process of migrating to a web-based application.<br>Thus, the commands may be outdated or with limited functionality.
<br>

## 📝 Requirements
- Run `pip install -r requirements.txt` to install the dependencies.
<br>

## 🚀 Usage
- Join the [Winterpixel Games Discord server](https://discord.gg/kdGuBhXz2r) and try it out in `#bot-commands`!

<a href="https://discord.gg/mypstDMXP3"><img src="https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/media/join_discord_button.png" alt="Join Discord server"></a>
<br><br>

## 🤖 Bot Commands
<img width="60%" src="https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/media/demo_commands_list.gif" alt="demo commands list">

### 🔵 [Goober Dash](https://gooberdash.winterpixel.io/)
<details>
<summary>5 commands</summary>

  | Command | Example | Usage | Status |
  | -------- | -------- | -------- | -------- |
  | **goober_dash leaderboard** \<type\> \<changes\> \<country_code\> | `/goober_dash leaderboard type: 🏳️ Local changes: Shown country_code: CA` | Return the specified season leaderboard of Goober Dash of current season | $${\color{Green}\text{Up to date}}$$ |
  | **goober_dash official_levels** \<levels\> \<sorted_by\> \<order\> | `/goober_dash official_levels levels: Knockout Levels only sorted_by: Update Time (Update) order: 🔻 Descending` | Return a list of official levels of Goober Dash, sorted by various values | $${\color{Green}\text{Up to date}}$$ |
  | **goober-dash get_config** | `/goober-dash get_config` | Get the most updated Goober Dash server config | $${\color{Green}\text{Up to date}}$$ |
  | **goober-dash level_info** \<level_id\> | `/goober-dash level_info level_id: ef17d73e-cb9b-4bb7-a3a9-4dcc32d9d65f` | Return info about a specified Goober Dash level | $${\color{Green}\text{Up to date}}$$ |
  | **goober-dash user_info** \<user_type\> \<id_or_username\> | `/goober-dash user_info user_type: Username id_or_username: GoodGoob` | Return info about a specified Goober Dash user | $${\color{Green}\text{Up to date}}$$ |
</details>

### 🟢 [Moonrock Miners](https://moonrockminers.com/)
<details>
  <summary>2 commands</summary>

   Command | Example | Usage | Status |
  | -------- | -------- | -------- | -------- |
  | **moonrock_miners leaderboard** \<changes\> \<season\> | `/moonrock_miners leaderboard changes: Shown season: 15` | Return the specified season leaderboard of Moonrock Miners, default current season | $${\color{Green}\text{Up to date}}$$ |
  | **moonrock-miners get_config** | `/moonrock-miners get_config` | Get the most updated Moonrock Miners server config | $${\color{Green}\text{Up to date}}$$ |
</details>

### 🟡 [Rocket Bot Royale](https://rocketbotroyale.winterpixel.io/)
<details>
  <summary>9 commands</summary>

  | Command | Example | Usage | Status |
  | -------- | -------- | -------- | -------- |
  | **rocket_bot_royale leaderboard** \<mode\> \<changes\> \<season\> | `/rocket_bot_royale leaderboard mode: 🏆 Trophies changes: Hidden season: 20` | Return the specified season leaderboard of Rocket Bot Royale by various modes, default current season | $${\color{Green}\text{Up to date}}$$ |
  | **rocket-bot-royale fandom** | `/rocket-bot-royale fandom article: Weapons` | Fetch any articles from Rocket Bot Royale fandom here! | $${\color{Green}\text{Up to date}}$$ |
  | **rocket-bot-royale get_config** | `/rocket-bot-royale get_config` | Get the most updated Rocket Bot Royale server config | $${\color{Green}\text{Up to date}}$$ |
  | **rocket-bot-royale optimize_crate** \<one_star\> \<two_star\> \<three_star\> | `/rocket-bot-royale optimize_crate one_star: 20 two_star: 10 three_star: 2` | Optimize the use of in game crates and Estimate the amount of coins in Rocket Bot Royale | $${\color{Green}\text{Up to date}}$$ |
  | **rocket-bot-royale plot_season** \<graph\> \<mode\> \<start_season\> \<end_season\> | `/rocket-bot-royale plot_season graph: League Trophies Range mode: 🏆 Trophies start_season: 15 end_season: 19` | Plot statistics graph and table by various modes in season(s) in Rocket Bot Royale | $${\color{Green}\text{Up to date}}$$ |
  | **rocket-bot-royale random_tank** | `/rocket-bot-royale random_tank` | Get a random tank | $${\color{Yellow}\text{Obsolete}}$$ |
  | **rocket-bot-royale trophies_calc** \<reason\> \<your_trophies\> \<opponents_trophies]>  \<format\> | `/rocket-bot-royale trophies_calc reason: Outranked by your_trophies: 200 opponents_trophies: 800 format: Text` | Calculate trophies gain/loss by reasons and plot and graph (optional) in Rocket Bot Royale | $${\color{Yellow}\text{Obsolete}}$$ |
  | **rocket-bot-royale user_info** \<user_type\> \<id_or_code\> \<section\> | `/rocket-bot-royale user_info user_type: Friend Code id_or_code: f030d36f section: All` | Return info about a specified Rocket Bot Royale user with optional sections(s) | $${\color{Green}\text{Up to date}}$$ |
  | **rocket-bot-royale user_single_season_records** \<user_type\> \<id_or_code\> \<season\> | `/rocket-bot-royale user_single_season_records user_type: Friend Code id_or_code: c386f531 season: 4` | Return all types of seasons records in a season about a specified Rocket Bot Royale user | $${\color{Green}\text{Up to date}}$$ |
</details>

### ⚪ Server/Miscellaneous
<details>
  <summary>13 commands</summary>
 
  | Command | Example | Usage | Status |
  | -------- | -------- | -------- | -------- |
  | **server_misc discord_coins_leaderboard** \<changes\> | `/server_misc discord_coins_leaderboard changes: Hidden` | Return the Discord coins leaderboard | $${\color{Green}\text{Up to date}}$$ |
  | **server_misc game_memory** | `/server_misc game_memory` | Test your memory by matching 2 tanks! | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc battle** | `/server-misc battle` | Have a battle with a random bot! | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc bot_info** | `/server-misc bot_info` | Get info about this Discord bot | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc build_a_bot** | `/server-misc build_a_bot` | Bear the responsibility of creating new life... I mean bot | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc double_or_half** | `/server-misc double_or_half` | Helps you get out of a rut if your balance is negative | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc game_slot_machine** \<bet\> | `/server-misc game_slot_machine bet: 1` | Play the slot machine game! | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc join_game**  | `/server-misc join_game` | Join the current game | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc long_tank** \<length\> \<barrel\> | `/server-misc long_tank length: 5 barrel: 3` | Build your supercalifragilisticexpialidocious long tank equipped with as many barrels as you want! | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc my_balance** | `/server-misc my_balance` | Find out how much coins you have on Discord | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc random_bot_name** | `/server-misc random_bot_name` | Generate a random bot name | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc start_game** | `/server-misc start_game` | Start a game with the people joined | $${\color{Green}\text{Up to date}}$$ |
  | **server-misc transfer_coins** \<amount\> \<recipient\> | `/server-misc transfer_coins amount: 5 recipient: <@970784448633258054>` | Transfer some coins to another user on Discord | $${\color{Green}\text{Up to date}}$$ |
</details>

### 🔴 Bot (For developers only)
<details>
  <summary>1 command</summary>

   Command | Example | Usage | Status |
  | -------- | -------- | -------- | -------- |
  | **sync_commands** | `/sync_commands` | Synchronizes the slash commands for the bot test | $${\color{Green}\text{Up to date}}$$ |
</details>
<br>

## 🌟 Showcase
- `/rocket_bot_royale leaderboard` - A leaderboard with page view showing Rocket Bot Royale players ranking in a season.
<img width="25%" src="https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/media/demo_rbr_leaderboard.gif" alt="demo rbr leaderboard">

- `/rocket-bot-royale user_info` - A graph showing statistics of a Rocket Bot Royale player which are not shown in game.
<img width="50%" src="https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/media/demo_get_user.png" alt="demo get user">
 
- `/rocket-bot-royale plot_season` - A graph showing the ranges of trophies of different tiers in all season.
<img width="50%" src="https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/media/demo_plot_season.png" alt="demo plot season">
<img width="50%" src="https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/media/demo_plot_season_2.png" alt="demo plot season 2">

And many more!
<br><br>

## 🤝 Contributing
- Want to suggest something?
- Open up an [issue](https://github.com/blakexe/Winterpixel-Community-Bot/issues) with the `enhancement` label.
- You may also feel free to make a [pull request](https://github.com/blakexe/Winterpixel-Community-Bot/pulls) if you want to implement it on your own.

[![Pull Requests Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

![Alt](https://repobeats.axiom.co/api/embed/8c95b5e144a687c022819adab793b72de979a37d.svg "Repobeats analytics image")
<br><br>

## 📜 Disclaimer

```
© WinterpixelGames Inc. All rights reserved.
Winterpixel, Rocket Bot Royale, Goober Dash, and Moonrock Miners are trademarks, services marks, or registered trademarks of WinterpixelGames.
```
- This bot includes official media copyrighted (©) by [Winterpixel Games](https://www.winterpixel.com/).
- Though these media is subject to copyright, it is believed that its use qualifies as fair use under U.S. fair use laws when used on this tool, hosted on servers in the United States by [Replit, Inc](https://replit.com).
<br>

## 📝 License
The source code is licensed under [MIT license](https://github.com/blakexe/Winterpixel-Community-Bot/blob/main/LICENSE).
<br>

---

<p align="center">
Developed with 💖 by Community
</p>
