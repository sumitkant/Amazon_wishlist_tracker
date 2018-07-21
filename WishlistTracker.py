
# coding: utf-8

# In[1]:


# Load Libraries
import time
import pandas as pd
import numpy as np

import warnings
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver

warnings.filterwarnings("ignore")

def open_browser():
    # Opens Chrome Browser
    path_to_chromedriver = 'D:/Setups/chromedriver_win32/chromedriver_2.40.exe'
    brow = webdriver.Chrome(executable_path = path_to_chromedriver)
    return brow

def capture_prices(browser):
    
    
    # Go to Amazon wishlist
    browser.get('https://www.amazon.in/hz/wishlist/ls/2HHS9D5KS8VQF')
    time.sleep(3)
    browser.execute_script("window.scrollTo(0, 10000)")
    time.sleep(15)

    products = browser.find_elements_by_xpath("//div[@class='a-fixed-right-grid']")
    pdts = []
    for item in products:
        pdts.append(item.text)
    pdts = pd.Series(pdts)
    names = [x[0] for x in pdts.str.split('\n')]
    pricesdf = pdts.str.extract(r'₹(\d{1,2}),(\d{1,2}),(\d{1,3})|₹(\d{1,3}),(\d{1,3})|₹(\d{1,3})')
    pricesdf.fillna('', inplace = True)
    prices = pd.DataFrame(names, columns = ['Item_Name'])
    prices['Price'] = pricesdf.sum(axis = 1)
    prices['Timestamp'] = pd.Timestamp.now()
    prices.head()
#     print ("Prices Captured : ", len(prices))
    price_dict = prices.to_dict('records')
    browser.quit()
    return price_dict

def worksheet_writer(new_dict):
    
    print ('---- Authorizing Credentials ----\n ')
    # Write to worksheet
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('sumitsamazonwishilisttracking-f1146cfb6b6a.json', scope)
    gc = gspread.authorize(credentials)

    wks = gc.open('python-whishlist-tracking').sheet1
    # Resize is required otherwise this unexpectly appends to 1001 row of sheet,
    # rather than at the end of the last data point
    wks.resize(len(wks.get_all_records())+1) 
    
    print ('Writing to Sheets ---> \n ')

    for i in np.arange(len(new_dict)):
        wks.append_row([new_dict[i]['Item_Name'], new_dict[i]['Price'], new_dict[i]['Timestamp']])
        print ('{} \t'.format(i+1))

def main():

    
    # Browser open
    print ('---- Opening Browser ----\n')
    browser = open_browser()
    print ('---- Browser opened ----\n')
    
    # Capture prices
    print ('---- Capturing Prices ----\n')
    this_dict = capture_prices(browser)
    print ('---- {} Prices captured -----\n'.format(len(this_dict)))
    
    # Write to worksheet
    print ('---- Uploading to Google Sheets ----\n ')
    worksheet_writer(this_dict)    
    print ('---- Appended captured prices to sheet ---- \n')
    
if __name__=="__main__":
    
    main()


# In[26]:


# # Extract entity names and prices
# item_headers = browser.find_elements_by_xpath("//h3[@class='a-size-base']//a[@class='a-link-normal']")
# len(item_headers)
# headers = []
# for h in item_headers:
#     headers.append(h.text)

# prices_whole = browser.find_elements_by_xpath("//span[@class='a-price-whole']")
# prices = []
# for p in prices_whole:
#     prices.append(int(''.join(p.text.split('.')[0].split(','))))

# print (len(prices))
# print (len(headers))

# df = pd.Series(headers).to_frame()
# df['Prices'] = prices
# df.columns = ['Item','Prices']
# df['Date'] = pd.datetime.today()

