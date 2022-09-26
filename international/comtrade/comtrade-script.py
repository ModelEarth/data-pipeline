import http.client
import json
import time
import sys
import collections

# Had to run https://stackoverflow.com/questions/17309288/importerror-no-module-named-requests
# sudo pip3 install requests
import requests

# To run, enter the following command in a folder containing the comtrade-script.py file. 
# python3 also works
# python comtrade-script.py nokey

# Or you may run in an Anaconda Jupyter Notebook.

print ('Number of arguments:', len(sys.argv), 'arguments.')  
print ('Argument List:', str(sys.argv))  
# print ('Argument 2:', str(sys.argv[1]))  

# To get your API key, (not needed for batches of 10,000)

# api_key = "Not needed"
# if (len(sys.argv) > 1 and str(sys.argv[1]) != "-f"): api_key = str(sys.argv[1]) 
# else: print("Please enter an API key.")

# Will we need to move the following into main when running as a GitHub Action?

print("################");
url='https://comtrade.un.org/api/get?max=2&type=C&freq=A&px=HS&ps=2018&r=152&p=all&rg=all&cc=851712'
un_data=requests.get(url)
#print(un_data.content)

print("Validation:");
print(un_data.json()["validation"]);

un_data = un_data.json()["dataset"]; # For Python3 - https://stackoverflow.com/questions/35424124/google-maps-response-starts-with-b-how-can-i-retrieve-the-data

print("---");
print("Dataset Array:");
print(un_data)
print("---");
rowQuantity = len(un_data);
print(rowQuantity);
print("---");

timeRequest = time.time()
#rows={}; # Dictionary
rows = un_data;
requestBucket = 0
simArray = [] # Array of tuples, for dedupping with frozenset
# Examples: https://comtrade.un.org/data/doc/api/bulk/
#conn = http.client.HTTPSConnection("comtrade.un.org/api/get/bulk/C/A/2018/ALL/HS")
#payload = "{}"  # Was payload = "{}" but caused 403 error

def main():
    global requestBucket, timeRequest
    rowCount = 0
    get = rowQuantity; # determined by the max= in the API url # 20
    while (rowCount < get):
        preCount = rowCount
        rowCount = fetch_rows(mCount=rowCount,mMax=get)
    print("Total rowCount: " + str(rowCount))
    
    # Save rows to csv file
    #with open('row_ID_name.csv', 'w') as writer:
    #    [writer.write('{0},{1}\n'.format(key, value)) for key, value in rows.items()]
    with open('row_ID_name.csv', 'w') as writer:
        [writer.write("TradeValue\n")]
        [writer.write('{0}\n'.format(rows[0]["TradeValue"]))]
    writer.close()
    print('done')

def fetch_rows(mCount,mMax):
    # Genre Drama #18 and >= 2004, 350 with most popular first
    global requestBucket, timeRequest
    page = mCount;
    print(page)
    #conn.request("GET", "/3/discover/movie?page=" + str(page) + "&maximum=20&language=en-US&with_genres=18&sort_by=popularity.desc&primary_release_date.gte=2004&api_key=" + api_key, payload)
    #res = conn.getresponse()
    requestBucket += 1
    mCount += 1
    return mCount
    


if __name__ == '__main__':
    main()
