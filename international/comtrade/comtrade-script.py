import http.client
import json
import time
import sys
import collections

# To run, enter the following command in a folder containing the script.py file. 
# python3 also works
# python comtrade-script.py [your therowdb.org API key]
# Or you may run in an Anaconda Jupyter Notebook.

print ('Number of arguments:', len(sys.argv), 'arguments.')  
print ('Argument List:', str(sys.argv))  
print ('Argument 2:', str(sys.argv[1]))  

# To get your API key, login to therowdb.org then go to Settings and click API on the left.

#IMDB has an API too - https://stackoverflow.com/questions/1966503/does-imdb-provide-an-api

api_key = ""
if (len(sys.argv) > 1 and str(sys.argv[1]) != "-f"): api_key = str(sys.argv[1]) 
else: print("Please enter an API key.")

timeRequest = time.time()
rows={}; # Dictionary
requestBucket = 0
simArray = [] # Array of tuples, for dedupping with frozenset
conn = http.client.HTTPSConnection("api.therowdb.org")
payload = ""  # Was payload = "{}" but caused 403 error

def main():
    global requestBucket, timeRequest
    rowCount = 0
    get = 350 # 350
    while (rowCount < get):
        preCount = rowCount
        rowCount = fetch_rows(mCount=rowCount,mMax=get)
    print("Total rowCount: " + str(rowCount))
    
    # Save rows to csv file
    with open('row_ID_name.csv', 'w') as writer:
        [writer.write('{0},{1}\n'.format(key, value)) for key, value in rows.items()]
    writer.close()
    

if __name__ == '__main__':
    main()
