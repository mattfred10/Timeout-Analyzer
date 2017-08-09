# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
from tutorial.items import *



class BBallPipeline(object):
    def __init__(self):
        self.connection = psycopg2.connect(host='localhost', database='CollegeBBall', user='postgres', password='')
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        bballtuplelist = [] #spider returns a dictionary of lists. need to convert to single entries

        skipheader = 0 #If game has a name (e.g., rivalry match (IOWA CORN CY-HAWK SERIES) or tournament) then the title is collected as an event

        if len(item.get('time')) < len(item.get('event')):
            skipheader = 1

        for i in range(0,len(item.get('time'))):  # Should be exactly one entry for every time stamp
            minutes = item.get('time')[i].split(':')[0]  # Convert from string #:## to seconds - need for comparisons later
            seconds = item.get('time')[i].split(':')[1]
            timeleft = 60*int(minutes)+int(seconds)
            #event has +1 because the crawler is grabbing from .css(.header) even though the rest are from .game-detail. This is a simple fix but maybe not rigorous.
            #gameid and teams are constant - teams needs to be converted to string (gameid may need to be as well)
            bballtuplelist.append((item.get('gameid'), str(item.get('teams')), timeleft, item.get('event')[i+skipheader], item.get('score')[i],)) #does teams need to be converted to string?

        self.cursor.executemany("""INSERT INTO playbyplay (gameid, teams, time, event, score) VALUES (%s, %s, %s, %s, %s)""", bballtuplelist)
        self.connection.commit()
        return item