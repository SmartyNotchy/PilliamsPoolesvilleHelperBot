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
@tree.command(name="dreamluck", description="[DEBUG] Rigs the RNG.", guild=discord.Object(id=GUILD_ID))
async def dreamluck(interaction):
  global DREAM_LUCK_ACTIVATED
  if is_pilliam(interaction):
    DREAM_LUCK_ACTIVATED = True
    await interaction.response.send_message("Rigging the RNG for the next message you send!", ephemeral=True)
  else:
    await interaction.response.send_message("Nope!", ephemeral=True)

DENY_NEXT_MSG = False
@tree.command(name="debugdeny", description="[DEBUG] Denies the next command sent, or something like that.", guild=discord.Object(id=GUILD_ID))
async def dreamluck(interaction):
  global DENY_NEXT_MSG
  if is_pilliam(interaction):
    DENY_NEXT_MSG = True
    await interaction.response.send_message("ratio incoming", ephemeral=True)
  else:
    await interaction.response.send_message("Nope!", ephemeral=True)

######################
## HELPER FUNCTIONS ##
######################

async def send_dm(id, msg):
  try:
    user = await bot.fetch_user(id)
    await user.send(msg)
  except:
    pass

async def send_dm_embed(id, color, title, body):
  user = await bot.fetch_user(id)
  await user.send(embed=discord.Embed(title=title, description=body, color=color))
  
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

###############
## BOT SETUP ##
###############

