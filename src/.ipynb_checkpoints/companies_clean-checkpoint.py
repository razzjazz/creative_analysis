import numpy as np
import pandas as pd
from collections import Counter


def companies_clean():
    #read the raw companies file and do basic cleaning
    f = open('data/companies2.txt', 'r')
    raw = f.read()
    raw = raw.replace('"','')
    raw = raw.splitlines()
    #create a header and body
    header = raw[0:10]
    body = raw[10:]
    #convert the 1d list into a datafram
    master_body = []
    for i in range(1,995):
        master_body.append(body[:10])
        body=body[10:]
    df = pd.DataFrame(master_body)
    
    #clean the header info and add it to the dataframe
    head = []
    for i in header:
        head.append(i.replace(",",""))
    
    #finalize the dataframe
    df.columns = head

    #adds a column using MOAT's naming convention
    df['Moat Name'] = df['Organization Name'].str.replace(' ', '-')
    df['Moat Name'] = df['Organization Name'].str.replace("'", '-')
    df['Moat Name'] = df['Organization Name'].str.replace(".", '-')
    # the number of unique categories was too high to dummy. The following code reduces the number of categories down to 
    # around 240 

    #finds all the unique categories in the dataframe
    unique_categories = []
    for i in df['Category Groups']:
        unique_categories = unique_categories + i.split(', ')
    cat_dict = Counter(unique_categories)
    #creates a list of categories to be removed based on the number of occurances in the dataframe
    remove_list = [k for k,v in cat_dict.items() if v <= 2]
    # removes those categories from the categories column and creates a new categories simple field
    df['Categories_simple'] = df['Category Groups'].replace(remove_list, value='', regex=True)
    df['Categories_simple'] = df['Categories_simple'].apply(lambda x: list(filter(None, x.split(", ",))))
    
    #adding age of company to dataframe
    df['clean_date'] = df['Founded Date'].apply(lambda x: x[-4:])
    df['clean_date'].loc[df[df['clean_date']== '—'].index] = 2018
    df['clean_date'] = df['clean_date'].apply(lambda x: int(x))
    df['age'] = df['clean_date'].max() - df['clean_date']
    del df['clean_date']
    
    df.drop(['Number', 'Logo'], axis=1, inplace=True)

    return df