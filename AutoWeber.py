"""AutoWeber
Created by Joseph Woolf

This file contains a class that can derive an HTML structure based off what
the user provided for data references.  The JSON structure returned can be
written to file or used for other purposes, such as generating web scraping
code.
"""
from bs4 import BeautifulSoup, element
from urllib.request import urlopen
import re
import string
import random
import json

# Django's RE for determining a website
urlRE = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class AutoWeber():
    """A class for loading HTML, data, and generating JSON representations
    of the provided HTML code.

    Attributes
    ----------
    _html : BeautifulSoup Tag
        A BeautifulSoup representation of the HTML file.
    _data : list
        The list of data references for the class when generating the
        JSON strucutre.
    _htmlText : str
        Similar to _html, but is only a string representation
    _url : str
        The HTML url/file that is being used.

    Methods
    -------
    loadHtml(url)
        Loads the url provided by the user.
    loadDataFromFile(filename)
        Loads and adds data from the file.  
    addData(line)
        Adds user provided data to the data list.
    clearData()
        Deletes all the data from the object.
    writeStructureToJson(filename)
        Writes the JSON structure to file.
    """
    def __init__(self):
        self._html = None
        self._data = []
        self._htmlText = None
        self._url = None

    # Determine whether the url is a website.
    def _isWebsite(self, url):
        """Determines whether the provided url is a website.

        Parameters
        ----------
        url : str
            The url string for checking.

        Returns
        -------
        boolean
            Whether the url is a valid website.
        """
        return urlRE.search(url) is not None
    
    def loadHtml(self, url):
        """Loads the url provided by the user.

        Parameters
        ----------
        url : str
            The url string that'll be used for loading the html data

        Returns
        -------
        None
        """
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
        """Loads and adds data from the file.  
        
        Note that a line represents a separate data entry.

        Parameters
        ----------
        filename : str
            The filename to be opened and read.

        Returns
        -------
        None
        """
        lines = open(filename).read().split('\n')
        for line in lines:
            self.addData(line)

    # Adds data for analysis
    def addData(self, line):
        """Adds user provided data to the data list.

        Parameters
        ----------
        line : str
            The line of data to be added for the object.

        Returns
        -------
        None
        """
        self._data.append(line)
    
    # Clear all data
    def clearData(self):
        """Deletes all the data from the object.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self._data = []

    def _getTag(self, line):
        """Returns the tag name from the provided input.

        Parameters
        ----------
        line : str
            The string that contains an HTML tag.

        Returns
        -------
        The tag name from the regular expression.
        """
        insideTag = re.compile(r"<([^/>]*)>")
        return re.findall(insideTag, line)[0]

    def _getImmediateTags(self):
        """Using the data provided by the user, find the HTML elements 
        containing the string.

        Parameters
        ----------
        None

        Returns
        -------
        The list of HTML elements containing the data we were provided.
        """
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
        """Generate a string consisting of HTML tag names.

        Parameters
        ----------
        html : BeautifulSoup Tag or BeautifulSoup NavigableString
            The BeautifulSoup object containing the HTML data that we will
            generate the string with.

        Returns
        -------
        The string consisting of HTML tags.
        """
        if type(html) == element.NavigableString:
            return ""
        result = html.name
        filteredChildren = [child for child in html.children if child != '\n']
        for child in filteredChildren:
            result += self._generateHTMLOrderString(child)
        return result

    def _generateStructure(self, html):
        """Generate a JSON representation of the HTML code.

        Parameters
        ----------
        html : [BeautifulSoup Tag]
            A list of BeautifulSoup objects containing HTML instances 
            for generating

        Returns
        -------
        A dict/JSON representation of the HTML code.
        """
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
            children = [
                [
                    child for child in html[i].children if child != '\n' 
                    and type(child) != element.NavigableString
                ] 
                for i in range(len(html))
            ]
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
        """Determines the common structure and returns the JSON 
        representation of the HTML code based off of the data
        references provided by the user..

        Parameters
        ----------
        None

        Returns
        -------
        A dict/JSON representation of the HTML code.
        """
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
                # If the current parent level is greater than the amount of parents
                # found for the tag, move on to the next tag.
                if i >= len(val):
                    continue
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
        """Writes the JSON structure to file.

        Parameters
        ----------
        filename : str
            A string that references the file that will be written to.

        Returns
        -------
        None
        """
        structure = self._deriveCommonStructure()
        fileExt = filename.find('.')
        if fileExt == -1:
            filename += ".json"
        elif filename[fileExt:] != '.json':
            filename = filename[:fileExt]
            filename += '.json'
        with open(filename, 'w') as output:
            json.dump(structure, output, indent = 4)