messagesWithoutBrainrot = 0
BRAINROT_BLACKLIST = [
  "kys-",
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
  global quickplay_sessions

  if message.author == bot.user:
    return

  ####
  ## MESSAGE RNG
  ####

  global DREAM_LUCK_ACTIVATED, DENY_NEXT_MSG
  await custom_rng_reaction(message, "<:StrawberryJam:1107856772615655504>", 1001, 420)
  await custom_rng_reaction(message, "<:RainbowBerry:1107431137363644529>", 10001, 69)
  await custom_rng_reaction(message, "<:ballincat43:1256664028751593493>", 1000001, 420690)
  await custom_rng_reaction(message, "<:Vasisht:1196660405225926666>", 10, 1, ["vashi", "vasis"])
  await custom_rng_reaction(message, "🐺", 10, 1, ["alpha", "beta", "sigma"])
  if is_pilliam_id(message.author.id) and DREAM_LUCK_ACTIVATED:
    DREAM_LUCK_ACTIVATED = False
  if DENY_NEXT_MSG and not is_pilliam_id(message.author.id):
    await custom_rng_reaction(message, "❌", 1, 1)
    DENY_NEXT_MSG = False


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
        if messagesWithoutBrainrot >= 10:
          await message.add_reaction("❌")
          staff_channel = bot.get_channel(1253017097273868352)
          await staff_channel.send("https://discord.com/channels/1106646802905702560/" + str(message.channel.id) + "/" + str(message.id) + " <@" + str(message.author.id) + "> broke a no-brainrot streak of " + str(messagesWithoutBrainrot) + " messages! :skull:")
        messagesWithoutBrainrot = -1
        break
    messagesWithoutBrainrot += 1


@tree.command(name="nobrainrot", description="View the current no-brainrot message streak.", guild=discord.Object(id=GUILD_ID))
async def debugcounter(interaction):
  await interaction.response.send_message(str(messagesWithoutBrainrot), ephemeral=True)


##############################
## QUICKPLAY SLASH COMMANDS ##
##############################

QuestionTopics = Enum(value="QuestionTopics", names=["NSL Chapter 1", "NSL Chapter 2", "NSL Chapter 3", "NSL Unit 1 (Ch 1-3)"])

QUESTION_SETS = {
  "QuestionTopics.NSL Chapter 1": ["nsl/u1ch1.txt"],
  "QuestionTopics.NSL Chapter 2": ["nsl/u1ch2.txt"],
  "QuestionTopics.NSL Chapter 3": ["nsl/u1ch3.txt"],
  "QuestionTopics.NSL Unit 1 (Ch 1-3)": ["nsl/u1ch1.txt", "nsl/u1ch2.txt", "nsl/u1ch3.txt"]
}

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
      questionsFile = open("questions/{}".format(setFile)).read().strip().split("\n")
      questions += parseQuestionsFromTxt(questionsFile)
    embed.add_field(name=(key[15:]), value="{} Questions".format(len(questions)))
  
  await interaction.response.send_message(embed=embed)

def parseQuestionsFromTxt(txtLines):
  res_qlist = []
  reading_q = False
  for line in txtLines:
    line = line.strip()
    if "[QUESTION]" in line:
      assert not reading_q
      reading_q = True
      res_qlist.append(["", "Unknown Topic", ""])
    elif reading_q:
      if "[ANSWER]" in line:
        reading_q = False
        line = line[9:]
        #res_qlist[-1][-1] += "**--------------------------**"
        res_qlist[-1][2] = line
      elif "[TOPIC]" in line:
        res_qlist[-1][1] = line[8:]
        res_qlist[-1][0] += "Topic: ||`" + line[8:] + "`||\n"
      else:
        res_qlist[-1][0] += line + "\n"
  
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
    self.topicStats = {}
    self.currentFirstTry = True
    self.stats = {
      "correct": 0,
      "incorrect": 0,
      "skipped": 0
    }

    topicQuestionSet = QUESTION_SETS[str(topic)]
    for setFile in topicQuestionSet:
      questionsFile = open("questions/{}".format(setFile)).read().strip().split("\n")
      self.questions += parseQuestionsFromTxt(questionsFile)

    random.shuffle(self.questions)

    await self.sendInfo()
    await self.nextQuestion()

  async def sendInfo(self):
    cmdInfoString = "Question Set: `" + str(self.topic)[15:] + "`\nProgress: `" + str(max(self.questionNum, 0)) + "/" + str(len(self.questions)) + "`\n\nUse `!skip` to skip a question.\nUse `!end` to end this quickplay session.\nUse `!embedtoggle` to toggle message styles.\nUse `!stats` to view session stats. Stats are also sent on session end.\nUse `!info` to view this info text."
    if self.embedMode:
      await send_dm_embed(self.player, 0x9933ff, "Quickplay Session Info", cmdInfoString)
      await send_dm(self.player, "*Embeds not showing? Use `!embedtoggle` to toggle embeds and `!info` to re-send this help text.*")
    else:
      await send_dm(self.player, "**--- Quickplay Session Info ---**")
      await send_dm(self.player, cmdInfoString)
  
  async def sendStats(self):
    if self.questionNum == 0:
      if self.embedMode:
        await send_dm_embed(self.player, 0xffcc00, "Overall Stats", "Total Questions: 0/{} (0%)\n- No stats to show yet!".format(len(self.questions)))
      else:
        await send_dm(self.player, "**--- Overall Stats ---**\n" + "Total Questions: 0/{} (0%)\n- No stats to show yet!".format(len(self.questions)) + "\n**--------------------**")
    else:
      if self.embedMode:
        await send_dm_embed(self.player, 0xffcc00, "Overall Stats", "Total Questions: {}/{} ({}%)\n- Correct: {} ({}%)\n- Incorrect: {} ({}%)\n- Skipped: {} ({}%)"\
                            .format(self.questionNum, len(self.questions), round(100*self.questionNum/len(self.questions), 1),\
                                    self.stats["correct"], round(100*self.stats["correct"]/self.questionNum, 1),\
                                    self.stats["incorrect"], round(100*self.stats["incorrect"]/self.questionNum, 1),\
                                    self.stats["skipped"], round(100*self.stats["skipped"]/self.questionNum, 1)))
      else:
        await send_dm(self.player, "**--- Overall Stats ---**\n" + "Total Questions: {}/{} ({}%)\n- Correct: {} ({}%)\n- Incorrect: {} ({}%)\n- Skipped: {} ({}%)"\
                            .format(self.questionNum, len(self.questions), round(100*self.questionNum/len(self.questions), 1),\
                                    self.stats["correct"], round(100*self.stats["correct"]/self.questionNum, 1),\
                                    self.stats["incorrect"], round(100*self.stats["incorrect"]/self.questionNum, 1),\
                                    self.stats["skipped"], round(100*self.stats["skipped"]/self.questionNum, 1)) + "\n**--------------------**")
  async def nextQuestion(self):
    self.questionNum += 1
    self.currentFirstTry = True
    if self.questionNum >= len(self.questions):
      if self.embedMode:
        await send_dm_embed(self.player, 0xff0000, "Quickplay Session Completed!", "Congrats, you've completed the question set! This quickplay session has been ended. Feel free to start a new one anytime!")
      else:
        await send_dm(self.player, "Congrats, you've completed the question set! This quickplay session has been ended.")
      await self.sendStats()
      self.active = False
      return
    
    
    question = self.questions[self.questionNum]
    if self.embedMode:
      await send_dm_embed(self.player, 0x33ccff, "Quickplay Session - Question #" + str(self.questionNum+1) + "/" + str(len(self.questions)), question[0])
    else:
      await send_dm(self.player, "**--------------------------**\n" + question[0] + "**--------------------------**")

  def matchesPlayer(self, other):
    return self.player == other

  async def parse_msg(self, message):
    content = message.content.lower().strip()
    self.lastMessage = datetime.datetime.now()
    if content == "!skip":
      if self.embedMode:
        await send_dm_embed(self.player, 0x99ddff, "Skipped!", "All Accepted Answers:\n" + "\n".join("- " + x for x in self.questions[self.questionNum][2].split(",")))
      else:
        await message.add_reaction("⏭️")
        await send_dm(self.player, "Skipped! Answers: " + ", ".join(self.questions[self.questionNum][2].split(",")))
      self.stats["skipped"] += 1
      await self.nextQuestion()
    elif content == "!end":
      self.active = False
      if self.embedMode:
        await send_dm_embed(self.player, 0xff0000, "Quickplay Session Ended!", "Feel free to start a new one anytime.")
        await self.sendStats()
      else:
        await message.add_reaction("👋")
        await send_dm(self.player, "Quickplay Session Ended!")
        await self.sendStats()
    elif content == "!embedtoggle":
      self.embedMode = not self.embedMode
      if self.embedMode:
        await send_dm_embed(self.player, 0xffcc00, "Embed Mode Enabled!", "")
      else:
        await message.add_reaction("🗃️")
        await send_dm(self.player, "Embed Mode disabled!")
    elif content == "!info":
      await self.sendInfo()
    elif content == "!stats":
      await self.sendStats()
    elif len(content) > 0 and content[0] == "!":
      if self.embedMode:
        await send_dm_embed(self.player, 0xff0000, "Invalid Command!", "Use `!info` to view a list of commands.")
      else:
        await message.add_reaction("🚧")
        await send_dm(self.player, "Invalid Command! Use `!info` to view a list of commands.")
    else:
      correctAns = self.questions[self.questionNum][2].split(",")
      isCorrect = False
      for ca in correctAns:
        if ("[EX] " in ca and content == ca[5:].strip().lower()) or (not ("[EX] " in ca) and similar(ca, content) > 0.777):
          isCorrect = True
          break
      if isCorrect:
        if self.embedMode:
          await send_dm_embed(self.player, 0x33cc33, "Correct!", "All Accepted Answers:\n" + "\n".join("- " + x for x in self.questions[self.questionNum][2].split(",")))
        else:
          await message.add_reaction("✅")
          await send_dm(self.player, "Correct! All Correct Answers: " + ", ".join(self.questions[self.questionNum][2].split(",")))
        if self.currentFirstTry:
          self.stats["correct"] += 1
        else:
          self.stats["incorrect"] += 1
        await self.nextQuestion()
      else:
        self.currentFirstTry = False
        await message.add_reaction("❌")


@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="quickplay",
  description="Set up a quickplay trivia session."
)
async def quickplay(interaction: discord.Interaction, topics: QuestionTopics):
  global quickplay_sessions

  #if interaction.channel.name != "bots":
  #  await interaction.response.send_message("*Error! Quickplays can only be started in <#1173286856381710427>!*", ephemeral=True)
  #  return

  playerID = interaction.user.id
  for qps in quickplay_sessions:
    if qps.matchesPlayer(playerID) and qps.active:
      await interaction.response.send_message("*Error! You are already in a quickplay session! DM the bot `!end` to leave!*", ephemeral=True) 
      return
  
  await interaction.response.send_message("Creating quickplay session for `" + str(topics)[15:] + "`!", ephemeral=True)
  new_qps = QuickplaySession()
  await new_qps.setup(playerID, topics)
  quickplay_sessions.append(new_qps)

