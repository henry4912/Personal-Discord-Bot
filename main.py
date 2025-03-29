
import discord
from discord.ext import commands, tasks
import os
#import asyncio
import requests
import traceback
import instagram_scrape
import manga_update
import maple_scrape
from replit import db
from keep_alive import keep_alive

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

TOKEN = os.environ['BOT_TOKEN']
ID = os.environ['ID']
USERID = os.environ['USERID']

URL = os.environ['URL']  # URL of the subreddit 
SUB = os.environ['SUB']
FLAIR = os.environ['FLAIR']
chID = os.environ['CHANNEL_ID']

users = []
insta = instagram_scrape.InstaScrape()
manga = manga_update.MangaUpdate()
maple = maple_scrape.MapleUpdate()

# FUNCTIONS

# Function to simulator rock, paper, scissors
# If it detects if the creator uses the command, loses on purpose
# Bot automatically wins if other user uses the command
def rps_func(msg, authorID):
  if authorID == ID:
    if msg == 'rock':
      return 'Scissors\nW'
    elif msg == 'scissors':
      return 'Paper\nW'
    elif msg == 'paper':
      return 'Rock\nW'
    else:
      return 'Invalid option :(\nStill a W'
  else:
    if msg == 'rock':
      return 'Paper\nL'
    elif msg == 'scissors':
      return 'Rock\nL'
    elif msg == 'paper':
      return 'Scissors\nL'
    else:
      return 'Invalid option :(\nL'

# Function to detect if the attachment on a reddit post is an image/gif or a video
def renderVidOrImg(post, sub):
  ifImg = ['.jpg', '.png', '.gif', 'gallery']
# Checks if the items in the array make the post an image/gif or image gallery
  for type in ifImg:    
# Checks if url overriden is in the json file, pure text posts do not have it
    if type in post['data']['url_overridden_by_dest']:  
# Creates a discord embed with the information of the post
      redditURL = 'https://www.reddit.com' + post['data']['permalink']
      title = post['data']['title'].replace('amp;', '')
      embed = discord.Embed(title=title,
      url=redditURL,
      description= 'Flair: ' + post['data']['link_flair_text'],
      color=discord.Color.red())
      embed.set_image(url=post['data']['url_overridden_by_dest'])
      embed.set_footer(text='Powered by ' + sub)
      return {'Embed' : embed}  # Returns dict to read if returns embed or string
  if '.jpeg' in post['data']['url_overridden_by_dest']:
    redditURL = 'https://www.reddit.com' + post['data']['permalink']
    title = post['data']['title'].replace('amp;', '')
    embed = discord.Embed(title=title,
    url=redditURL,
    description= 'Flair: ' + post['data']['link_flair_text'],
    color=discord.Color.red())
    imgURL = post['data']['preview']['images'][0]['source']['url'].replace('amp;','')
    embed.set_image(url=imgURL)
    embed.set_footer(text='Powered by ' + sub)
    return {'Embed' : embed}
# If the post has an image, will just post the links, cannot make image embeds
  redditURL = 'https://www.reddit.com' + post['data']['permalink']
  str = redditURL + '\n' + post['data']['url_overridden_by_dest']
  return {'String' : str}


def msgCounter(authorID):
  if str(authorID) in db.keys():
    db[str(authorID)] += 1
  else:
    db[str(authorID)] = 1


def emptyDatabase():
  for i in db.keys():
    if i.startswith('ID'):
      del db[i]


@bot.event
# Function to print out something to make sure the Bot is ready to run
async def on_ready():
  print("Bot Ready!")
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Hi!'))



@bot.command()
# Command function to detect !rps, prints out prompts and calls rps function
# Uses an array to store user ID for anyone running it to prevent spam, removes at end
async def rps(ctx):
  for i in users:
    if ctx.author == i:
      return
  users.append(ctx.author)
  await ctx.send('Type rock, paper, or scissors when I say shoot!')
  await asyncio.sleep(1)
  await ctx.send('Rock')
  await asyncio.sleep(0.5)
  await ctx.send('Paper')
  await asyncio.sleep(0.5)
  await ctx.send('Scissors')
  await asyncio.sleep(1)
  await ctx.send('Shoot!')
  msg = await bot.wait_for('message', check=lambda msg: msg.author == ctx.author)
  await ctx.send(rps_func(msg.content.lower(), str(ctx.author)))
  users.remove(ctx.author)



@bot.command()
async def msg(ctx):
  if str(ctx.author.id) in db.keys():
    string = 'You have sent ' + str(db[str(ctx.author.id)]+1) + ' messages in this server since 11:20 AM PST on 12/9/2021!'
    await ctx.send(string)
  else:
    string = 'You have sent 1 message in this server since 11:20 AM PST on 12/9/2021!'
    await ctx.send(string)



