import MFLibrary as mf
import re

import time
from datetime import date, timedelta

import requests
import json
from bs4 import BeautifulSoup


import sqlite3


def generate_scoreboard_urls():
    """Systematically generates a list of urls for API calls"""
    urls = []
    for i in range(2008,2016):
        for iterdate in dategenerator(date(i, 11, 1), date(i, 12, 31)):
            urls.append('http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?lang=en&region=us&calendartype=blacklist&limit=300&dates=' + iterdate.strftime(
                    '%Y%m%d') + '&tz=America%2FNew_York')
        for iterdate in dategenerator(date(i + 1, 1, 1), date(i + 1, 4, 15)):
            urls.append(
                'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?lang=en&region=us&calendartype=blacklist&limit=300&dates=' + iterdate.strftime(
                    '%Y%m%d') + '&tz=America%2FNew_York')
    return urls

    # Unfortunately ESPN api support ends here (not sure why I can get score board but not individual events)


def get_game_ids(urls):
    """Surfs and parses API for game ids and team info"""
    gamedata = []

    for url in urls:
        try:
            req = requests.get(url)
        except:
            time.sleep(60)
            pass
        print(req)
        data = json.loads(req.text)
        if not data['events']:
            continue
        for event in data['events']:
            for competition in event['competitions']:
                gameid = competition['id']
                gamedate = competition['date'].split('T')[0] # Don't care about time zone.
                teams = []
                for competitor in competition['competitors']:
                    teamid = competitor['id']
                    homeaway = competitor['homeAway']
                    abr = competitor['team']['abbreviation']
                    name = competitor['team']['displayName']
                    teams.append([teamid, homeaway, abr, name])
                gamedata.append([gameid, gamedate, teams])
        if len(gamedata) > 10:
            break

    print(gamedata[-1])
    return gamedata


def get_playbyplay(gamedata):
    """Scrapes play by play data using game id"""

    results = []
    for game in gamedata:
        try:
            req = requests.get("http://www.espn.com/mens-college-basketball/playbyplay?gameId={!s}".format(game[0]))
            print('Game found:')
            print(req)  # gives html status code
        except:
            # Wait 1 minute and try again
            time.sleep(60)

        soup = BeautifulSoup(req.content, 'html.parser')
        header = 0  # Delete 1 from game index if there is a header
        for i,row in enumerate(soup.article.find_all('tr')):
            if row.th:
                header += 1
                continue  # skip header rows
            splittime = row.find_all('td','time-stamp')[0].string.split(':')
            gametime = int(splittime[0])*60 + int(splittime[1])  # MM:SS to seconds
            actor = int(re.search(r'\/([0-9]+)\.', row.find_all('img')[0]['src'])[1])
            event = row.find_all('td','game-details')[0].string
            splitscore = row.find_all('td','combined-score')[0].string.split('-')  # MM:SS to seconds
            score1 = int(splitscore[0])
            score2 = int(splitscore[1])

            results.append([int(game[0]), i-header, gametime, actor, event, score1, score2])
            print(row)
            break
        break
    return results

def db_insert(gamedata, results):
    conn = sqlite3.connect("C:\\Dropbox\\Dropbox\\HAXz\\CBBTO\\CBB.sqlite3")


def dategenerator(start, end):
    current = start
    while current <= end:
        if current < end:
            yield current
            current += timedelta(days=1)
        else:
            yield current
            break

if __name__ == "__main__":
    get_playbyplay(get_game_ids(generate_scoreboard_urls()))