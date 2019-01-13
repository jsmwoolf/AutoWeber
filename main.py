import argparse
from BeautifulSoupWeber import BeautifulSoupWeber

ap = argparse.ArgumentParser()
ap.add_argument('-s', '--source', type=str, 
    help="The source that will be retrieved.")
ap.add_argument('-d', '--data', type=str,
    help="The input file source.")
ap.add_argument('-o', '--output', type=str,
    help="The output file source.")
args = vars(ap.parse_args())

url = args['source']
myFile = args['data']
output = args['output']

weber = BeautifulSoupWeber()
weber.loadHtml(url)
weber.loadDataFromFile(myFile)

weber.generateScrapingCode(output)