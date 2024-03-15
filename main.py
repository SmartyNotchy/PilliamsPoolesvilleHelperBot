# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

print("Hello World!")

import discord
from discord import app_commands
from discord.ext import tasks, commands

import re
from enum import Enum
import asyncio

import math
import os
import random

from difflib import SequenceMatcher

print("Modules Loaded")

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

GUILD_ID = 1106646802905702560

# Create the Bot
bot = commands.Bot(command_prefix='$', intents = discord.Intents.all())

######################################
## DISCORD ACTIVE DEVELOPER COMMAND ##
######################################

tree = bot.tree
@tree.command(name="active_dev_refresh", description="I hate slash commands I hate slash commands I hate slash commands", guild=discord.Object(id=GUILD_ID))
async def first_command(interaction):
  await interaction.response.send_message("Slash commands suck! But your bot needs them in order to get the active developer badge...")

############################
## DISCORD ADMIN COMMANDS ##
############################

@tree.command(name="printrules", description="Prints the Civilized PHS Server rules. Admin-only.", guild=discord.Object(id=GUILD_ID))
async def printrules(interaction):
  ctx = interaction.channel
  if "<@" + str(interaction.user.id) + ">" == "<@714930955957043360>":
    embed = discord.Embed(title="Server Rules", description="This server has stricter rules & management than most other school servers; hence the name \"Civilized PHS SMCS Server.\" If you don't like this, then join another PHS server and accept the responsibility; don't complain about it here.", color=0x3366ff)
    embed.add_field(name="Rule 1 - Keep Things PG-13(ish)", value="Keep things PG-13 (no NSFW). Swearing is discouraged, but there won't be consequences for it unless it's excessive & actively making other members uncomfortable.", inline=False)
    embed.add_field(name="Rule 2 - No Hate Speech", value="No racism, hate, bias, discrimination, sexism, homophobia, etc. Complaining about others **on civilized & logical grounds** is generally accepted, but keep things, well, *civilized*.", inline=False)
    embed.add_field(name="Rule 3 - No Doxxing", value="I can't really ban possession without being a hypocrite, but be cool & don't share someone's personal info with others. In other words: don't pull a SSSniperWolf.",inline=False)
    embed.add_field(name="Rule 4 - No (Serious) Threats", value="This should be self-explanatory.",inline=False)
    embed.add_field(name="Rule 5 - Plagiarism Bad", value="I generally won't care unless you're copy-pasting entire assignments.",inline=False)
    embed.add_field(name="Rule 6 - No Spamming", value="Don't spam pings or messages, it's annoying.",inline=False)
    embed.add_field(name="TL;DR", value="This is a civilized school server. If you wouldn't be comfortable with your parents viewing your messages, then rethink what you're posting.",inline=False)
    await ctx.send(embed=embed)

    embed = discord.Embed(title="ToS", color=0x009933, description="By sending messages in this server, you acknowledge that the content of said messages are logged (even if deleted/edited) and may be shown to applicable staff members in extreme cases where the safety and/or wellbeing of students and/or staff is threatened. (TL;DR, don't make any threats or racial cyberbullying or stuff or it WILL be reported to applicable staff members)")
    await ctx.send(embed=embed)

    embed = discord.Embed(title="Punishments", color=0xFF0000)
    embed.add_field(name="First Infraction", value="Warning")
    embed.add_field(name="Second Infraction", value="24 Hour Mute")
    embed.add_field(name="Third Infraction", value="Permanent Ban")
    embed.add_field(name="Exceptions", value="I can't predict every incident that will happen, so there are bound to be some edge cases; however, don't count on it.", inline=False)
    await ctx.send(embed=embed)

    embed = discord.Embed(title="Invitation Process", color=0xAD8460, description="You can suggest people to be invited by directly messaging me (please don't abuse this). If at least 2 admins approve, then an invitation poll will be set up for members of the server. A 2/3 majority is needed for the invitation to be fully approved & sent. If the invitation is rejected by the public, then a new poll for that person cannot be created again for the next month.")
    await ctx.send(embed=embed)
  else:
    embed=discord.Embed(title="No Perms <:NotLikeShift:1119797767175409674>", description="Hey, you aren't Pilliam... only Pilliam can use this command!", color=0xFF5733)
    await ctx.send(embed=embed)

