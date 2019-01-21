# AutoWeber
A Proof of Concept (Pof) on an auto adapting web scraper.

## Purpose 
AutoWeber determines the common structure of an HTML webpage using data provided by the user for reference.  AutoWeber will then derive the common structure and generate a JSON representation of the structure.  That structure can then be used for generate web scraping code.  At the moment, there is no implementation of generating web scraping code.

## Running AutoWeber
In order to run AutoWeber, you'll need to install BeautifulSoup.  You can do this using pip:

```bash
pip install beautifulsoup4
```