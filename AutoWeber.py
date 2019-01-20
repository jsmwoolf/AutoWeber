from bs4 import BeautifulSoup, element
from urllib.request import urlopen
import re
import string, random, json

# Django's RE for determining a website
urlRE = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class AutoWeber():
    def __init__(self):
        self._html = None
        self._data = []
        self._htmlText = None
        self._url = None

    # Determine whether the url is a website.
    def _isWebsite(self, url):
        return urlRE.search(url) is not None
    
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

    def _getTag(self, line):
        insideTag = re.compile(r"<([^/>]*)>")
        return re.findall(insideTag, line)[0]

    def _getImmediateTags(self):
        results = []
        for entity in self._data:
            # Find first instance
            found = re.compile(r"<[^\/][^>]*>{}<\/[^>]*>".format(entity))
            tags = re.findall(found, self._htmlText)
            for tag in tags:
                nameTag = self._getTag(tag).split()
                results.append(self._html.find_all(nameTag, string=entity)[0])
        return results 

    def _generateHTMLOrderString(self, html):
        if type(html) == element.NavigableString:
            return ""
        result = html.name
        filteredChildren = [child for child in html.children if child != '\n']
        for child in filteredChildren:
            result += self._generateHTMLOrderString(child)
        return result

    def _generateStructure(self, html):
        struct = {'name': html[0].name}
        # Grab attributes
        if len(html[0].attrs) > 0:
            struct['attrs'] = {}
            if 'class' in html[0].attrs:
                #print(key)
                elements = {val for val in html[0].attrs['class']}
                for i in range(1, len(html)):
                    elements = elements.intersection({val for val in html[i].attrs['class']})
                struct['attrs']['class'] = list(elements)
        # Deal with children instances
        if len(list(html[0].children)) > 0:
            # Preparing child instances for looping and filtering
            children = [[child for child in html[i].children if child != '\n' and type(child) != element.NavigableString] for i in range(len(html))]
            children = [nonEmpty for nonEmpty in children if nonEmpty != []]
            # Check whether we still have children
            if len(children) > 0:
                struct["children"] = []
                for i in range(len(children[0])):
                    newLayer = [children[j][i] for j in range(len(html))]
                    struct["children"].append(self._generateStructure(newLayer))
        # Return structure
        return struct
            
    # Derive a common structure
    def _deriveCommonStructure(self):
        tags = self._getImmediateTags()
        if len(tags) == 0:
            raise Exception("No tags derived from data.")
        tagHeir = {}
        for tag in tags:
            tagHeir[tag] = list(tag.parents)
        i = 0
        finalStructStr = None
        structs = {}
        # Deduct the data into a common denominator.
        while finalStructStr == None:
            for key, val in tagHeir.items():
                orderStr = self._generateHTMLOrderString(val[i])
                if orderStr not in structs:
                    structs[orderStr] = []
                structs[orderStr].append(val[i])
                if len(structs[orderStr]) == len(tagHeir):
                    finalStructStr = orderStr
                    break
            i += 1
        structure = self._generateStructure(structs[finalStructStr])
        return structure

    def writeStructureToJson(self, filename):
        structure = self._deriveCommonStructure()
        fileExt = filename.find('.')
        if fileExt == -1:
            filename += ".json"
        elif filename[fileExt:] != '.json':
            filename = filename[:fileExt]
            filename += '.json'
        with open(filename, 'w') as output:
            json.dump(structure, output, indent = 4)