##########################
## BATTLE BOT SIMULATOR ##
##########################

####
## Reading Events
####

nEvents = [] # Neutral Events
nEventsFile = open("battles/nEvents.txt")
while True:
    event = nEventsFile.readline().strip()
    if event == "":
        break
    else:
        mentions = re.findall("{\d}", event)
        mentions = (int(x[1]) for x in mentions)
        nEvents.append((max(mentions), event))

dEvents = [] # Death Events
dEventsFile = open("battles/dEvents.txt")
while True:
    event = dEventsFile.readline().strip()
    if event == "":
        break
    else:
        event = event.split("|")
        if len(event) != 2:
            print("Error reading death events")
            print("Debug:", event)
            exit(1)
        else:
            killed = int(event[1])
            event = event[0]
            mentions = re.findall("{\d}", event)
            mentions = (int(x[1]) for x in mentions)
            dEvents.append((max(mentions), event, killed))
####
## Helper Funcs
####

def chooseEvent(eventType, remainingPlayers):
  global nEvents, dEvents
  if eventType == 0:
      event = random.choice(nEvents)
      while remainingPlayers < event[0]:
          event = random.choice(nEvents)
      return event
  else:
      event = random.choice(dEvents)
      while remainingPlayers < event[0]:
          event = random.choice(dEvents)
      return event


async def send_dm(id, msg):
  try:
    user = await bot.fetch_user(id)
    await user.send(msg)
  except:
    pass

def getSuffix(i):
  if i % 100 >= 10 and i % 100 <= 19:
    return "th"
  if i % 10 == 1:
    return "st"
  if i % 10 == 2:
    return "nd"
  if i % 10 == 3:
    return "rd"
  return "th"


####
## Bot Setup
####

waitingForPlayers = False
askingTrivia = False
battleRunning = False

battleChannel = None
registeredPlayers = []
scores = [[], [], [], [], [], [], [], [], [], [], []]
accuracy = {}

questions = []
questionID = 0
inQuestion = False
questionTime = 0
correctBonus = 0
timeLeft = 0

numPlayersNotBots = 0
numPlayersAnswered = 0

@bot.event
async def on_message(message):
  global waitingForPlayers, askingTrivia, battleRunning, battleChannel, registeredPlayers, scores, questionID, inQuestion, questionTime, correctBonus, numPlayersAnswered, accuracy

  if message.author == bot.user:
    return

  # Trivia Scores
  if message.guild is None and ("<@" + str(message.author.id) + ">") in registeredPlayers and askingTrivia and inQuestion and (not ("<@" + str(message.author.id) + ">") in [x[0] for x in scores[questionID]]):
    correctAns = questions[questionID][1].lower().split("/")
    userAns = message.content.lower()

    isCorrect = False
    for ca in correctAns:
      if similar(ca, userAns) > 0.777:
        isCorrect = True
        break
    if isCorrect:
      numPlayersAnswered += 1
      await message.add_reaction("✅")
      scores[questionID].append(["<@" + str(message.author.id) + ">", correctBonus + int(questionTime*((1000 - correctBonus)/500))])
      accuracy["<@" + str(message.author.id) + ">"] += 1
      await message.channel.send("Answered correctly in " + str(round((500 - questionTime)*0.03, 2)) + " seconds for " + str(correctBonus + int(questionTime*((1000 - correctBonus)/500))) + " points!")
      #print("<@" + str(message.author.id) + "> answered Q{0} in {1} seconds for {2} points.".format(questionID, round((500 - questionTime)*0.03, 2), 500 + questionTime))
    elif "!bad" in message.content.lower():
      await message.add_reaction("🔎")
      await battleChannel.send("🔎 <@" + str(message.author.id) + "> requested a manual reviewal of Q{0}!".format(questionID))
    else:
      await message.add_reaction("❌")
  elif message.guild is None and ("<@" + str(message.author.id) + ">") in registeredPlayers and askingTrivia:
    if "!bad" in message.content.lower():
      await message.add_reaction("🔎")
      await battleChannel.send("🔎 <@" + str(message.author.id) + "> requested a manual reviewal of Q{0}!".format(questionID+1))

  # RNG yay
  if random.randint(0, 1000) == 420:
    await message.add_reaction("<:StrawberryJam:1107856772615655504>")
  
  if ("vashi" in message.content.lower() or "vasis" in message.content.lower()) and random.randint(0, 3) == 1:
    await message.add_reaction("<:Vasisht:1196660405225926666>")

  # Battle Registration
  #if not waitingForPlayers or message.channel != battleChannel:
  #  return

  #if message.author == bot.user or ("<@" + str(message.author.id) + ">") in registeredPlayers:
  #  return

  #registeredPlayers.append("<@" + str(message.author.id) + ">")
  #await message.add_reaction("⚔️")

