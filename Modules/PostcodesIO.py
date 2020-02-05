import json
import urllib.request


class PostcodeIO:
    def __init__(self):
        """Look up data from Postcodes.io server"""
        self.url = "http://api.postcodes.io/postcodes"

    def get_latlng(self, postcode):
        postcode.replace(' ', '')
        url = str(self.url) + '/' + postcode
        res = urllib.request.urlopen(url).read()
        data = res.decode('utf8')#.replace("'", '"')
        data = json.loads(data)
        latlng = [data["result"]["latitude"], data["result"]["longitude"]]
        return latlng

    def get_postcode(self, lng, lat):
        url = str(self.url) + '?lon=' + str(lng) + "&lat=" + str(lat)
        res = urllib.request.urlopen(url).read()
        data = res.decode('utf8')
        data = json.loads(data)
        if data["result"]:
            postcode = [data["result"][0]["postcode"]]  # Returned as a list
            return postcode[0]
        else:
            print('No postcode found')
            return "No Postcode"