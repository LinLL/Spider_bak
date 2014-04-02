__author__ = 'Luolin'
from threading import Thread,Condition
import random
import time


class testCon():
    con = Condition()
    product = None
    

    def produce(self,canshu):
        print canshu
        if self.con.acquire():
            while True:
                if self.product is None:
                    print "produce...."
                    self.product = random.random()
                    print "produce successed"+str(self.product)
                    self.con.notify()

                self.con.wait()
                time.sleep(1)

    def consume(self):
        if self.con.acquire():
            while True:
                if self.product is not None:
                    print "consuming...."
                    print "consume successed"+str(self.product)
                    self.product = None
                    self.con.notify()

                self.con.wait()
                time.sleep(1)

if __name__=="__main__":
    t = testCon()
    xiaohong ="luolin"
    t1 = Thread(target=t.produce,args=(xiaohong,))
    t2 = Thread(target=t.consume)
    t1.start()
    t2.start()