####
## BATTLE SLASH COMMANDS
####

BattleType = Enum(value="BattleType", names=["APUSH Unit 1", "APUSH Unit 2", "APUSH Unit 3", "APUSH Unit 4",\
                                             "APUSH Unit 5", "APUSH Unit 6", "APUSH Unit 7", "APUSH Unit 8", "APUSH All Units"])
ScoreType = Enum(value="ScoreType", names=["Accuracy 50% Speed 50%", "Accuracy 75% Speed 25%", "Accuracy 90% Speed 10%"])

QUESTION_SETS = {
  "BattleType.APUSH Unit 1": ["apush/unit1.txt"],
  "BattleType.APUSH Unit 2": ["apush/unit2.txt"],
  "BattleType.APUSH Unit 3": ["apush/unit3.txt"],
  "BattleType.APUSH Unit 4": ["apush/unit4.txt"],
  "BattleType.APUSH Unit 5": ["apush/unit5.txt"],
  "BattleType.APUSH Unit 6": ["apush/unit6.txt"],
  "BattleType.APUSH Unit 7": ["apush/unit7.txt"],
  "BattleType.APUSH Unit 8": ["apush/unit8.txt"],
  "BattleType.APUSH All Units": ["apush/unit1.txt", "apush/unit2.txt", "apush/unit3.txt", "apush/unit4.txt", "apush/unit5.txt", "apush/unit6.txt", "apush/unit7.txt", "apush/unit8.txt"]
}

@tree.command(
    guild=discord.Object(id=GUILD_ID),
    name="questionsets",
    description="Lists available question sets for use in battles."
)

async def questionsets(interaction: discord.Interaction):
  embed = discord.Embed(title="Trivia Question Sets", description="List of question sets for use in trivia battles.", color=0x3366ff)
  
  for (key, value) in QUESTION_SETS.items():
    questions = []
    for setFile in value:
      #print(setFile)
      questionsFile = open("battles/{}".format(setFile)).read().strip().split("\n")
      questions += list(map(lambda x : x.split("]"), questionsFile))
    embed.add_field(name=(key[11:]), value="{} Questions".format(len(questions)))
  
  await interaction.response.send_message(embed=embed)



@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="battle",
  description="Start the register countdown for an Trivia Battle."
)

