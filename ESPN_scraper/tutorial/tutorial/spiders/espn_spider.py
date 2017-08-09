import scrapy
from datetime import date, timedelta
import json



class BBallSpider(scrapy.Spider):
    name = 'bball'


    #defining this in a function rather than as "start_urls" to ensure that it operates correctly
    def start_requests(self):
        urls = []
        #2005 is earliest play by play data on espn website
        for i in range(2004,2016): #skip offseason
            for iterdate in dategenerator(date(i, 11, 1), date(i, 12, 31)):
                urls.append('http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?lang=en&region=us&calendartype=blacklist&limit=300&dates=' + iterdate.strftime('%Y%m%d') + '&tz=America%2FNew_York')
            for iterdate in dategenerator(date(i+1, 1, 1), date(i+1, 4, 15)):
                urls.append('http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?lang=en&region=us&calendartype=blacklist&limit=300&dates=' + iterdate.strftime('%Y%m%d') + '&tz=America%2FNew_York')
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        data = json.loads(response.body)
        for event in data['events']:
            gameid = event['id']
            url = "http://www.espn.com/mens-college-basketball/playbyplay?gameId=" + gameid
            yield scrapy.Request(url, callback=self.parse_game)



    def parse_game(self, response):
         yield {
                'gameid': response.url.split('=')[1], #might be worth learning how to pass meta data, but this worked fine
                'teams': response.css('.team-name::text').extract(),
                'time': response.css('.time-stamp::text').extract(),
                'event': response.css('.game-details::text').extract(),
                'score': response.css('.combined-score::text').extract(),
                }


def dategenerator(start, end):
    current = start
    while current <= end:
        if current < end:
            yield current
            current += timedelta(days=1)
        else:
            yield current
            break