from AutoWeber import AutoWeber
import random

class BeautifulSoupWeber(AutoWeber):
    def __init__(self):
        super().__init__()
        self._file = None

    def _writeToFile(self, line):
        print(line, file=self._file)

    def _walkStructure(self, struct, soup):
        name = struct['name']
        variable = self._id_generator(random.randint(5, 15))
        self._writeToFile("  {} = {}.find_all(".format(variable, soup))
        self._writeToFile("    \"{}\",".format(name))
        if 'attrs' in struct:
            self._writeToFile("    attrs = {}".format(struct['attrs']))
        self._writeToFile("  )")
        if "children" in struct:
            for child in struct["children"]:
                self._walkStructure(child, variable)

    def generateScrapingCode(self, filename):
        structure = self._deriveCommonStructure()
        self._file = open(filename, "w")
        self._writeToFile("from bs4 import BeautifulSoup, element")
        self._writeToFile("")
        self._writeToFile("def doScrape(html):")
        self._walkStructure(structure, "html")
        self._writeToFile("doScrape(")
        self._writeToFile("  BeautifulSoup(")
        self._writeToFile("    open(")
        self._writeToFile("      \"{}\"".format(self._url))
        self._writeToFile("    ).read(),")
        self._writeToFile("    'html.parser'")
        self._writeToFile("  )")
        self._writeToFile(")")
        self._file.close()