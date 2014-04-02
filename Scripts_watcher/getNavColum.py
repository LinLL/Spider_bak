__author__ = 'Luolin'

import re
list = []
with open("navigation","r") as fp:
    for line in fp.readlines():
         s = re.search(r'href="/.*">',line)
         if  not s==None:
            list.append(s.group()[7:-2])

print list