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

import datetime

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
  await interaction.response.send_message("Slash commands suck! But your bot needs them in order to get the active developer badge...", ephemeral=True)

############################
## DISCORD ADMIN COMMANDS ##
############################

def is_pilliam(intrctn):
  return "<@" + str(intrctn.user.id) + ">" == "<@714930955957043360>"

def is_pilliam_id(user_id):
  return "<@" + str(user_id) + ">" == "<@714930955957043360>"

@tree.command(name="printrules", description="Prints the Civilized PHS Server rules. Admin-only.", guild=discord.Object(id=GUILD_ID))
async def printrules(interaction):
  ctx = interaction.channel
  if is_pilliam(interaction):
    embed = discord.Embed(title="Server Rules", description="This server has stricter rules & management than most other school servers; hence the name \"Civilized PHS SMCS Server.\" If you don't like this, then join another PHS server and accept the responsibility; don't complain about it here.", color=0x3366ff)
    embed.add_field(name="Rule 1 - PG-13", value="Keep things PG-13 (no NSFW). Swears are fine, slurs are not.", inline=False)
    embed.add_field(name="Rule 2 - No Hate Speech", value="No racism, hate, bias, discrimination, sexism, homophobia, etc.", inline=False)
    embed.add_field(name="Rule 3 - No Serious Threats", value="Anything that could be perceived as a legitimate threat is banned. If it's obviously in jest AND not too serious, it's fine. \"KYS\" = AutoMod 1 hour mute.",inline=False)
    embed.add_field(name="Rule 4 - Plagiarism Bad", value="Don't copy-pasting entire assignments.",inline=False)
    embed.add_field(name="Rule 5 - No Spamming", value="Don't spam pings or messages, it's annoying.",inline=False)
    embed.add_field(name="Rule 6 - No Drama", value="This isn't Twitter. Keep this a nice and friendly community. DMs exist for a reason.",inline=False)
    embed.add_field(name="TL;DR", value="Assume this server will inevitably get leaked, and don't send anything stupid.",inline=False)
    await ctx.send(embed=embed)

    embed = discord.Embed(title="Legal Yap", color=0x009933, description="By sending messages in this server, you acknowledge that the content of said messages are logged (even if deleted/edited) and may be shown to applicable staff members in extreme cases where the safety and/or wellbeing of students and/or staff is threatened. (TL;DR, don't make any threats or racial cyberbullying or stuff or it WILL be reported to applicable staff members)")
    await ctx.send(embed=embed)

    embed = discord.Embed(title="Punishments", color=0xFF0000, description="Literally whatever fits the situtation. You could call this admin abuse, but you really shouldn't be causing enough trouble to necessitate this in the first place.")
    await ctx.send(embed=embed)

    embed = discord.Embed(title="Invitation Process", color=0xAD8460, description="How members are added (and removed). These polls run for 3 days and are admin-only.")
    embed.add_field(name="Invitation Polls", value="75% majority required for an invitation, or 95% after one day. 3 month cooldown in between failed polls for a single person.", inline=False)
    embed.add_field(name="Expulsion Polls", value="If you really hate someone for some reason, an 90% majority (explicitly between YES and NO) will be enough to kick them out.", inline=False)
    await ctx.send(embed=embed)

    await interaction.response.send_message("Success!", ephemeral=True)
  else:
    await interaction.response.send_message("Nice try. If you actually wanted to see the rules, visit <#1106683398757564476>!", ephemeral=True)

DREAM_LUCK_ACTIVATED = False
@tree.command(name="dreamluck", description="I hired an astrophysicist, trust me rainbow berry reactions are a lot more common than you think.", guild=discord.Object(id=GUILD_ID))
async def dreamluck(interaction):
  global DREAM_LUCK_ACTIVATED
  if is_pilliam(interaction):
    DREAM_LUCK_ACTIVATED = True
    await interaction.response.send_message("Rigging the RNG for the next message you send!", ephemeral=True)
  else:
    await interaction.response.send_message("... did anything even happen?", ephemeral=True)

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


async def send_dm_embed(id, color, title, body):
  user = await bot.fetch_user(id)
  await user.send(embed=discord.Embed(title=title, description=body, color=color))
  
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


