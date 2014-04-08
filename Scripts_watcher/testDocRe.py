__author__ = 'Luolin'
import urllib2
from bs4 import BeautifulSoup
import urllib
from snownlp import SnowNLP

soup = BeautifulSoup(urllib2.urlopen("http://bbs.tianya.cn/post-lookout-358741-1.shtml").read())
data = soup.find('meta',{'name':'author'})
db = soup.find("div")
data = data['content'].encode('utf-8')
author =  {'d':data}
author_enc = urllib.urlencode(author)[2:]
lead_div = soup.find('div',{"class":"atl-main"})
text = lead_div.find('div',{'class':'bbs-content clearfix'}).get_text().strip().encode('utf-8')+"\r\n"
#docs = soup.findAll('div',{'js_username':author_enc})
"""
for div in docs:
    text+= div.find('div',{'class':'bbs-content'}).get_text().strip().encode('utf-8')+"\r\n"
    """

text = unicode(text.decode('utf-8'))
s = SnowNLP(text)
for key in s.keywords(10):
    if len(key)>1:
        print key


