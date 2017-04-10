import urllib
from xml.dom import minidom

xml = urllib.urlopen('http://www.nytimes.com/services/xml/rss/nyt/GlobalHome.xml').read()
p = minidom.parseString(xml)
item = p.getElementsByTagName('item')
print item
print len(item)