async def custom_rng_reaction(message, reaction, chance, numtoroll, prereqs=[""]):
  global DREAM_LUCK_ACTIVATED
  for prq in prereqs:
    if prq in message.content.lower():
      if random.randint(1, chance) == numtoroll or (is_pilliam_id(message.author.id) and DREAM_LUCK_ACTIVATED):
        await message.add_reaction(reaction)
        if chance >= 100:
          staff_channel = bot.get_channel(1253017097273868352)
          await staff_channel.send("https://discord.com/channels/1106646802905702560/" + str(message.channel.id) + "/" + str(message.id) + " Rolled a " + reaction + " reaction (1/" + str(chance) + ")!")
      return

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

messagesWithoutBrainrot = 0
BRAINROT_BLACKLIST = [
  "skibid",
  "fanu",
  "gya",
  "backshot",
  "camera man",
  "nathaniel b",
  "vro",
  "aura",
  "goon",
  "rizz",
  "wizz",
  "only in ohio",
  "duke dennis",
  "did you pray today",
  "baby gronk",
  "sussy",
  "sigma alpha",
  "sigma male",
  "alpha male",
  "beta male",
  "yogurt male",
  "m the alpha",
  "grindset",
  "andrew tate",
  "freddy fazbear",
  "smurf cat",
  "ishowspeed",
  "ambatakum",
  "griddy",
  "kai cenat",
  "edging",
  "whopper whopper whopper",
  "1 2 buckle",
  "busting it down",
  "with da sauce",
  "with the sauce",
  "john pork",
  "grimace sh",
  "amogus",
  "ayo da pizza",
  "ayo the pizza",
  "t-pose",
  "family guy moments",
  "family guy clips",
  "family guy funny",
  "subway surfer",
  "mewing",
  "quandale dingle",
  "biggest bird",
  "brawl stars"
]
BRAINROT_WHITELIST = {
  "camera man": ["camera mand"],
  "goon": ["lagoon"]
}


@bot.event
async def on_message(message):
  global messagesWithoutBrainrot
  global quickplay_sessions, waitingForPlayers, askingTrivia, battleRunning, battleChannel, registeredPlayers, scores, questionID, inQuestion, questionTime, correctBonus, numPlayersAnswered, accuracy

  if message.author == bot.user:
    return

  '''
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
  '''

  ####
  ## MESSAGE RNG
  ####

  global DREAM_LUCK_ACTIVATED
  await custom_rng_reaction(message, "<:StrawberryJam:1107856772615655504>", 1001, 420)
  await custom_rng_reaction(message, "<:RainbowBerry:1107431137363644529>", 10001, 69)
  await custom_rng_reaction(message, "<:ballincat43:1256664028751593493>", 1000001, 420690)
  await custom_rng_reaction(message, "<:Vasisht:1196660405225926666>", 10, 1, ["vashi", "vasis"])
  await custom_rng_reaction(message, "🐺", 10, 1, ["alpha", "beta", "sigma"])
  if is_pilliam_id(message.author.id) and DREAM_LUCK_ACTIVATED:
    DREAM_LUCK_ACTIVATED = False


  ####
  ## BRAINROT TRACKER
  ####

  if message.guild is None and str(message.author.id) != "819365581899825182":
    for qps in quickplay_sessions:
      if qps.active and qps.matchesPlayer(message.author.id):
        await qps.parse_msg(message)
  else:
    for br_keyword in BRAINROT_BLACKLIST:
      if br_keyword in message.content.lower() and all(not (x in message.content.lower()) for x in BRAINROT_WHITELIST.get(br_keyword, ["A"])):
        if messagesWithoutBrainrot >= 50:
          await message.add_reaction("❌")
          staff_channel = bot.get_channel(1253017097273868352)
          await staff_channel.send("https://discord.com/channels/1106646802905702560/" + str(message.channel.id) + "/" + str(message.id) + " <@" + str(message.author.id) + "> broke a no-brainrot streak of " + str(messagesWithoutBrainrot) + " messages! :skull:")
        messagesWithoutBrainrot = -1
        break
    messagesWithoutBrainrot += 1


@tree.command(name="nobrainrot", description="View the current no-brainrot message streak.", guild=discord.Object(id=GUILD_ID))
async def debugcounter(interaction):
  await interaction.response.send_message(str(messagesWithoutBrainrot), ephemeral=True)



####
## BATTLE SLASH COMMANDS
####

