import discord
import os
import requests
from replit import db

redditURL = os.environ['URL']

class RedditScrape:
  def __init__(self):
    self.header = {'User-Agent': 'Mozilla/5.0'}
    self.url = redditURL

  def getJSON(self):
    fileJSON = requests.get(self.url, self.header)
    return fileJSON

  def checkPostType(self, fileJSON):
    fileJSON = fileJSON.json()
    imgTags = ['.jpg', '.png', '.gif']
    if 'gallery' in fileJSON.json()['data']['children']['data']['url_overriden_by_dest']:
      if 'crosspost_parent_list' in fileJSON['data']['children']['data']:
        return 'crosspost gallery'
      else:
        return 'gallery'
    if '.jpeg' in fileJSON['data']['children']['data']['url_overriden_by_dest']:
      return 'jpeg'
    for tag in imgTags:
      if tag in fileJSON['data']['children']['data']['url_overriden_by_dest']:
        return tag
    return 'none'

  def handleGallery(self, fileJSON):
    fileJSON = fileJSON.json()
    checkStr = ''
    mediaID = []
    imgTags = ['.jpg', '.png', '.jpeg']
    for img in fileJSON['data']['children']['data']['gallery_data']['items']:
      mediaID.append(img['media_id'])

    for id in mediaID:
      for tag in imgTags:

        if tag in fileJSON['data']['children']['data']['media_metadata'][id]['m']:
          checkStr += fileJSON['data']['children']['data']['media_metadata'][id]['s']['u'].replace('amp;', '') + '\n'

        elif 'gif' in fileJSON['data']['children']['data']['media_metadata'][id]['m']:
            checkStr += fileJSON['data']['children']['data']['media_metadata'][id]['s']['gif'].replace('amp;', '') + '\n'

    checkLength = 'https://www.reddit.com' + fileJSON['data']['children']['data']['permalink'] +'\n' + checkStr

    if len(checkLength) > 2000:
      return 'https://www.reddit.com' + fileJSON['data']['children']['data']['permalink']
    else:
      return checkLength

  # Check both gallery functions to see if some things are necessary in the code
  def handleCrosspostGallery(self, fileJSON):
    fileJSON = fileJSON.json()
    checkStr = ''
    mediaIDs = []
    imgTags = ['.jpg', '.png', '.jpeg']

    for i in range(len(fileJSON['data']['children']['data']['crosspost_parent_list'])):
      for media in fileJSON['data']['children']['data']['crosspost_parent_list'][i]['gallery_data']['items']:
        mediaIDs.append(media['media_id'])

      for id in mediaIDs:
        for tag in imgTags:

          if tag in fileJSON['data']['children']['data']['crosspost_parent_list'][i]['media_metadata'][id]['m']:
            checkStr += fileJSON['data']['children']['data']['crosspost_parent_list'][i]['media_metadata'][id]['s']['u'].replace('amp;', '')

          elif 'gif' in fileJSON['data']['children']['data']['crosspost_parent_list'][i]['media_metadata'][id]['m']:
            checkStr += fileJSON['data']['children']['data']['crosspost_parent_list'][i]['media_metadata'][id]['s']['gif'].replace('amp;', '')

    checkLength = 'https://www.reddit.com' + fileJSON['data']['children']['data']['permalink'] +'\n' + checkStr

    if len(checkLength) > 2000:
      return 'https://www.reddit.com' + fileJSON['data']['children']['data']['permalink']
    else:
      return checkLength

  def handleImage(self, fileJSON):
    sub = os.environ['SUB']
    fileJSON = fileJSON.json()
    redditURL = 'https://www.reddit.com' + fileJSON['data']['children']['data']['permalink']
    title = fileJSON['data']['children']['data']['title'].replace('amp;', '')
    embed = discord.Embed(title=title,
    url=redditURL,
    description= 'Flair: ' + fileJSON['data']['children']['data']['link_flair_text'],
    color=discord.Color.red())
    embed.set_image(url=fileJSON['data']['children']['data']['url_overridden_by_dest'])
    embed.set_footer(text='Powered by ' + sub)   
    return embed 

  def handleJPEG(self, fileJSON):
    sub = os.environ['SUB']
    fileJSON = fileJSON.json()
    redditURL = 'https://www.reddit.com' + fileJSON['data']['children']['data']['permalink']
    title = fileJSON['data']['children']['data']['title'].replace('amp;', '')
    embed = discord.Embed(title=title,
    url=redditURL,
    description= 'Flair: ' + fileJSON['data']['children']['data']['link_flair_text'],
    color=discord.Color.red())
    imgURL = fileJSON['data']['children']['data']['preview']['images'][0]['source']['url'].replace('amp;','')
    embed.set_image(url=imgURL)
    embed.set_footer(text='Powered by ' + sub)
    return embed

  def start(self):
    fileJSON = self.getJSON()
    type = self.checkPostType(fileJSON)
    if type == 'gallery':
      str = self.handleGallery(fileJSON)
      return {'String' : str}
    elif type == 'crosspost gallery':
      str = self.handleCrosspostGallery(fileJSON)
      return {'String' : str}
    elif type == 'jpeg':
      embed = self.handleJPEG(fileJSON)
      return {'Embed' : embed}
    elif type == 'none':
      return 'none'
    else:
      embed = self.handleImage(fileJSON)
      return {'Embed' : embed}
