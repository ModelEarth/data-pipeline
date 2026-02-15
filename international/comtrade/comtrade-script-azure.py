########### Python 3.2 #############
import urllib.request, json

try:
    # ?flowCode=-1&customsCode=C01&motCode=1000
    url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"

    hdr ={
    # Request headers
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': '6237c576c1504e4e804849e00ea59d14',
    }

    req = urllib.request.Request(url, headers=hdr)

    req.get_method = lambda: 'GET'
    response = urllib.request.urlopen(req)
    print(response.getcode())
    print(response.read())
except Exception as e:
    print(e)
####################################