BattleType = Enum(value="BattleType", names=["NSL Chapter 1", "NSL Chapter 2", "NSL Chapter 3", "NSL Unit 1 (Ch 1-3)"])
ScoreType = Enum(value="ScoreType", names=["Accuracy 50% Speed 50%", "Accuracy 75% Speed 25%", "Accuracy 90% Speed 10%"])

QUESTION_SETS = {
  "BattleType.NSL Chapter 1": ["nsl/u1ch1.txt"],
  "BattleType.NSL Chapter 2": ["nsl/u1ch2.txt"],
  "BattleType.NSL Chapter 3": ["nsl/u1ch3.txt"],
  "BattleType.NSL Unit 1 (Ch 1-3)": ["nsl/u1ch1.txt", "nsl/u1ch2.txt", "nsl/u1ch3.txt"]}
'''"BattleType.APUSH Unit 1": ["apush/unit1.txt"],
  "BattleType.APUSH Unit 2": ["apush/unit2.txt"],
  "BattleType.APUSH Unit 3": ["apush/unit3.txt"],
  "BattleType.APUSH Unit 4": ["apush/unit4.txt"],
  "BattleType.APUSH Unit 5": ["apush/unit5.txt"],
  "BattleType.APUSH Unit 6": ["apush/unit6.txt"],
  "BattleType.APUSH Unit 7": ["apush/unit7.txt"],
  "BattleType.APUSH Unit 8": ["apush/unit8.txt"],
  "BattleType.APUSH All Units": ["apush/unit1.txt", "apush/unit2.txt", "apush/unit3.txt", "apush/unit4.txt", "apush/unit5.txt", "apush/unit6.txt", "apush/unit7.txt", "apush/unit8.txt"]
}'''

@tree.command(
    guild=discord.Object(id=GUILD_ID),
    name="questionsets",
    description="Lists available question sets for use in quickplay sessions."
)

async def questionsets(interaction: discord.Interaction):
  embed = discord.Embed(title="Trivia Question Sets", description="List of question sets for use in quickplay sessions.", color=0x3366ff)
  
  for (key, value) in QUESTION_SETS.items():
    questions = []
    for setFile in value:
      #print(setFile)
      questionsFile = open("battles/{}".format(setFile)).read().strip().split("\n")
      questions += parseQuestionsFromTxt(questionsFile)
    embed.add_field(name=(key[11:]), value="{} Questions".format(len(questions)))
  
  await interaction.response.send_message(embed=embed)


'''
@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="battle",
  description="Start the register countdown for an Trivia Battle."
)

async def runbattle(interaction: discord.Interaction, topics: BattleType, scoring: ScoreType, numquestions: int):
  global waitingForPlayers, askingTrivia, battleRunning, battleChannel, registeredPlayers, scores, questions, timeLeft, questionID, inQuestion, questionTime, correctBonus, numPlayersAnswered, numPlayersNotBots, accuracy

  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! Battles can only be started in <#1173286856381710427>!*", ephemeral=True)
    return
  if waitingForPlayers or battleRunning or askingTrivia:
    await interaction.response.send_message("*Error! There is already a battle running!*") 
    return
  if numquestions <= 0:
    await interaction.response.send_message("*Error! The battle must ask at least 1 question!*")
    return
  
  playerID = interaction.user.id
  for qps in quickplay_sessions:
    if qps.matchesPlayer(playerID) and qps.active:
      await interaction.response.send_message("*Error! You cannot start a battle while in a quickplay session! DM the bot `!end` to leave.*") 
      return

  questions = []
  
  topicQuestionSet = QUESTION_SETS[str(topics)]
  for setFile in topicQuestionSet:
    questionsFile = open("battles/{}".format(setFile)).read().strip().split("\n")
    questions += list(map(lambda x : x.split("]"), questionsFile))

  random.shuffle(questions)

  if numquestions > len(questions):
    await interaction.response.send_message("*Error! There are not enough questions in the question set. You can ask at most `{}` questions for the topic `{}`.*".format(len(questions), str(topics)[11:]), ephemeral=True)
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
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*", ephemeral=True)
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
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*", ephemeral=True)
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
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*", ephemeral=True)
    return
  elif not waitingForPlayers:
    await interaction.response.send_message("*Error! There is no battle to register for!*")
    return
  elif "<@" + str(interaction.user.id) + ">" in registeredPlayers:
    await interaction.response.send_message("*Error! You are already registered for this battle!*")
    return
  
  playerID = interaction.user.id
  for qps in quickplay_sessions:
    if qps.matchesPlayer(playerID) and qps.active:
      await interaction.response.send_message("*Error! You cannot join a battle while in a quickplay session! DM the bot `!end` to leave.*") 
      return
  
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
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*", ephemeral=True)
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
    await interaction.response.send_message("*Error! This command can only be used in <#1173286856381710427>!*", ephemeral=True)
    return
  elif not waitingForPlayers:
    await interaction.response.send_message("*Error! There is no battle to register for!*")
    return
  elif not is_pilliam(interaction):
    await interaction.response.send_message("*Error! This command can only be used by <@714930955957043360>!*", ephemeral=True)
    return
  elif player in registeredPlayers:
    await interaction.response.send_message("*Error! This player is already registered for this battle!*")
    return

  playerID = interaction.user.id
  for qps in quickplay_sessions:
    if qps.matchesPlayer(playerID) and qps.active:
      await interaction.response.send_message("*Error! This player is in a quickplay session!*") 
      return
    
  registeredPlayers.append(player)
  await interaction.response.send_message("⚔️ " + str(player) + " has been registered for the upcoming battle!")
'''

