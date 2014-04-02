#-*- coding: utf-8 -*-
import re
import os
import sys
import getopt
import urllib2
import threading
from Queue import Queue
from BeautifulSoup import BeautifulSoup


class ImageCrawler(object):

    folder = 'pics'
    max_img_num = 0
    thread_count = 10
    queue = Queue()
    image_queue = Queue()

    def __init__(self, folder='pics', max_img_num=0):
        self.folder = folder
        self.max_img_num = max_img_num
        self.image_queue = Queue(maxsize=max_img_num)
        if not os.path.isdir(folder):
            os.mkdir(folder)

    def request(self, url):
        """
        Use `GET` method to access to the target url and return the HTML code.
        param:
            url: The target url, without the prefix `http://`.
        return:
            text: The HTML code of the target url.
        """
        try:
            return urllib2.urlopen('http://%s' % url)
        except urllib2.URLError:
            pass

    def download(self, uri, file_name=''):
        print 'Downloading: %s ...' % uri
        with open(self.folder+'/'+file_name.replace('\r', '').replace('\n', ''), "wb") as fp:
            response = self.request(uri.replace('http://', ''))
            if response:
                fp.write(response.read())

    def create_thread(self, target=None):
        """
        Create the new thread for download images.
        """
        if not target:
            return
        self.thread_count = self.thread_count if self.thread_count else 1
        for i in range(0, self.thread_count):
            print 'Threading %d Starting ...' % (i+1)
            threading.Thread(target=target).start()


class MMCrawler(ImageCrawler):

    columns = ['qingliang', 'jingyan', 'bagua', 'suren', 'picbest/cars', 'picbest/Lolita']
    is_end = False
    index_page = '/index.html'
    index_url = 'www.22mm.cc'
    columns_url = 'www.22mm.cc/mm/'
    match_img_url = re.compile('arrayImg\[\d+\]="([\w\W]+?)";')

    def __init__(self, folder='pics', max_img_num=0, thread_count=10):
        self.thread_count = thread_count
        self.lock = threading.Lock()
        super(MMCrawler, self).__init__(folder=folder, max_img_num=max_img_num)

    def get_next_page(self, column):
        """
        Return the next page's url
        param:
            column: The name of the column.
        return:
            text: Return the next page's url
        """
        next_page_link = BeautifulSoup(self.request(self.columns_url+column).read()).find(
            'div', {'class': 'ShowPage'}).findAll('a')[-1]
        if next_page_link.contents[0] == '>':
            return dict(next_page_link.attrs)['href']
        else:
            return ''

    def get_img_queue(self):
        """
        Get the images detail urls and push it to the `queue`.
        """
        page = self.index_page
        while not self.image_queue.full():
            for column in self.columns:
                while not page == '/':
                    print 'Page:',self.columns_url+column+page
                    soup = BeautifulSoup(self.request(self.columns_url+column+page).read())
                    uls = soup.findAll('ul', {'class': 'pic'})
                    for ul in uls:
                        for li in ul.findAll('li'):
                            self.queue.put(dict(li.a.attrs)['href'])
                    page = '/' + self.get_next_page(column+page)
                    if self.max_img_num == self.image_queue.qsize() and self.max_img_num:
                        self.end()
                page = self.index_page
            break
        self.end()

    def get_image_url(self):
        """
        Get the image's uri, then download it.
        This method needs to be called by a thread.
        """
        list_url = self.queue.get()
        page_code = self.request(self.index_url+list_url).read()
        total = BeautifulSoup(page_code).find('strong', {'class': 'diblcok'}).contents[1].strip('/')
        # Get the last page URL

        response = self.request(self.index_url+'.'.join(list_url.split('.')[:-1])+'-%s.html' % total).read()
        img_list = self.match_img_url.findall(response)
        # Get the images URL

        for img in img_list:
            if self.lock.acquire():
                if self.is_end:
                    self.lock.release()
                    return
                if not self.image_queue.full():
                    self.image_queue.put(img)
                    self.lock.release()
                    self.download(img.replace('big', 'pic'), '_'.join(img.split('/')[-3:]))
                    # The true url of the image which `big` should be replaced to `pic`
                else:
                    self.lock.release()
                    return
        self.get_image_url()

    def create_thread(self, target=None):
        """
        Create the new thread for download images.
        """
        self.thread_count = self.thread_count if self.thread_count else 1
        for i in range(0, self.thread_count):
            print 'Threading %d Starting ...' % (i+1)
            threading.Thread(target=target).start()

    def start(self):
        """
        Start the crawler.
        """
        print '** MM Crawler **'
        user_input = raw_input('Strat now?(y/n):')
        if user_input == 'y':
        	self.create_thread(self.get_image_url)
        	self.get_img_queue()
        else:
        	self.end()

    def end(self):
        self.is_end = True
        print '-' * 79
        print 'Please wait the thread end, and all done, have fun :)'
        sys.exit()


def usage():
    print u'\nMM Crawler - 一个抓取 www.22mm.cc 的美女图片的脚本。\n'
    print u'帮助:'
    print u'-h               打印帮助文本。'
    print u'-n [num]         指定线程数，默认为10。'
    print u'-l [num]         指定抓取图片最大数量，默认(0)不限制。'
    print u'-o directory     指定图片存放目录。\n'
    print u'包依赖:'
    print u'BeautifulSoup    v3.2.0'
    sys.exit()

def parser_param():
    folder, thread_count, max_img_count = 'pics', 10, 0  # Default value
    try:
        options, args = getopt.getopt(sys.argv[1:], "ho:l:n:")
    except getopt.GetoptError:
        usage()
    for name, value in options:
        if name == "-h":
            usage()
        if name == "-o":
            folder = value
        if name == "-l":
            try:
                max_img_count = int(value)
            except ValueError:
                usage()
        if name == "-n":
            try:
                thread_count = int(value)
            except ValueError:
                usage()
    mm_crawler = MMCrawler(folder=folder, max_img_num=max_img_count, thread_count=thread_count)
    mm_crawler.start()


if __name__ == '__main__':
    parser_param()