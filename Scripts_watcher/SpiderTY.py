__author__ = 'Luolin'

import os
import urllib2
import re
import sys
from multiprocessing import Queue
from multiprocessing import Pool
from bs4 import BeautifulSoup
import threading

def store_doc_url(self,colum):
    """
    The methon is for store article url
    """
    first_flag = True
    while not self.doc_queue.full():
        print "loading...article's url"
        side = self.index_url+'/'+colum
        next_page = self.get_next_page(colum)
        soup = BeautifulSoup(urllib2.urlopen("http://"+side).read())
        #soup.find('table',{'class':'tab-bbs-list tab-bbs-list-2'}).find('a',{'target':'_blank'})["href"]
        a_tags = soup.find('table',{'class':'tab-bbs-list tab-bbs-list-2'}).findAll('a',title=re.compile(r".*"))

        while 1:
            for tag in a_tags:
                url = tag['href']
                title = tag.contents[0].strip()
                """store article's url and title to file
                with open(self.folder+'/'+file_name.replace('\r', '').replace('\n', ''), "ab") as fp:
                    fp.write(url+'\r\n')
                    fp.write(title+'\r\n')
                """
                self.doc_queue.put({(url,title):side})
            if first_flag==True:
                first_flag = False
            else:
                next_page = self.get_next_page(next_page)
            #test for store to the file  !!!!!!!!!the file must be changed
            print "writing......"
            with open("testStore","ab") as fp:
                fp.write("----------------side:%s--------------\r\n" %side)
                while not self.doc_queue.empty():
                    arti_url,arti_title = self.doc_queue.get().keys()[0]
                    print arti_url,arti_title
                    fp.write("url:%s,title:%s"%(arti_url.encode("utf-8"),arti_title.encode("utf-8")))
                    fp.write("\r\n")

            if not next_page or self.doc_queue.qsize()>self.max_doc_num:
                #self.end()
                exit(1)
            else:
                next_page_url = self.index_url+next_page
                side = next_page_url
                soup = BeautifulSoup(urllib2.urlopen("http://"+side).read())
                a_tags = soup.find('table',{'class':'tab-bbs-list tab-bbs-list-2'}).findAll('a',title=re.compile(r".*"))
                continue

class Spider(object):

    folder = 'store'
    thread_count = 10
    max_doc_num = 0
    queue = Queue()
    doc_queue = Queue()
    is_end = False

    def __init__(self, folder = 'store',max_doc_num = 0):
        self.folder = folder
        self.max_doc_num = max_doc_num
        self.doc_queue = Queue(max_doc_num)
        if not os.path.isdir(folder):
            os.mkdir(folder)

    def requese(self,url):
        """
        Use `GET` method to access to the target url and return the HTML code.
        param:
            url: The target url, without the prefix `http://`.
        return:
            text: The HTML code of the target url.
        """
        try:
            return urllib2.urlopen("http://%s" %url)
        except urllib2.URLError:
            pass



    def createPool(self, target,iterable=[] ):
        """
        Create Pool for target
        """
        if not target:
            return
        self.thread_count = self.thread_count if self.thread_count else 1
        pool = Pool(self.thread_count)
        pool.map(target,iterable,chunksize=1)
        pool.join()

    def createThread(self,target,args):
        """
        Create Thread for Targe
        """
        if not target:
            return
        self.thread_count = self.thread_count if self.thread_count else 1
        for i in range(self.thread_count):
            t = threading.Thread(target=target,args=args)
            print "thread%d loading...." %i
            t.start()
            print "thread%d success..." %i


    def end(self):
        self.is_end = True
        print '-' * 79
        print 'Please wait the thread end, and all done, have fun :)'
        sys.exit()

class TySpider(Spider):
    index_url = "bbs.tianya.cn"
    columns = ['list-free-1.shtml', 'list-law-1.shtml', 'list-funstribe-1.shtml', 'list-1095-1.shtml', 'list-university-1.shtml',
               'list-828-1.shtml', 'list-develop-1.shtml', 'list-837-1.shtml', 'list-consumer-1.shtml', 'list-culture-1.shtml',
               'list-665-1.shtml', 'list-feeling-1.shtml', 'list-no11-1.shtml', 'list-play-1.shtml', 'list-no05-1.shtml',
               'list-books-1.shtml', 'list-no16-1.shtml', 'list-poem-1.shtml', 'list-no02-1.shtml', 'list-169-1.shtml',
               'list-no17-1.shtml', 'list-16-1.shtml', 'list-house-1.shtml', 'list-stocks-1.shtml', 'list-no22-1.shtml',
               'list-no20-1.shtml', 'list-enterprise-1.shtml', 'list-no100-1.shtml', 'list-cars-1.shtml', 'list-944-1.shtml',
               'list-itinfo-1.shtml', 'list-516-1.shtml', 'list-numtechnoloy-1.shtml', 'list-it-1.shtml', 'list-no06-1.shtml',
               'list-news-1.shtml', 'list-worldlook-1.shtml', 'list-1089-1.shtml', 'list-20-1.shtml', 'list-no01-1.shtml',
               'list-fans-1.shtml', 'list-sport-1.shtml', 'list-basketball-1.shtml', 'list-travel-1.shtml', 'list-1092-1.shtml',
               'list-685-1.shtml', 'list-96-1.shtml', 'list-98-1.shtml', 'list-female-1.shtml', 'list-outseachina-1.shtml',
               'list-100-1.shtml', 'list-spirit-1.shtml', 'list-motss-1.shtml', 'list-water-1.shtml', 'list-funinfo-1.shtml',
               'list-tianyamyself-1.shtml','list-filmtv-1.shtml', 'list-music-1.shtml', 'list-14-1.shtml', 'list-no04-1.shtml',
               'list-tianyaphoto-1.shtml', 'list-english-1.shtml', 'list-936-1.shtml', 'list-1013-1.shtml', 'list-lookout-1.shtml']
    is_end = False


    def __init__(self, func, thread_num = 5, folder="store", max_doc_num=10 ):
        self.thread_count = thread_num
        self.store_doc_url = func
        Spider.__init__(self, folder="stroe", max_doc_num=max_doc_num)

    def get_next_page(self,colum):
        """
        return the next page's url
        """
        if self.queue.full():
            return
        soup = BeautifulSoup(urllib2.urlopen("http://"+self.index_url+"/"+colum).read())
        next_page_url = soup.find('div',{'class':'links'}).find('a',{'rel':'nofollow'})['href']
        return next_page_url



    def end(self):
        return True

    def catchKeywords(self):
        """
        The methon is for deal with keywords in Tianya side
        """
        print "loading"
        return True

if __name__=="__main__":
    ts = TySpider(store_doc_url,max_doc_num=1000)
    ts.createPool(target=ts.store_doc_url,iterable=ts.columns)