@tasks.loop(minutes=60.0)
async def instaScrape():
  print('Working on insta!')
  await bot.wait_until_ready()
  ch = bot.get_channel(434362745555517440)
  i = insta.checkIfNew()
  if i is not False:
    await ch.send(embed=i)


@tasks.loop(minutes=15.0)
async def mapleScrape():
  print('Checking for maple updates!')
  await bot.wait_until_ready()
  ch = bot.get_channel(396844844443631618)
  n = maple.start()
  if n is not False:
    await ch.send(n)


@tasks.loop(hours=4.0)
async def mangaUpdate():
  print('Checking for manga updates!')
  await bot.wait_until_ready()
  ch = bot.get_channel(397615422599462922)
  m = manga.start()
  if m is not False:
    await ch.send(m)


    

# Command to get images/gifs from the newest post on subreddit
@tasks.loop(seconds=90.0)
async def scrape(URL, SUB, chID, FLAIR, FLAIR2='None', FLAIR3='None', FLAIR4='None'):
  print("Working on scraping!") # Makes sure command is being ran

  # AUTOMATICALLY CLEANS OUT THE DATABASE IF DATA EXCEEDS 160 KEYS
  if len(db) > 160:
    emptyDatabase()
    
  ignore = os.environ['ignoreAuth']
  images = []     # List holds images just in case the post is an image gallery
  mediaIDs = []   # List that holds image IDs for images in image galleries
  r = requests.get(url=URL, headers={'User-Agent': 'Mozilla/5.0'}) # Gets json file
  #CHANNEL_ID = os.environ['CHANNEL_ID'] # Gets channel to send message to
  await bot.wait_until_ready()
  ch = bot.get_channel(chID)
# Try Except block for video or image posts that sometimes messes up with the 
# json file format. Needs the [0], but if it causes an error, run it without the [0].
  try:
    for post in r.json()['data']['children']:
      contentID = post['data']['id']
      if post['data']['author'] == ignore:
        return
      if post['data']['removed_by_category'] == 'deleted':
        return
      if contentID in db.values():
        return
      else:
        db['ID_' + str(len(db)+1)] = contentID
        if post['data']['link_flair_text'] == FLAIR or post['data']['link_flair_text'] == FLAIR2 or post['data']['link_flair_text'] == FLAIR3 or post['data']['link_flair_text'] == FLAIR4:
          return
        if 'url_overridden_by_dest' in post['data']:
          if 'gallery' in post['data']['url_overridden_by_dest']:
            if 'crosspost_parent_list' in post['data']:
              for i in range(len(post['data']['crosspost_parent_list'])):
                for media in post['data']['crosspost_parent_list'][i]['gallery_data']['items']:
                  mediaIDs.append(media['media_id'])
                for k in mediaIDs:
                  images.append(post['data']['crosspost_parent_list'][i]['media_metadata'][k]['s']['u'].replace('amp;', ''))
            else:
              for media in post['data']['gallery_data']['items']:
                mediaIDs.append(media['media_id'])
              for i in mediaIDs:
                images.append(post['data']['media_metadata'][i]['s']['u'].replace('amp;', ''))
            galResp = 'https://www.reddit.com' + post['data']['permalink'] +'\n'
            for imgURL in images:
              galResp += imgURL + '\n'
            if len(galResp) > 2000:
              await ch.send('https://www.reddit.com' + post['data']['permalink'])
            else:
              await ch.send(galResp)
          else:
            ans = renderVidOrImg(post, SUB)
            if 'Embed' in ans:
              await ch.send(embed=ans['Embed'])
            else:
              await ch.send(ans['String'])
  
  # Exception was used for testing when post needed [0] above in r.json()[0]...
  # Now used for JSONDecodeError error to allow the bot to continue running
  # if it runs into errors. (test)
  except Exception:
    err_ch = bot.get_channel(int(434178144216285184))
    await err_ch.send('https://www.reddit.com' + r.json()['data']['children'][0]['data']['permalink'])
    await err_ch.send(traceback.print_exc())
    await ch.send('<a:DinkDonk:918617842675499028> ERROR!!! <@' + str(USERID) + '> <a:DinkDonk:918617842675499028>')




@bot.event
async def on_message(ctx):
  Cword = os.environ['CODE_WORD']
  Cresponse = os.environ['CODE_RESPONSE']

  await bot.process_commands(ctx)
  if ctx.author == bot.user:
    return

  if ctx.author.bot:
    return

  if ctx.content.startswith(Cword):
    await ctx.channel.send(Cresponse)

  if ctx.author != bot.user:
    msgCounter(ctx.author.id)

    

#emptyDatabase()

scrape.start(URL, SUB, int(chID), FLAIR)
#instaScrape.start()
mangaUpdate.start()
mapleScrape.start()
keep_alive()
try:
  bot.run(TOKEN)
except:
  os.system('kill 1')
