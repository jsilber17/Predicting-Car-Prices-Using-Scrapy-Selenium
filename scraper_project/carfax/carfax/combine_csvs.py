import os 
import glob
import pandas as pd 

#os.chdir('/home/jrsilber/Projects/Predicting-Car-Prices_Using-Scrapy-Selenium/scraper_project/carfax/carfax/spiders/car_data')
os.chdir('spiders/car_data')
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames]).drop_duplicates()

combined_csv.to_csv('craigslist_csv_combined.csv', index=False)
