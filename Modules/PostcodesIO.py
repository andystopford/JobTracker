import json
import urllib.request


class PostcodeIO:
    def __init__(self):
        """Look up latitude and longitude from Postcodes.io server"""
        self.url = "http://api.postcodes.io/postcodes/"

    def get_latlng(self, postcode):
        url = str(self.url) + postcode
        res = urllib.request.urlopen(url).read()
        data = res.decode('utf8')#.replace("'", '"')
        #print('data', data)
        data = json.loads(data)
        latlng = [data["result"]["latitude"], data["result"]["longitude"]]
        #print('latlng', latlng)
        return latlng