quickplay_sessions_expired = []
def check_active(qps, time_now):
  global quickplay_sessions_expired
  if time_now - qps.lastMessage > datetime.timedelta(hours=12):
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
      await send_dm_embed(qps.player, 0xff0000, "👋 Quickplay Session Closed!", "This quickplay session has been closed due to inactivity.\nFeel free to start a new one anytime.")
    else:
      await send_dm(qps.player, "👋 This quickplay session has been closed due to inactivity. Feel free to start a new one anytime.")
    await qps.sendStats()
  quickplay_sessions_expired = []

@tree.command(
  guild=discord.Object(id=GUILD_ID),
  name="testdm",
  description="Test if your Discord Account is properly setup to use quickplay sessions"
)
async def register(interaction: discord.Interaction):
  await interaction.response.send_message("If you can see this message and just received a DM, everything's good to go! If you did not receive a DM, refer to https://support.discord.com/hc/en-us/articles/217916488-Blocking-Privacy-Settings.", ephemeral=True)
  await send_dm(interaction.user.id, "If you're reading this, everything's all set!")

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
  bot.run(open("C:/Users/smart/Desktop/Python/bot.txt", "r").readline())
except discord.HTTPException as e:
  if e.status == 429:
    print("The Discord servers denied the connection for making too many requests")
    print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    os.system("kill 1")
  else:
    raise e
