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
    for i in range(2004,2016):
        for iterdate in dategenerator(date(i, 11, 1), date(i, 12, 31)):
            urls.append('http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?lang=en&region=us&calendartype=blacklist&limit=300&dates=' + iterdate.strftime(
                    '%Y%m%d') + '&tz=America%2FNew_York')
        for iterdate in dategenerator(date(i + 1, 1, 1), date(i + 1, 4, 15)):
            urls.append(
                'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?lang=en&region=us&calendartype=blacklist&limit=300&dates=' + iterdate.strftime(
                    '%Y%m%d') + '&tz=America%2FNew_York')
    print("Generated URLS!")
    return urls


def get_game_ids(urls):
    """Surfs and parses API for game ids and team info"""
    gamedata = []

    for url in urls:
        try:
            req = requests.get(url)
        except:
            time.sleep(60)
            pass
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

    print("collected game ids!")

    return gamedata


def get_playbyplay(gamedata):
    """Scrapes play by play data using game id"""

    badlogos = set()
    results = []
    for game in gamedata:

        while True:
            try:
                req = requests.get("http://www.espn.com/mens-college-basketball/playbyplay?gameId={!s}".format(game[0]))
                if len(results) % 5 == 0:
                    print('Game found: ' + game[0])
                    print(req)  # gives html status code
            except:
                # Wait 1 minute and try again
                print("Error. Retrying...")
                time.sleep(60)
            if req.status_code == 200:
                break
            print("Error. Retrying...")
            time.sleep(15)

        home = ''
        away = ''
        for team in game[2]:
            if team[1].lower() == 'home':
                home = team[2]
            else:
                away = team[2]

        soup = BeautifulSoup(req.content, 'html.parser')
        header = 0  # Delete 1 from game index if there is a header
        # Using i to create an index for each game - may be easier later than the rowid from sqlite
        for i, row in enumerate(soup.article.find_all('tr')):
            if row.th:
                header += 1
                continue  # skip header rows
            splittime = row.find_all('td','time-stamp')[0].string.split(':')
            gametime = int(splittime[0])*60 + int(splittime[1])  # MM:SS to seconds
            try:
                actor = int(re.search(r'\/([0-9]+)\.', row.find_all('img')[0]['src'])[1])
            except IndexError:
                # At least one game doesn't have team logos
                if int(game[0]) not in badlogos:
                    badlogos.add(int(game[0]))
                actor = -1
            event = row.find_all('td','game-details')[0].string
            splitscore = row.find_all('td','combined-score')[0].string.split('-')  # MM:SS to seconds
            awayscore = int(splitscore[0])
            homescore = int(splitscore[1])

            results.append([int(game[0]), game[1], i-header, gametime, actor, event, away, home, awayscore, homescore])

        # I apparently don't have enough memory, so I'm periodically dumping the result list.
        if len(results) >= 5000:
            db_insert(results)
            results = []

    mf.csv.write_list("BadLogos.csv", badlogos)

    return results


def make_dictionaries(gamedata):
    """Making dictionaries for use later"""

    teamABR = {}
    teamNUM = {}
    errordict = {}

    for game in gamedata:
        for team in game[2]:
            # Check if entry matches existing entry/exists at all
            try:
                if team[3] != teamABR[team[2]]:
                    errordict[team[2]] = team[3]
            except KeyError:  # If if doesn't exist, add it.
                teamABR[team[2]] = team[3]

            # Same except using numbers
            try:
                if teamNUM[team[0]] != team[3]:
                   errordict[team[0]] = team[3]
            except KeyError:
                teamNUM[team[0]] = team[3]

    mf.csv.write_dict("ABRdictionary.csv", teamABR)
    mf.csv.write_dict("NUMdictionary.csv", teamNUM)


def db_insert(results):
    """Put it into a db"""

    conn = sqlite3.connect("C:\\Dropbox\\Dropbox\\HAXz\\CBBTO\\data\\CBBdb.sqlite3")
    curr = conn.cursor()

    # Just gonna create the table here so I don't have to do it elsewhere
    # Pass if the table already exists
    try:
        curr.execute("""CREATE TABLE
                        playbyplay (
                        game_id int,
                        date string,
                        event_index int,
                        time int,
                        actor int,
                        event string,
                        away string,
                        home string,
                        away_score int,
                        home_score int
                        )
                        """)

    except sqlite3.OperationalError:
        # Tots fine that it already exists
        pass

    curr.executemany("""INSERT INTO playbyplay
                    (game_id, date, event_index, time, actor, event, away, home, away_score, home_score)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    """, results)

    conn.commit()
    conn.close()

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
    gamedata = get_game_ids(generate_scoreboard_urls())
    make_dictionaries(gamedata)
    get_playbyplay(gamedata)