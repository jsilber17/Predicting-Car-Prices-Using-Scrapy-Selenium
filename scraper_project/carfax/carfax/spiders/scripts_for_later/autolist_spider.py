import requests
import csv 
import pandas as pd
import scrapy
from scrapy import Selector, Request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time


class AutoListSpider(scrapy.Spider): 
        name = 'autolist'
        allowed_domains = ['autolist.com']
        start_urls = ['https://www.autolist.com/listings#page=61&latitude=39.6888&location=Denver%2C+CO&longitude=-105.156']

        def __init__(self):
            self.driver = webdriver.Chrome('/usr/bin/chromedriver')

        def parse(self, response):
            
            self.driver.get(self.start_urls[0])
            with open('scrape_data.csv_4', 'w', newline='') as file: 
                csvwriter = csv.writer(file, delimiter='|') 
                csvwriter.writerow(['title', 'year', 'price', 'feature_names', 'feature_values', 'items'])
                iterator = 61
                
                while iterator <= 100:
            
                    time.sleep(10)
                    list_links = [link.get_attribute('href') for link in self.driver.find_elements_by_xpath("//div[@id='vehicle-list']//a")] 
                    for link in list_links: 
                    
                        cols = []
                    
                        try:
                        
                            self.driver.get(link)
                            time.sleep(10)
                            #WebDriverWait(self.driver, 15).until(EC.url_changes(self.start_urls))
                            sel = Selector(text=self.driver.page_source)
                            title = sel.xpath("//div[@class='title']/text()").extract()[0]
                            year = sel.xpath("//div[@class='title']/text()").extract()[0][0:4]
                            price = sel.xpath("//div[@class='title']/text()").extract()[1]
                            feature_names = sel.xpath("//span[@class='feature-block feature-label']/text()").extract()
                            feature_values = sel.xpath("//span[@class='feature-block feature-value']/text()").extract()
                            items = sel.xpath("//ul[@class='clean-list spaced-list']/li/text()").extract()
                            price_diff_green = sel.xpath("//h3[@class='jsx-724030441 price-diff green']/text()").extract()
                            price_diff_red = sel.xpath("//h3[@class='jsx-724030441 price-diff red']/text()").extract()
                            days_market = sel.xpath("//div[@class='jsx-724030441 box time-on-market']/h3[@class='jsx-724030441 time']/text()").extract()
                            price_change_green = sel.xpath("//h3[@class='jsx-724030441 price-history-diff green']/text()").extract()
                            price_change_red = sel.xpath("//h3[@class='jsx-724030441 price-history-diff red']/text()").extract()
                            self.driver.get(self.start_urls[0])
                            print(title, year, price, feature_names, feature_values, items, price_diff_green, price_diff_red, days_market, price_change_green, price_change_red)                    
                    
                            item = {
                                'title': title, 
                                'year': year,
                                'price': price,
                                'feature_names': feature_names,
                                'feature_values': feature_values,
                                'items': items,
                                'price_diff_green': price_diff_green,
                                'price_diff_red': price_diff_red,
                                'days_market': days_market,
                                'price_change': price_change_green,
                                'price_change_red': price_change_red
                                }
                            cols.append(item)

                            df = pd.DataFrame(cols, columns=['title', 'year', 'price', 'feature_names', 'feature_values', 'items', 'price_diff_green','price_diff_red', 'days_market', 'price_change_green', 'price_change_red']) 
                    
                            csvwriter.writerows(df.values)
                        except IndexError:  
                            print('No data was found for this car') 

                    iterator += 1 
                    self.start_urls = ['https://www.autolist.com/listings#page={}&latitude=39.6888&location=Denver%2C+CO&longitude=-105.156'.format(iterator)]
                    self.driver.get(self.start_urls[0])
                    time.sleep(10)
                self.driver.close()
            

    
