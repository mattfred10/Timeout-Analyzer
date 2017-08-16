
import scrapy

class BBallSpider(scrapy.Spider):
    name = 'bballspider'
    start_urls = ['http://www.espn.com/mens-college-basketball/']

    def parse(self, response):
        for row in response.css('play-by-play'):
            yield ['time': time.css()]
