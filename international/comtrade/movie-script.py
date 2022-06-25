import http.client
import json
import time
import sys
import collections

# To run, enter the following command in a folder containing the script.py file.
# python3 also works
# python movie-script.py [your themoviedb.org API key]
# Or you may run in an Anaconda Jupyter Notebook.

print ('Number of arguments:', len(sys.argv), 'arguments.')  
print ('Argument List:', str(sys.argv))  
print ('Argument 2:', str(sys.argv[1]))  

# To get your API key, login to themoviedb.org then go to Settings and click API on the left.

#IMDB has an API too - https://stackoverflow.com/questions/1966503/does-imdb-provide-an-api

api_key = ""
if (len(sys.argv) > 1 and str(sys.argv[1]) != "-f"): api_key = str(sys.argv[1]) 
else: print("Please enter an API key.")

timeRequest = time.time()
movies={}; # Dictionary
requestBucket = 0
simArray = [] # Array of tuples, for dedupping with frozenset
conn = http.client.HTTPSConnection("api.themoviedb.org")
payload = ""  # Was payload = "{}" but caused 403 error

def main():
    global requestBucket, timeRequest
    movieCount = 0
    get = 350 # 350
    while (movieCount < get):
        preCount = movieCount
        movieCount = fetch_movies(mCount=movieCount,mMax=get)
    print("Total movieCount: " + str(movieCount))
    
    # Save movies to csv file
    with open('movie_ID_name.csv', 'w') as writer:
        [writer.write('{0},{1}\n'.format(key, value)) for key, value in movies.items()]
    writer.close()
    
    print("requestBucket prior to similar " + str(requestBucket)) # Should return 18
    for key in movies:
        fetch_similar(sCount=5,movieID=key)
        print("Code : {0}, Value : {1}".format(k, v))
    
    # Remove duplicates by moving into frozen set
    simArraySets = map(frozenset, simArray)
    deduped = set(simArraySets)
    
    # Save similar movies to csv file
    with open('movie_ID_sim_movie_ID.csv', 'w') as writer:
        # [writer.write('{0},{1}\n'.format(key, value)) for key, value in similar.items()]
        for eachSet in deduped:
            elem1, elem2 = eachSet
            writer.write('{0},{1}\n'.format(elem1, elem2))
    writer.close()
    print('done')



    
def fetch_movies(mCount,mMax):
    # Genre Drama #18 and >= 2004, 350 with most popular first
    global requestBucket, timeRequest
    page = mCount/20 + 1;
    conn.request("GET", "/3/discover/movie?page=" + str(page) + "&maximum=20&language=en-US&with_genres=18&sort_by=popularity.desc&primary_release_date.gte=2004&api_key=" + api_key, payload)
    res = conn.getresponse()
    requestBucket += 1
    print(res.status, res.reason)
    if res.status == 200:
        print("mCount at " + str(mCount) + " before load")
        data = res.read().decode('utf-8')
        json_data = json.loads(data)
        print(json_data)
        for i in range(0,20):
            if (i == 0):
                timeRequest = time.time()
            id = json_data["results"][i]["id"]
            title = json_data["results"][i]["title"]
            # overview = json_data["results"][i]["overview"]

            if (mCount < mMax): # Omit movies exceeding 350.
                mCount += 1
                movies.update({id:title})            
            print(mCount,id,title)
    else:
        # The API allows you to make 40 requests every 10 seconds. 20 is max per request.
        print("Failed fetch at movie count " + str(mCount) + ". Trying again. res.status:" + str(res.status))
        #time.sleep(5) # Wait 5 seconds, allows for up to two failures to occur in 10 seconds before success.
    return mCount

def fetch_similar(sCount,movieID):
    # Similar Movies
    global requestBucket, timeRequest 
    conn.request("GET", "/3/movie/" + str(movieID) + "/similar?language=en-US&page=1&maximum=" + str(sCount) + "&api_key=" + api_key, payload)
    res = conn.getresponse()
    requestBucket += 1
    
    #print(res.status, res.reason)
    if res.status == 200:
        print("sCount at " + str(sCount) + " before load")
        data = res.read().decode('utf-8')
        json_data = json.loads(data)
        ##print(json_data)
        found = json_data["total_results"]
        if (json_data["total_results"] > 5): found = 5
        #print(str(found) + " found")
        for i in range(0,found):
            #print("i:" + str(i))
            id = json_data["results"][i]["id"]
            simArray.append((movieID,id)) # Tuple - we allow dups at this stage, then clean by moving into a frozen set.
                               
        if (requestBucket >= 40):
            print("Go to sleep, requestBucket has " + str(requestBucket) + " requests in " + str(time.time()-timeRequest) + " seconds.")
            if (time.time()-timeRequest < 10):
                time.sleep(15 - (time.time()-timeRequest)) # Didn't work with 10 minus time so far, 11 works but increased to 15 as a precaution for testers.
            requestBucket = 0
            timeRequest = time.time()
    else:
        # The API allows you to make 40 requests every 10 seconds. Request.
        print("Failed fetch at request for similar movies to movieID " + str(movieID) + ". Trying again.")
        #time.sleep(10) # Wait 5 seconds, allows for up to two failures to occur in 10 seconds before success.
        #fetch_similar(sCount=sCount,movieID=movieID,requestBucket=requestBucket)
    return

if __name__ == '__main__':
    main()
