import requests
from bs4 import BeautifulSoup
import http
import sqlite3
import json
import time
import ssl
import sys
from itertools import chain

def scrape(result):
    mega_links = []
    mega_subtext = []
    for res in result:
        req = requests.get(res)
        soup = BeautifulSoup(req.text,'html.parser')
        link = soup.select('.storylink')
        subtext = soup.select('.subtext')
        mega_links.append(link)
        mega_subtext.append(subtext)
    mega_links = list(chain.from_iterable(mega_links))
    mega_subtext = list(chain.from_iterable(mega_subtext))
    return mega_links,mega_subtext

def sort_stories_by_votes(hnlist):
  return sorted(hnlist, key= lambda k:k['votes'], reverse=True)

def create_custom_hn(links, subtext):
  hn = []
  for idx, item in enumerate(links):
    title = item.getText()
    href = item.get('href', None)
    vote = subtext[idx].select('.score')
    age = subtext[idx].select('.age')
    if len(vote):
      points = int(vote[0].getText().replace(' points', ''))
      age = age[0].getText()
      if points > 99:
        hn.append({'title': title, 'link': href, 'votes': points,'age':age})
  return sort_stories_by_votes(hn)

def create_datebase(data):
    conn = sqlite3.connect("HackerNews.sqlite")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS NEWS(Title TEXT,Link TEXT,Score INTEGER,Age INTEGER)''')
    mega_links,mega_subtext = scrape(result)
    data = create_custom_hn(mega_links,mega_subtext)
    for item in data:
        cur.execute('''INSERT INTO NEWS(Title,Link,Score,Age)
        VALUES ( ? , ? , ?, ?)''',(item["title"],
        item["link"],item["votes"],item['age']))
    conn.commit()
    return "Done"

if __name__ == "__main__":
    print("\n\tThe best of HackerNews for you in CommandLine\n")
    print("\n\tIt Scrapes all the stories that have score over 100.\n")
    num = int(input("\tHow many pages of HackerNews you want to scrape of : "))
    result = ['https://news.ycombinator.com/news?p='+str(letter) for letter in range(1,num)]
    mega_links,mega_subtext = scrape(result)
    data = create_custom_hn(mega_links,mega_subtext)
    create_datebase(data)
    print("\n\tYour News-result has been stored into the DataBase.\n")
