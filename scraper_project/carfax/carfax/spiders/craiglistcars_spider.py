import requests
import csv 
import pandas as pd
import scrapy
from scrapy.http import Request
from scrapy import Selector


class AutoListSpider(scrapy.Spider): 
        name = 'craigslist'
        cities = ['newyork'] # 'chicago', 'losangeles', 'denver', 'rochester', 'seattle',
#                'madison', 'portland', 'atlanta', 'jacksonville', 'minneapolis', 'stlouis',
#                'nashville', 'topeka', 'boston', 'philadelphia', 'pittsburgh', 'milwaukee', 'stpaul', 
#                'richmond', 'charleston', 'anchorage', 'burlington', 'manchester', 'phoenix', 'albuquerque',
#                'spokane', 'santafe', 'sandiego', 'honolulu', 'jackson', 'boulder', 'detroit', 'grandrapids', 
#                'buffalo', 'providence', 'syracuse', 'newhaven', 'jerseycity', 'newark', 'sacramento', 'sanfrancisco']
        allowed_domains = ['craigslist.org']
        #start_urls = ['https://{city}.craigslist.org/d/cars-trucks/search/cta'.format(city=city) for city in cities]
        start_urls = ['http://newyork.craigslist.org/d/cars-trucks/search/cta']
        csv_number = 0

        def parse(self, response):
            sel = Selector(response) 
            for url in sel.xpath("//p[@class='result-info']/a/@href").extract(): 
                yield Request(url, callback=self.parse_craiglist_ad)

            next_page = sel.xpath("//span[@class='buttons']/a[@class='button next']/@href").extract_first() 
            next_page = 'http://newyork.craigslist.org' + str(next_page)

            if next_page:
                print('fuccccccccccck')
                print(next_page)
                yield Request(next_page, callback=self.parse_craiglist_ad)

        
        def parse_craiglist_ad(self, response):
            self.csv_number += 1 
            cols = []
            sel = Selector(response) 
            items = sel.xpath("//section[@id='postingbody']/text()").extract()
            items_2 = sel.xpath("//section[@id='postingbody']//strong").extract()
            important_info_fields = sel.xpath("//p[@class='attrgroup']//span/text()").extract()
            important_info_values = sel.xpath("//p[@class='attrgroup']//b/text()").extract()[1:]
            title = sel.xpath("//span[@id='titletextonly']/text()").extract()
            price = sel.xpath("//span[@class='price']/text()").extract()
            post_date = sel.xpath("//time/@datetime").get()
            important_info = list(zip(important_info_fields, important_info_values))
            city = response.url.split('.')[0].replace('https://', '')
    
            data_dict = {
                    'title': title,
                    'price': price,
                    'city': city,
                    'items': items,
                    'items_2': items_2, 
                    'important_info_fields': important_info,
                    'important_info_values': important_info_values,
                    'post_date': post_date,
                    'important_info': important_info
                    }

            cols.append(data_dict)

            df = pd.DataFrame(cols) 
            df.to_csv('car_data/out{}.csv'.format(self.csv_number))

            next_page = sel.xpath("//span[@class='buttons']/a[@class='button next']/@href").extract_first()
            next_page = "http://newyork.craigslist.org" + str(next_page)
            if next_page: 
                yield Request(next_page, callback=self.parse)


                            

    