def parseQuestionsFromTxt(txtLines):
  res_qlist = []
  reading_q = False
  for line in txtLines:
    line = line.strip()
    if "[QUESTION]" in line:
      assert not reading_q
      reading_q = True
      res_qlist.append([""])
    elif reading_q:
      if "[ANSWER]" in line:
        reading_q = False
        line = line[9:]
        #res_qlist[-1][-1] += "**--------------------------**"
        res_qlist[-1].append(line)
      else:
        res_qlist[-1][-1] += line + "\n"
  
  return res_qlist


quickplay_sessions = []

class QuickplaySession:
  async def setup(self, player, topic):
    self.player = player
    self.topic = topic
    self.active = True
    self.embedMode = True
    self.lastMessage = datetime.datetime.now()
    self.questions = []
    self.questionNum = -1
    
    topicQuestionSet = QUESTION_SETS[str(topic)]
    for setFile in topicQuestionSet:
      questionsFile = open("battles/{}".format(setFile)).read().strip().split("\n")
      self.questions += parseQuestionsFromTxt(questionsFile)

    random.shuffle(self.questions)

    if self.embedMode:
      await send_dm_embed(self.player, 0x9933ff, "Quickplay Session - " + str(topic)[11:], "Use `!skip` to skip a question.\nUse `!end` to end this quickplay session.\nUse `!embedtoggle` to toggle message styles.")
    else:
      await send_dm(self.player, "**--- Quickplay Session ---**")
      await send_dm(self.player, "Topic: `" + str(topic)[11:] + "`\nUse `!skip` to skip a question.\nUse `!end` to end this quickplay session.\nUse `!embedtoggle` to toggle message styles.")
    await self.nextQuestion()

  async def nextQuestion(self):
    self.questionNum += 1
    if self.questionNum >= len(self.questions):
      if self.embedMode:
        await send_dm_embed(self.player, 0xff0000, "Quickplay Session Completed!", "Congrats, you've completed the question set! This quickplay session has been ended. Feel free to start a new one anytime!")
      else:
        await send_dm(self.player, "Congrats, you've completed the question set! This quickplay session has been ended.")
      self.active = False
      return
    
    
    question = self.questions[self.questionNum]
    if self.embedMode:
      await send_dm_embed(self.player, 0x33ccff, "Quickplay Session - Question #" + str(self.questionNum+1), question[0])
    else:
      await send_dm(self.player, "**--------------------------**\n" + question[0] + "**--------------------------**")

  def matchesPlayer(self, other):
    return self.player == other

  async def parse_msg(self, message):
    content = message.content.lower().strip()
    self.lastMessage = datetime.datetime.now()
    if content == "!skip":
      if self.embedMode:
        await send_dm_embed(self.player, 0x99ddff, "Skipped!", "All Accepted Answers:\n" + "\n".join("- " + x for x in self.questions[self.questionNum][1].split(",")))
      else:
        await message.add_reaction("⏭️")
        await send_dm(self.player, "Skipped! Answers: " + ", ".join(self.questions[self.questionNum][1].split(",")))
      await self.nextQuestion()
    elif content == "!end":
      self.active = False
      if self.embedMode:
        await send_dm_embed(self.player, 0xff0000, "Quickplay Session Ended!", "Feel free to start a new one anytime.")
      else:
        await message.add_reaction("👋")
        await send_dm(self.player, "Quickplay Session Ended!")
    elif content == "!embedtoggle":
      self.embedMode = not self.embedMode
      if self.embedMode:
        await send_dm_embed(self.player, 0xffcc00, "Embed Mode Enabled!", "")
      else:
        await message.add_reaction("🗃️")
        await send_dm(self.player, "Embed Mode disabled!")
    else:
      correctAns = self.questions[self.questionNum][1].split(",")
      isCorrect = False
      for ca in correctAns:
        if ("[EX] " in ca and content == ca[5:].strip().lower()) or (not ("[EX] " in ca) and similar(ca, content) > 0.777):
          isCorrect = True
          break
      if isCorrect:
        if self.embedMode:
          await send_dm_embed(self.player, 0x33cc33, "Correct!", "All Accepted Answers:\n" + "\n".join("- " + x for x in self.questions[self.questionNum][1].split(",")))
        else:
          await message.add_reaction("✅")
          await send_dm(self.player, "Correct! All Correct Answers: " + ", ".join(self.questions[self.questionNum][1].split(",")))
        await self.nextQuestion()
      else:
        await message.add_reaction("❌")