async def runbattle(interaction: discord.Interaction, topics: BattleType, scoring: ScoreType, numquestions: int):
  global waitingForPlayers, askingTrivia, battleRunning, battleChannel, registeredPlayers, scores, questions, timeLeft, questionID, inQuestion, questionTime, correctBonus, numPlayersAnswered, numPlayersNotBots, accuracy

  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! Battles can only be started in <#1173286856381710427>!*")
    return
  if waitingForPlayers or battleRunning or askingTrivia:
    await interaction.response.send_message("*Error! There is already a battle running!*") 
    return
  if numquestions <= 0:
    await interaction.response.send_message("*Error! The battle must ask at least 1 question!*")
    return

  questions = []
  
  topicQuestionSet = QUESTION_SETS[str(topics)]
  for setFile in topicQuestionSet:
    questionsFile = open("battles/{}".format(setFile)).read().strip().split("\n")
    questions += list(map(lambda x : x.split("]"), questionsFile))

  random.shuffle(questions)

  if numquestions > len(questions):
    await interaction.response.send_message("*Error! There are not enough questions in the question set. You can ask at most `{}` questions for the topic `{}`.*".format(len(questions), str(topics)[11:]))
    return
  
  registeredPlayers = ["<@" + str(interaction.user.id) + ">"]
  waitingForPlayers = True
  battleRunning = False
  battleChannel = interaction.channel
  await interaction.response.send_message(registeredPlayers[0] + " is starting a battle!")
  await interaction.channel.send("Topic: `" + str(topics)[11:] + "`\nQuestions: `" + str(numquestions) + "`\nScoring: `" + str(scoring)[10:] + "`\nUse /battleregister to register for the battle.\nRegistration is open for 5 minutes.")
  await interaction.channel.send(registeredPlayers[0] + ", you can skip the countdown by using /battleskip.")

  timeLeft = 300
  while timeLeft > 0:
    await asyncio.sleep(1)

    if not waitingForPlayers:
      # has been cancelled
      return
    
    timeLeft -= 1
    if timeLeft % 600 == 0 or timeLeft in [300, 120, 60]:
      await interaction.channel.send("Registration will close in " + str(timeLeft//60) + " minute(s).")
  battleRunning = True
  waitingForPlayers = False

  accuracy = {}
  for p in registeredPlayers:
    accuracy[p] = 0

  numPlayersNotBots = len(registeredPlayers)

  if len(registeredPlayers) < 10:
    await interaction.channel.send("Not enough people registered! Adding bot students...")
    players = open("battles/allstudents.txt").read().split("\n")
    random.shuffle(players)
    i = 0
    while len(registeredPlayers) < 10:
      await interaction.channel.send("> " + players[i] + " joins the battle!")
      registeredPlayers.append(players[i])
      i += 1
      await asyncio.sleep(1)
  
  if str(scoring) == "ScoreType.Accuracy 50% Speed 50%":
    correctBonus = 500
  elif str(scoring) == "ScoreType.Accuracy 75% Speed 25%":
    correctBonus = 750
  else:
    correctBonus = 900

  await asyncio.sleep(3)
  await interaction.channel.send("**----------- Battle Start! -----------**")
  players = registeredPlayers.copy()
  msg = ", ".join(players[:-1]) + ", and " + players[-1] + " are the players in this battle!" 
  await interaction.channel.send(msg)
  await interaction.channel.send("**" + str(len(players)) + " players remain.**")
  await asyncio.sleep(1)
  await interaction.channel.send("Questions will start in about 10 seconds. Please check your DMs.")
  for player in players:
    if player[0] == "<":
      await send_dm(player[2:-1], "**----- Scoring -----**\nYou will have 15 seconds each to answer {} questions.\nScoring for each question goes as follows:\n> `{}` Points for a Correct Answer\n> Up to `{}` additional points for faster answers\n> `0` Points for wrong answers/Not Finishing\nWrong answers will not penalize you if you get the correct answer later.\nThe player with the most points at the end will be the winner of the battle.\nIf I messed up on a question, type !bad to report the most recently answered question.\n\nHang tight for the battle to start!".format(numquestions,correctBonus,1000-correctBonus))



  waitingForPlayers = False
  askingTrivia = False
  battleRunning = True
  
  questions = questions[:numquestions]
  await asyncio.sleep(10)
  
  await interaction.channel.send("**--------- Asking Trivia... ---------**")

  # Ask Trivia Questions
  askingTrivia = True
  battleRunning = False
  questionID = 0
  questionTime = 500

  scores = [[] for i in range(len(questions))]
  for questionID in range(len(questions)):
    numPlayersAnswered = 0
    questionTime = 500
    inQuestion = True
    for player in players:
      if player[0] == "<":
        await send_dm(player[2:-1], "--------------------\nQ{0}: ".format(questionID+1) + questions[questionID][0])

    nextQEarly = False
    for i in range(500):
      await asyncio.sleep(0.03)
      if (numPlayersAnswered == numPlayersNotBots):
        nextQEarly = True
        break
      questionTime -= 1
    inQuestion = False
    for player in players:
      if player[0] == "<":
        endMsg = "Time's up"
        if nextQEarly:
          endMsg = "All non-bot players have answered"
          await asyncio.sleep(1)
        await send_dm(player[2:-1], "{}! The correct answer(s) were \"{}\".".format(endMsg, questions[questionID][1]))
      else:
        if random.randint(0, 3) == 0:
          if "Bozo" in player:
            pass
          else:
            scores[questionID].append([player, correctBonus + random.randint(0, 100)])

    await asyncio.sleep(3)

  # Leaderboard calculation
  leaderboard = {}
  for p in players:
    leaderboard[p] = 0
  for q in scores:
    for q_p in q:
      leaderboard[q_p[0]] += q_p[1]

  origLeaderboard = leaderboard.copy()
  leaderboard = list(leaderboard.items())
  leaderboard = sorted(leaderboard, key=lambda x : x[1])
  origScores = scores.copy()
  scores = leaderboard.copy()
  leaderboard = [p[0] for p in leaderboard]

  for player in players:
    if player[0] == "<":
      await send_dm(player[2:-1], "All the questions have been asked! Go back to <#1173286856381710427> for the results!")

  battleRunning = True
  askingTrivia = False
  await interaction.channel.send("**---------- Fighting Start! ----------**")
  await interaction.channel.send("The fighting is about to begin!")
  await asyncio.sleep(7)

  # Run Battle
  usedEvents = []
  dEventStartChance = 95
  dEventEndChance = 60
  totalPlayers = len(players)
  remainingPlayers = len(players)
  toKillPos = 0

  while len(players) > 1:
    # Roll Probabilities
    dEventChance = (dEventStartChance - dEventEndChance) * (remainingPlayers / totalPlayers) + dEventEndChance
    dEventChance = round(dEventChance)
    eventType = random.choices([1, 0], weights=(dEventChance, 100 - dEventChance))[0]
    event = chooseEvent(eventType, remainingPlayers)
    while event in usedEvents:
      event = chooseEvent(eventType, remainingPlayers)
    usedEvents.append(event)
    if eventType == 0:
      random.shuffle(players)
      involvedPlayers = players[:event[0]]
      await interaction.channel.send("> " + event[1].format(*([None] + involvedPlayers)))
    else:
      random.shuffle(players)
      killedIdx = event[2]-1
      killedPlayer = leaderboard[toKillPos]
      toKillPos += 1
      involvedPlayers = players[:event[0]]
      while killedPlayer in involvedPlayers and involvedPlayers.index(killedPlayer) != killedIdx:
        random.shuffle(players)
        involvedPlayers = players[:event[0]]
      involvedPlayers[killedIdx] = killedPlayer
      await interaction.channel.send("> " + event[1].format(*([None] + involvedPlayers)) + " **" + killedPlayer + " died.**")
      try:
        players.remove(killedPlayer)
      except:
        print(killedPlayer, players)
      dEvents.remove(event)

      remainingPlayers = len(players)

    await asyncio.sleep(3)

  # Print Leaderboard
  await interaction.channel.send("**---------- Battle Over! ----------**")
  await asyncio.sleep(2)
  await interaction.channel.send("Leaderboard:")
  await asyncio.sleep(0.5)
  leaderboard.reverse()
  scores.reverse()
  for i in range(len(leaderboard)):
    if leaderboard[i][0] == "<":
      await interaction.channel.send("> {0}. {1} ({2} points, {3}/{4} correct)".format(str(i+1) + getSuffix(i+1), leaderboard[i], scores[i][1], accuracy[leaderboard[i]], len(questions)))
    else:
      await interaction.channel.send("> {0}. {1} ({2} points)".format(str(i+1) + getSuffix(i+1), leaderboard[i], scores[i][1]))
    await asyncio.sleep(0.5)

  await asyncio.sleep(3)
  await interaction.channel.send("\nThanks for playing!\nBattles can now be started again!")
  battleRunning = False   







pass




@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="battlecancel",
  description="Cancels a Trivia Battle countdown. Can only be used during the wait phase."
)
async def skip(interaction: discord.Interaction):
  global waitingForPlayers, registeredPlayers, timeLeft
  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*")
    return
  elif not waitingForPlayers:
    await interaction.response.send_message("*Error! There is no countdown to cancel!*")
    return
  elif "<@" + str(interaction.user.id) + ">" != registeredPlayers[0]:
    await interaction.response.send_message("*Error! This command can only be used by the battle starter!*")
    return
  else:
    if timeLeft <= 2:
      await interaction.response.send_message("Oops, too late!")
      return
    
    waitingForPlayers = False
    battleChannel = None
    registeredPlayers = []
    scores = [[], [], [], [], [], [], [], [], [], [], []]

    questions = []
    questionID = 0
    inQuestion = False
    questionTime = 0
    timeLeft = 0

    await interaction.response.send_message("Countdown cancelled!")



@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="battleskip",
  description="Skip the Trivia Battle countdown."
)
async def skip(interaction: discord.Interaction):
  global waitingForPlayers, registeredPlayers, timeLeft
  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*")
    return
  elif not waitingForPlayers:
    await interaction.response.send_message("*Error! There is no countdown to skip!*")
    return
  elif "<@" + str(interaction.user.id) + ">" != registeredPlayers[0]:
    await interaction.response.send_message("*Error! This command can only be used by the battle starter!*")
    return
  else:
    timeLeft = 1
    await interaction.response.send_message("Countdown set to 1 second!")




