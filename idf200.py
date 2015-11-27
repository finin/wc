#! /usr/bin/pyton

import os, sys, inspect, gzip

def execution_path(filename):
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), filename)

idf_dict = {}

default = 17.347363

for line in gzip.open(execution_path('e1.txt')):
    try:
        word, idf = line.split()
    except:
        print line
    idf_dict[word] = float(idf)

def idf(word):
    return idf_dict.get(word,default)






  
  
