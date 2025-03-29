import os
import requests
from bs4 import BeautifulSoup
from replit import db
import re

mapleURL = os.environ['mapleURL']
mapleLink = os.environ['mapleLink']


class MapleUpdate():
  def __init__(self):
    self.header = {'User-Agent': 'Mozilla/5.0'}
    self.url = mapleURL
  


  def getHTML(self):
    r = requests.get(url=self.url, headers=self.header)
    c = r.content
    soup = BeautifulSoup(c, 'html.parser')
    return soup



  def findFirstPost(self, soup):
    #a = re.findall(r'<ul class="news-container rows">[\s\S]+<\/ul>', str(soup))
    #a = a[0].split('</li>')
    firstPost = re.findall(r'<a href="(.+)">', str(soup))
    return mapleLink + firstPost[9]



  def checkIfNew(self, firstPost):
    if 'mapleNews' not in db.keys():
      db['mapleNews'] = firstPost
      return firstPost

    if firstPost == db['mapleNews']:
      return False
    else:
      db['mapleNews'] = firstPost
      return firstPost
    


  def start(self):
    soup = self.getHTML()
    firstPost = self.findFirstPost(soup)
    return self.checkIfNew(firstPost)
