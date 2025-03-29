import os
import requests
from bs4 import BeautifulSoup
from replit import db

mangaURL = os.environ['mangaURL']
manga = os.environ['manga']
mangaLink = os.environ['mangaLink']

class MangaUpdate():
  def __init__(self):
    self.header = {'User-Agent': 'Mozilla/5.0'}
    self.url = mangaURL
  


  def getHTML(self):
    r = requests.get(url=self.url, headers=self.header)
    c = r.content
    soup = BeautifulSoup(c, 'html.parser')
    return soup



  def findFirstPost(self, soup):
    firstPost = ''
    counter = 0
    allPosts = soup.find_all('a', limit=12)
    for post in allPosts:

      if manga in post.text or mangaLink in post.text:
        firstPost += post.text + '\n'
        counter += 1

      if counter == 2:
        return firstPost

    return False


  
  def checkIfNew(self, firstPost):
    if 'mangaCh' not in db.keys():
      db['mangaCh'] = 0

    if firstPost != False:
      start = firstPost.index(' ')
      end = firstPost.index(' ', start+1)
      chapterNum = firstPost[start+1:end]

      if int(chapterNum) == db['mangaCh']:
        return False
      else:
        db['mangaCh'] = int(chapterNum)
        return firstPost
        
    return firstPost
    


  def start(self):
    soup = self.getHTML()
    firstPost = self.findFirstPost(soup)
    return self.checkIfNew(firstPost)
