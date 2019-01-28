# -*- coding: utf-8 -*-
import requests
import pandas as pd
import datetime
import csv
import re
from bs4 import BeautifulSoup

class HTMLTableParser:

    def parse_url(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        return [(table['id'],self.parse_html_table(table))\
                for table in soup.find_all('table')]

    def parse_html_table(self, table):
        n_columns = 0
        n_rows=0
        column_names = []

        # Find number of rows and columns
        # we also find the column titles if we can
        for row in table.find_all('tr'):

            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows+=1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)

            # Handle column names if we find them
            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 else range(0,n_columns)
        df = pd.DataFrame(columns = columns,
                          index= range(0,n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1

        # Convert to float if possible
        for col in df:
            try:
                df[col] = df[col].astype(int)
            except ValueError:
                pass

        return df


def tablemaker(url):
    table = hp.parse_url(url)[0][1] # Grabbing the table from the tuple
    table.head()
    return table


def extractCoinNames(url):
    table = tablemaker(url)

    rank = table.Name.values

    coins_rank = []

    for item in rank:
        clean_item = re.sub(r'\n\n.*\n\n', '', item).replace('\n', '')
        coins_rank.append(clean_item)
        # coins_rank.append(item.replace('\n\n', '\"'))

    #return coins_rank
    return coins_rank


def extractCoinSymbols(url):
    table = tablemaker(url)
    rank = table.Symbol.values
    return rank

hp = HTMLTableParser()
now = datetime.datetime.now()
nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
nowDate = now.strftime('%Y-%m-%d')

coins_url = "https://coinmarketcap.com/all/views/all/"

coin_names = extractCoinNames(coins_url)
coin_symbols =extractCoinSymbols(coins_url)

# Save2File
file_name = nowDate + '_CMC_coins_rank.csv'
f = open(file_name, 'w', encoding='utf-8', newline='')
wr = csv.writer(f)
wr.writerow(["", nowDatetime])
wr.writerow(["No.", "Coin", "Symbol"])
for item in range(len(coin_names)):
    wr.writerow([item+1, coin_names[item], coin_symbols[item]])
f.close()