@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="battleregister",
  description="Register for a Trivia Battle."
)
async def register(interaction: discord.Interaction):
  global waitingForPlayers, registeredPlayers, timeLeft
  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*")
    return
  elif not waitingForPlayers:
    await interaction.response.send_message("*Error! There is no battle to register for!*")
    return
  elif "<@" + str(interaction.user.id) + ">" in registeredPlayers:
    await interaction.response.send_message("*Error! You are already registered for this battle!*")
    return
  else:
    registeredPlayers.append("<@" + str(interaction.user.id) + ">")
    await interaction.response.send_message("⚔️ You have registered for the upcoming battle!")



@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="battleunregister",
  description="Unregister from a Trivia Battle."
)
async def unregister(interaction: discord.Interaction):
  global waitingForPlayers, registeredPlayers, timeLeft
  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*")
    return
  elif not waitingForPlayers:
    await interaction.response.send_message("*Error! There is no battle to unregister from!*")
    return
  elif not "<@" + str(interaction.user.id) + ">" in registeredPlayers:
    await interaction.response.send_message("*Error! You are not registered for this battle!*")
    return
  elif "<@" + str(interaction.user.id) + ">" == registeredPlayers[0]:
    await interaction.response.send_message("Error! You cannot unregister from a battle if you are the battle leader!")
    return
  else:
    registeredPlayers.remove("<@" + str(interaction.user.id) + ">")
    await interaction.response.send_message("🏳️ You have unregistered from the upcoming battle.")



