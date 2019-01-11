from bs4 import BeautifulSoup
from urllib.request import urlopen
import argparse
import re

class AutoWeber():
    def __init__(self):
        self._html = None
        self._data = []
        self._htmlText = None
        # Django's RE for determining a website
        self.urlRE = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    # Determine whether the url is a website.
    def _isWebsite(self, url):
        return self.urlRE.search(url) is not None
    
    def loadHtml(self, url):
        res = ''
        if self._isWebsite(url):
            res = urlopen(url)
        else:
            res = open(url)

        # Load BeautifulSoup object for the webpage
        self._htmlText = res.read()
        self._html = BeautifulSoup(self._htmlText, 'html.parser')
        self._data = []

    # Adds data for analysis
    def addData(self, data):
        self._data.append(data)
    
    # Clear all data
    def clearData(self):
        self._data = []

    def _getTag(self, line):
        insideTag = re.compile(r"<([^/>]*)>")
        return re.findall(insideTag, line)[0]

    def _getImmediateTags(self):
        results = []
        for entity in self._data:
            # Find first instance
            found = re.compile(r"<[^>]*>{}</[^>]*>".format(entity))
            tags = re.findall(found, self._htmlText)
            for tag in tags:
                nameTag = self._getTag(tag).split()
                results.append(self._html.find_all(nameTag, string=entity)[0])
        return results 

    # 
    def deriveCommonStructure(self):
        tags = self._getImmediateTags()
        tagHeir = {}
        print(tags)
        for tag in tags:
            tagHeir[tag] = list(tag.parents)
        layers = set()
        i = 0
        while len(layers) != 1:
            layers = set()
            for key, val in tagHeir.items():
                newStr = BeautifulSoup(str(val[i]),'html.parser')
                layers = layers.union(set(newStr))
                print("Unioned layer: {}".format(layers))
            print("Current set: {}".format(layers))
            i += 1
        print("Final structure: {}".format(layers))

ap = argparse.ArgumentParser()
ap.add_argument('-s', '--source', type=str, 
    help="The source that will be retrieved.")
ap.add_argument('-d', '--data', type=str,
    help="The file source that contains what we're looking for.")
args = vars(ap.parse_args())

url = args['source']

weber = AutoWeber()
weber.loadHtml(url)
weber.addData('Test1')
weber.addData('Test2')

weber.deriveCommonStructure()