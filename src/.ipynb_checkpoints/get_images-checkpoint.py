# Import a library to fetch web content using HTTP requests.
import requests
# Import a library to parse the HTML content of web pages.
from bs4 import BeautifulSoup
import pandas as pd
import urllib
import os
import numpy as np
import io
# Imports the Google Cloud client library
import math
import json
import time
import random
import pickle


def get_images(df_companies=df_companies, 
                start_row = 0, 
                file_path='/Users/ian/Documents/week3/Capstone1/images/', 
                restart=False,
                if restart == True:
                    moat_df=moat_df)   
    """
        A scrapy splash bot which pushes data requests into MOAT.com to grab creative along with information about when
        it was live
        
        Parameters
        ----------
        df_companies : pandas dataframe : str
            must have a column titled 'Moat Name' with a list of companies for the bot to iterate through
            
        start_row : int
            if the function errors out due to moat sending unprocessable data, the function might need to be restarted from a 
            specific point within df_companies
            
        file_path : str
            the location to save images to disc
            
        returns:
            a pandas dataframe with the following columns
            'Companies Brand','Brand','Image Name','First Seen','Last Seen','Screenpath'
        """
    
    if restart == False:
        #creates an empty dataframe for the MOAT data to be populated into
        df_moat = pd.DataFrame(columns=['Companies Brand','Brand','Image Name','First Seen','Last Seen','Screenpath'])

    #pulls in a count with the total number of images saved through this function. Used for naming convention when saving 
    #files to disc
    test = open('master_count.txt','r') 
    master_count = int(test.read())

    # iterates through the company names and 
    for company in list(df_companies['Moat Name'][start_row:]):
        #push a from request into MOAT's AWS server and returns JSON with pathname information to access a companies creatives
        URL = 'https://moat.com/api/entity_report/advertiser/'+company+'/creatives_query_info?end_date=2019-06-26&filter=all&report_type=display&start_date=2012-05-01'
        # Get the HTML content of the web page as a string.
        content = requests.get(URL).content
        #load content into JSON
        f = json.loads(content)
        time.sleep(4)

        #this portion of the function uses scrapy splash to grab information regarding the creative and saves it into a dataframe
        #along with the image which is saved to disc

        # page range will determine how many pages of creatives to pull from the company
        for page_num in range(0,4):
            try:
                # takes the JSON requested above and iterates through AJAX JSON files to grab creative information and link locations
                URL = 'https://moat.com'+(f['base_creative_url'])+'?device=desktop&device=mobile&end_date='+f['max_date']+'&filter=all&load_time='+str(f['load_time'])+'&page='+str(page_num)+'&page_size=42&period=month&report_type=display&start_date='+f['min_date']+'&time_hash='+f['time_hash']
                # Get the HTML content of the web page as a string.
                content = requests.get(URL).content
                #load content into JSON
                j = json.loads(content)
                for i in range(len(j['creative_data'])):
                    #checks to see if the creative being examined is a 300x250
                    if (j['creative_data'][i]['dims'][0] == 300) & (j['creative_data'][i]['dims'][1] == 250):
                        df_moat.loc[master_count] = str(company),j['creative_data'][i]['brand']['name'], j['creative_data'][i]['brand']['name']+str(master_count)+'.jpg', j['creative_data'][i]['first_seen'], j['creative_data'][i]['last_seen'], j['creative_data'][i]['screenpath']
                        #saves the image down to drive
                        urllib.request.urlretrieve(j['creative_data'][i]['screenpath'],file_path +j['creative_data'][i]['brand']['name']+str(master_count)+'.jpg')
                        #master count is used to create a unique creative name which will allows google creative 
                        #cloud to read and parce each component
                        master_count += 1
            except:
                continue       
            time.sleep(random.randint(18,25))

    # changes the datetime columns type
    df_moat['First Seen'] = pd.to_datetime(df_moat['First Seen'])
    df_moat['Last Seen'] = pd.to_datetime(df_moat['Last Seen'])
    #adds two new columns with dates before the campaign started and after it ended
    df_moat['before_campaign'] = df_moat['First Seen'] - pd.DateOffset(months=4)
    df_moat['after_campaign'] = min(df_moat['Last Seen'] + pd.DateOffset(months=4),datetime.date(2019, 6, 22))

    #if you get an error about timestamps in line 94, the below code might be useful
    #trend_moat['Last Seen'] = trend_moat['Last Seen'].apply(lambda x: min(datetime.datetime.strptime(str(trend_moat['Last Seen'][1]),'%Y-%m-%d %H:%M:%S').date(), datetime.date(2019, 6, 22)))

    # saves the master count from creatives to a .txt file
    with open('master_count.txt', 'w') as f:
        f.write(str(master_count))
        
    #changes dates format to date time    
    df_moat['Last Seen'] =  pd.to_datetime(df_moat['Last Seen'])
    df_moat['First Seen'] =  pd.to_datetime(df_moat['First Seen'])
    #ads a new campaign length column as an int
    df_moat['Campaign Length'] = df_moat['Last Seen'] - df_moat['First Seen']
    df_moat['Campaign Length'] = df_moat['Campaign Length'].dt.days
    return df_moat


