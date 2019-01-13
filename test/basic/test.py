from bs4 import BeautifulSoup, element

html = open('./test/basic/testGrouping.html').read()
soup = BeautifulSoup(html, 'html.parser')
tmp = soup.find_all('div')

for child in tmp[0].children:
    if type(child) == element.NavigableString:
        print("Is a string")
    else:
        print('Element')
        print(child.name)