@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="forceregister",
  description="Force-register a user for a Trivia Battle. Admin-only."
)
async def forceregister(interaction: discord.Interaction, player: str):
  global waitingForPlayers, registeredPlayers, timeLeft
  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*")
    return
  elif not waitingForPlayers:
    await interaction.response.send_message("*Error! There is no battle to register for!*")
    return
  elif "<@" + str(interaction.user.id) + ">" != "<@714930955957043360>":
    await interaction.response.send_message("*Error! This command can only be used by <@714930955957043360>!*")
    return
  elif player in registeredPlayers:
    await interaction.response.send_message("*Error! This player is already registered for this battle!*")
    return
  else:
    registeredPlayers.append(player)
    await interaction.response.send_message("⚔️ " + str(player) + " has been registered for the upcoming battle!")


@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="testdm",
  description="Test if your Discord Account is setup properly to join trivia battles"
)
async def register(interaction: discord.Interaction):
  await interaction.response.send_message("If you can see this message and just received a DM, everything's good to go!")
  await interaction.channel.send("If you did not receive a DM, refer to https://support.discord.com/hc/en-us/articles/217916488-Blocking-Privacy-Settings.")
  await send_dm(interaction.user.id, "If you're reading this, everything's all set! Happy trivia battling!")

pass
###################################
## DISCORD BOT ACTIVITY MESSAGES ##
###################################

