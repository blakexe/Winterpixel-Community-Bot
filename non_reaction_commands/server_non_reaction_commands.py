import discord
import random
import json
import asyncio
import os
from replit import db
from collections import defaultdict, OrderedDict
from discord import app_commands
from misc.random_bot_name_get import get_a_random_bot_name
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


# Initialize rocket bot royale client
rocket_bot_royale_client = RocketBotRoyaleClient(rbr_mm_email_password, rbr_mm_email_password)

async def refresh_config():
  """🟡 Refresh Rocket Bot Royale game configuration"""

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


players = []
bots = []
playing = False


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


class ServerMisc(app_commands.Group): # Server_NRC
    """Server non-reaction commands"""
  
    def __init__(self, bot: discord.client):
        super().__init__()

    @tree.command()
    @app_commands.describe(bet="The minimum bet is 1 coin")
    async def game_slot_machine(self, interaction: discord.Interaction, bet: int):
        """⚪ Play the slot machine game! (*outdated)"""

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
                    color=0xFF0000,
                    title="SLOT MACHINE :slot_machine:",
                    description=f"You don't have enough {coin[0]}",
                )
            )
        elif bet <= 0:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=0xFF0000,
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
                color=0xFFFFFF,
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
                    color=0xFFFFFF,
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
                color=0xFFFFFF,
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
    async def double_or_half(self, interaction: discord.Interaction):
        """⚪ Helps you get out of a rut if your balance is negative"""

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
                        color=0xFFFFFF,
                    )
                )
            else:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title=f"{interaction.user} tries their hand at resolving their debt...",
                        description=f"Lol. Your debt has been doubled. New Balance: {change_player_coin(id, name, coins, True)}<:coin1:910247623787700264>",
                        color=0xFFFFFF,
                    )
                )

    
    @tree.command()
    async def battle(self, interaction: discord.Interaction):
        """⚪ Have a battle with a random bot!"""

        await refresh_config()
        
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
            response = await RocketBotRoyaleClient.query_leaderboard(
                self, rocket_bot_royale_current_season, "tankkings_trophies", 50
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
    async def build_a_bot(self, interaction: discord.Interaction):
        """⚪ Bear the responsibility of creating new life... I mean bot"""

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
    async def join_game(self, interaction: discord.Interaction):
        """⚪ Join the current game"""

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


    @tree.command()
    async def start_game(self, interaction: discord.Interaction):
        """⚪ Start a game with the people joined"""

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
        embed1 = discord.Embed(color=0xFFFFFF)
        embed1.add_field(name="Players: ", value=response, inline=False)
        await interaction.response.send_message(response)
        msg = await interaction.channel.send("Starting game")
        #     await asyncio.sleep(0)
        moneys = OrderedDict()
        while len(players) >= 1:
            embed = discord.Embed(color=0xFFFFFF)
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
                    # db[player_c] = db[player_c] - cur_num
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
    async def my_balance(self, interaction: discord.Interaction):
        """⚪ Find out how much coins you have on Discord"""

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
    async def transfer_coins(self, interaction: discord.Interaction, amount: int, recipient: str):
        """⚪ Transfer some coins to another user on Discord"""

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
    async def random_bot_name(self, interaction: discord.Interaction):
        """⚪ Generate a random bot name"""

        await interaction.response.send_message(get_a_random_bot_name())

    
    @tree.command()
    @app_commands.describe(
        length="Length of the tank", barrel="Number of barrels to be equipped"
    )
    async def long_tank(self, interaction: discord.Interaction, length: int, barrel: int = 1):
        """⚪ Build your supercalifragilisticexpialidocious long tank equipped with as many barrels as you want!"""

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
    async def bot_info(self, interaction: discord.Interaction):
        """⚪ Get info about this Discord bot"""

        await interaction.response.defer(ephemeral=False, thinking=True)

        embed = discord.Embed()
        embed.title = "Bot info:"
        embed.description = "Open source Community Discord bot, being hosted on repl.it\n\nFor more info visit https://github.com/Blakiemon/Winterpixel-Community-Bot.\n\n All pull requests will be reviewed, and appreciated."
        embed.color = 0xFFFFFF
        await interaction.followup.send(embed=embed)
