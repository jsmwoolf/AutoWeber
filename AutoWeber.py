from bs4 import BeautifulSoup, element
from urllib.request import urlopen
import re
import string, random

class AutoWeber():
    def __init__(self):
        self._html = None
        self._data = []
        self._htmlText = None
        self._url = None
        # The dictionary that dictates how the website should be parsed.
        self._options = {
            # Restricts the type of attributes that should be retrieved.
            'retrieve-attrs':[
                'class'
            ],
        }
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
            res = urlopen(url).read().decode('utf-8')
        else:
            res = open(url).read()

        # Load BeautifulSoup object for the webpage
        self._htmlText = res
        self._url = url
        #print(self._htmlText)
        self._html = BeautifulSoup(self._htmlText, 'html.parser')
        self._data = []

    def loadDataFromFile(self, filename):
        lines = open(filename).read().split('\n')
        for line in lines:
            self.addData(line)

    # Adds data for analysis
    def addData(self, data):
        self._data.append(data)
    
    # Clear all data
    def clearData(self):
        self._data = []

    def _isRetrievableAttr(self, attr):
        return attr in self._options['retrieve-attrs']

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

    def _walkTheTree(self, tag):
        struct = {}
        #print("{}, type={}".format(tag, type(tag)))
        children = [child for child in list(tag.children) if child != '\n' and type(child) != element.NavigableString]
        struct["name"] = tag.name
        if len(tag.attrs) > 0:
            struct["attrs"] = {}
            for key, val in tag.attrs.items():
                print(key)
                if self._isRetrievableAttr(key):
                    struct["attrs"][key] = val
        if len(children) > 0:
            struct["children"] = []
        for child in children:
            childStruct = self._walkTheTree(child)
            if struct["children"].count(childStruct) == 1:
                continue
            struct["children"].append(childStruct)
        return struct
        
    def _id_generator(self, size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        res = random.choice(string.ascii_uppercase + string.ascii_lowercase)
        print(res)
        return res + ''.join(random.choice(chars) for _ in range(size-1))

    # Derive a common structure
    def _deriveCommonStructure(self):
        tags = self._getImmediateTags()
        tagHeir = {}
        print(tags)
        for tag in tags:
            tagHeir[tag] = list(tag.parents)
        layers = set()
        i = 0
        # Deduct the data into a common denominator.
        while len(layers) != 1:
            layers = set()
            for key, val in tagHeir.items():
                newStr = BeautifulSoup(str(val[i]),'html.parser')
                layers = layers.union(set(newStr))
                print("Unioned layer: {}".format(layers))
            print("Current set: {}".format(layers))
            i += 1
        structure = self._walkTheTree(layers.pop())
        print("Final structure: {}".format(structure))
        return structure