@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="quickplay",
  description="Set up a quickplay trivia session. Great for last-minute cramming or if you have no friends."
)
async def quickplay(interaction: discord.Interaction, topics: BattleType):
  global quickplay_sessions, registeredPlayers

  if interaction.channel.name != "bots":
    await interaction.response.send_message("*Error! Quickplays can only be started in <#1173286856381710427>!*", ephemeral=True)
    return
  if "<@" + str(interaction.user.id) + ">" in registeredPlayers:
    await interaction.response.send_message("*Error! You cannot start a quickplay while registered for a battle!*", ephemeral=True) 
    return

  playerID = interaction.user.id
  for qps in quickplay_sessions:
    if qps.matchesPlayer(playerID) and qps.active:
      await interaction.response.send_message("*Error! You are already in a quickplay session! DM the bot `!end` to leave!*", ephemeral=True) 
      return
  
  await interaction.response.send_message("Creating quickplay session for `" + str(topics)[11:] + "`!", ephemeral=True)
  new_qps = QuickplaySession()
  await new_qps.setup(playerID, topics)
  quickplay_sessions.append(new_qps)

quickplay_sessions_expired = []
def check_active(qps, time_now):
  global quickplay_sessions_expired
  if time_now - qps.lastMessage > datetime.timedelta(minutes=5):
    qps.active = False
    quickplay_sessions_expired.append(qps)
    return False
  return True

@tasks.loop(minutes=5.0)
async def update_qp_sessions():
  global quickplay_sessions, quickplay_sessions_expired
  time_now = datetime.datetime.now()
  quickplay_sessions = list(filter(lambda x : x.active and check_active(x, time_now), quickplay_sessions))
  for qps in quickplay_sessions_expired:
    if qps.embedMode:
      await send_dm_embed(qps.player, 0xff0000, "👋 Quickplay Session Closed!", "This quickplay session has been closed due to inactivity. Feel free to start a new one anytime.")
    else:
      await send_dm(qps.player, "👋 This quickplay session has been closed due to inactivity. Feel free to start a new one anytime.")
  quickplay_sessions_expired = []

@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="testdm",
  description="Test if your Discord Account is setup properly to join trivia battles"
)
async def register(interaction: discord.Interaction):
  await interaction.response.send_message("If you can see this message and just received a DM, everything's good to go! If you did not receive a DM, refer to https://support.discord.com/hc/en-us/articles/217916488-Blocking-Privacy-Settings.", ephemeral=True)
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
  update_qp_sessions.start()

print("Attempting Logon")

try:
  pass
  #keep_alive()
  bot.run(open("C:/Users/smart/Desktop/Python/bot.txt", "r").readline())
except discord.HTTPException as e:
  if e.status == 429:
    print("The Discord servers denied the connection for making too many requests")
    print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    os.system("kill 1")
  else:
    raise e
