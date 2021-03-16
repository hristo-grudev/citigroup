import datetime
import re

import scrapy
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader

from ..items import CitigroupItem
from itemloaders.processors import TakeFirst


base = 'https://www.citigroup.com/citi/news/xml/news_rss{}.xml'

class CitigroupSpider(scrapy.Spider):
	name = 'citigroup'
	start_urls = [base.format('')]
	current_year = datetime.datetime.today().year
	year = 2007

	def parse(self, response):
		post_links = re.findall(r'<link>.+</link>', response.text)
		for post in post_links[1:]:
			url = post[6:-7]
			print(url)
			yield scrapy.Request(url, self.parse_post)

		self.year += 1
		if self.year == self.current_year:
			print(self.year)
			raise CloseSpider('End')
		else:
			yield response.follow(base.format(self.year), self.parse)


	def parse_post(self, response):
		title = response.xpath('//div[contains(@class, "press-details")]/h1/text()|//div[@class="info"]/h1/text()').get()
		description = response.xpath('//div[@class="press-content text-container"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="info press-date"]//text()').get()

		item = ItemLoader(item=CitigroupItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
