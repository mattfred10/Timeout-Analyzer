#ESPN stopped support for their API, so we are going to use a web browers work around
import scrapy

class BBallSpider(scrapy.Spider):
    name = 'bballspider'
    start_urls = ['http://www.espn.com/mens-college-basketball/']

    def parse(self, response):
        for row in response.css('play-by-play'):
            yield ['time': time.css()]