# 0 = Playing
# 1 = Watching
# 2 = Listening

PRESENCE_ACTIVITIES = [
  (0, "Peter Zhao: The Game"),
  (0, "Celeste - Strawberry Jam Collab"),
  (0, "Celeste - Any% Speedrun"),
  (0, "Terraria"),
  (0, "Minecraft"),
  (0, "Hypixel Skyblock"),
  (0, "Visual Studio Code"),
  (0, "Replit Flask App"),
  (0, "Rhythm Doctor"),
  (0, "Rhythm Dogtor"),
  (0, "Discord Putt Party"),
  (0, "RCMS School Simulator"),
  (0, "The RCMS Dungeons"),
  (0, "Rick Roll Boss Fight"),
  (0, "Rick Roll Bus Fight"),
  (1, "Extrude, Planes, and Rotating Parts - Day 1 of 100 OnShape Journey"),
  (1, "Replit Discord Bot Tutorial"),
  (1, "The Worst Programming Language Ever - Mark Rendle - NDC Oslo 2021"),
  (1, "Brooke's Discord Status"),
  (1, "Depressed Doorbell Commits"),
  (1, "rick roll but with a different link"),
  (1, "You"),
  (1, "Over SmartyNotchy"),
  (1, "Over Poolesville Civilization"),
  (1, "Over Pilliam's Future"),
  (1, "For Slight Grammatical Errors"),
  (1, "Strawberry Jam - The Movie"),
  (1, "10 Minutes of Relaxing Computer Static Noises"),
  (1, "krishnan splatton 4 gameplay"),
  (1, "for new Kingman Quotes"),
  (1, "Polly Programmer: Full Lore EXPLAINED"),
  (1, "for leaked Water Tower Blueprints"),
  (2, "Stardew & Chill"),
  (2, "Celeste Strawberry Jams - Vol. 1"),
  (2, "Celeste Strawberry Jams - Vol. 2"),
  (2, "Celeste Strawberry Jams - Vol. 3"),
  (2, "Celeste Strawberry Jams - Vol. 4"),
  (2, "Celeste Strawberry Jams - Vol. 5"),
  (2, "Never Gonna Give You Up"),
  (2, "the AHiT OST"),
  (2, "the Terraria OST"),
  (2, "the Minecraft OST"),
  (2, "the Undertale OST"),
  (2, "the Deltarune OST")
]

ACTIVITY_TYPES = (discord.ActivityType.playing, discord.ActivityType.watching, discord.ActivityType.listening)

@tasks.loop(minutes=10.0)
async def change_status():
  random_activity = random.choice(PRESENCE_ACTIVITIES)
  await bot.change_presence(activity = discord.Activity(type = ACTIVITY_TYPES[random_activity[0]],
                                                       name = random_activity[1]))

#########################
## DISCORD BOT STARTUP ##
#########################

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
  if isinstance(error, commands.CommandNotFound) or isinstance(error, discord.HTTPException):
    pass
  raise error

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await tree.sync(guild=discord.Object(id=GUILD_ID))
  change_status.start()

from webserver import keep_alive

print("Attempting Logon")

try:
  pass
  #keep_alive()
  bot.run(open("C:/Users/smart/Desktop/Python/bot.txt", "r").readline())
except discord.HTTPException as e:
  if e.status == 429:
    print("The Discord servers denied the connection for making too many requests")
    print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
  else:
    raise e
