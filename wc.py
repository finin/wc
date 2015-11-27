"""
Compute tdifd models for directories of text files.

  python wc.py [DIR]

recursively walks the directory DIR (defaults to .) and processes each
file whose name ends with '.txt'.  It recursively calls itself for any
subdiectory encountered.

For each directory, it writes two files: tfidf will contain a sorted
list of all terms and their normalized tfidf score, term_count is the
total number of terms encountered.

Words in the files in stop_words_files are ignored as are words W for
which good(W) is false.

Words are normalized by removing puncuation.

"""

import os
import sys
import argparse
import re
import subprocess
from operator import itemgetter
from collections import defaultdict

# we use the lematizer from NLTK
from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()

# some local lemma data
mylemma = {'datasets':'dataset','modelling':'model','modeling':'model','computing':'compute','computational':'compute', \
           'ontologies':'ontology','blogger':'blog', 'blogging':'blog', 'blogs':'blog', 'performatives':'performative', \
           'parsing':'parse', 'parses':'parse','classifier':'classify','classifies':'classify', 'reproduction':'reproduce', \
           'reproduced':'reproduce', 'smartphones':'smartphone', 'knowledge-based':'knowledge-base', \
           'knowledge-bases':'knowledge-base','kb':'knowledge-base','kbs':'knowledge-base', 'db':'database', 'databases':'database', \
           'tweets':'tweet', 'semantics':'semantic', 'classification':'classify', 'urls':'url', 'uris':'uri', 'clusters':'cluster', \
           'clustering':'cluster', 'svns':'svn', 'learning':'learn','reasoner':'reason','reasoning':'reason'}

# idf data from Paul McNamee from newswire
from idf200 import idf, idf_dict

pdftotext = '/usr/bin/pdftotext'

# from string import punctuation
punctuation = """'!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'"""

skip_oov = False

default_number_of_words = 0

dig_or_punct = "0123456789" + punctuation

text_dir = '.'

# remember good words
goodcache = {}

# minimum number of term counts to consider in final output
min_tf = 0

# sets of words we want to ignore (stop words) or not normalize (whitelist)

blacklist = set()
whitelist = set()

stop_words_files = ['general_stop_words.txt', 'local_stop_words.txt']
white_list_files =['whitelist.txt']

def load_word_lists():
    # the  word list file should be a file of stop words, one to a line
    for f in white_list_files:
        for line in open(f):
            for w in line.split():
                whitelist.add(w.lower())
    for f in stop_words_files:
        for line in open(f):
            for w in line.split():
                blacklist.add(normalize(w))



def compute_tfidf_file(f, n=0):
    """ Compute tfidf data for a single file, write results to 
        tfidf and toal term count to term_count"""
    tf_dict = defaultdict(int)
    if f.endswith('.txt'):
        tf_dict = process_file(f, open(f))
    elif f.endswith('.pdf'):
        proc = subprocess.Popen([pdftotext, f, '-'], stdout=subprocess.PIPE)
        tf_dict = process_file(f, iter(proc.stdout.readline,''))
    elif f.endswith('doc') or f.endswith('docx'):
        print 'Can not yet handle MS Word files:', f
        return
    else:
        print 'Unknown file type:', f
        return
    # term_count, tf_dict = tf2tfidf(tf_dict)
    # terms = sorted(tf_dict.iteritems(), key=itemgetter(1), reverse=True)
    # if n > 0:
    #     terms = terms[:n]
    # for w_n in terms:
    #     if w_n[1] > 0.0:
    #         sys.stdout.write("%s\t%9.9f\n" % w_n)

def compute_tfidf_dir(directory, n=0):
    """ Compute tfidf data for all files in directory then write data
        to tfidf and total term count to term_count"""
    # tf_dict = defaultdict(int)
    # tf_dict = process_directory(directory, tf_dict)
    term_count, tf_dict = tf2tfidf(tf_dict)
    out = open(os.path.join(directory, 'tfidf'), 'w')
    terms = sorted(tf_dict.iteritems(), key=itemgetter(1), reverse=True)
    if n > 0:
        terms = terms[:n]
    for w_n in terms:
        if w_n[1] > 0.0:        
            out.write("%s\t%9.9f\n" % w_n)
    out.close()
    out2 = open(os.path.join(directory, 'term_count'), 'w')
    out2.write(str(term_count))
    out2.close()

def write_tfidf_dir(directory, tf_dict, n=0):
    """ Compute tfidf data for all files in directory then write data
        to tfidf and total term count to term_count"""
    term_count, tf_dict = tf2tfidf(tf_dict)
    out = open(os.path.join(directory, 'tfidf'), 'w')
    terms = sorted(tf_dict.iteritems(), key=itemgetter(1), reverse=True)
    if n > 0:
        terms = terms[:n]
    for w_n in terms:
        if w_n[1] > 0.0:
            out.write("%s\t%9.9f\n" % w_n)
    out.close()
    out2 = open(os.path.join(directory, 'term_count'), 'w')
    out2.write(str(term_count))
    out2.close()

def write_tfidf_file(path, tf_dict, n=0):
    """ Compute tfidf data for all files in directory then write data
        to tfidf and total term count to term_count"""
    term_count, tf_dict = tf2tfidf(tf_dict)
    terms = sorted(tf_dict.iteritems(), key=itemgetter(1), reverse=True)
    if n > 0:
        terms = terms[:n]
    out = open(path + '.tfidf', 'w')
    for w_n in terms:
        if w_n[1] > 0.0:        
            out.write("%s\t%9.9f\n" % w_n)
    out.close()
    out2 = open(path + '.term_count', 'w')
    out2.write(str(term_count))
    out2.close()


def process_directory(directory, n=0):
    # add a document for each file in the subtree under directory
    tf_dict = defaultdict(int)
    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if os.path.isfile(path):
            if  path.endswith('.txt'):
                tf_dict = combine_tf_dicts(tf_dict, process_file(path, open(path)))
        else:
            tf_dict = combine_tf_dicts(tf_dict, process_directory(path))
    write_tfidf_dir(directory, tf_dict)
    return tf_dict

def process_file(filename, file, n=0):
    """ tests words in file, which can be a path or a file object, and update tf dictionary. """
    tf_dict = defaultdict(int)
    for line in file:
        for w in line.split():
            w = lemma(w)
            if good(w):
                tf_dict[w] += 1
    write_tfidf_file(filename, tf_dict)
    return tf_dict
    file.close()

def lemma(w):
    w = normalize(w)
    if w in mylemma:
        return mylemma[w]
    else:
        return lmtzr.lemmatize(w)
    
# a regex for words we want to ignore
rebad = re.compile("(\d+.*)|(.*\d\d.*)|([neouyiax]+$)")


def good(w):
    """Return True if word w is worth indexing"""
    if w not in goodcache:
        goodcache[w] = len(w) > 2 and \
                       w not in blacklist and \
                       (w in whitelist or \
                        (not pdfcrap(w) and \
                         not rebad.match(w) and \
                         (w in idf_dict or \
                          (not skip_oov and \
                           not_all_dig_or_punct(w) and \
                           not w.startswith('http') and \
                           not w.startswith('https') and \
                           not w.startswith('www') and \
                           is_ascii(w)))))
    return goodcache[w]
    

def oov(w):
    return not ( (w in whitelist) or w in idf_dict)

def is_ascii(s):
    """ Returns True if every character in string s is an ascii character. """
    for c in s:
        if ord(c) > 127:
            return False
    return True

# a regular expression to match a puntuation character.  What counts
# as a punctuation character is any charactr in string.punctuation.
repunct = re.compile('[%s]' % re.escape(punctuation))

def normalize(word):
    """normalize(W) returns W after deleting punctuation characters
    (if not in whitelist), converting to lower case and striping off
    any leading and training whitespace characters."""
    word = word.lower().strip()
    if word in whitelist:
        return word
    else:
        return repunct.sub('', word)
    

def not_all_dig_or_punct(s):
    """Returns True iff string s has at least one character that is not
    a digit."""
    for c in s:
        if c not in dig_or_punct:
            return True
    return False

def top_words(n=200):
    """Returns a list of N words in the collection that have highest
    tfidf scores."""
    # sort document's words by their tfidf scores
    words = sorted(tf_dict.iteritems(), key=itemgetter(1), reverse=True)
    # return a list of the last n words (i.e., those with highest
    # scores after sorting)
    return words[:n]


def combine_tf_dicts(tfd1, tfd2):
    """ adds values from tfd2 to tfd1 and returns tfd1 """
    for k in tfd1.keys():
        tfd1[k] = tfd1[k] + tfd2[k]
    for k in tfd2.keys():
        if k not in tfd1:
            tfd1[k] = tfd2[k]
    return tfd1

def tf2tfidf(tf_dict):
    """ Given a term frequence doctionary, converts it to a tf_idf
      dictionary.  Returns the totle number of terms and the tf_idf
      version of the dictionary """
    # compute the total number of terms
    term_count = sum(tf for tf in tf_dict.values())
    tcf = float(term_count)
    # print 'Term_count', term_count
    for word in tf_dict.keys():
        if tf_dict[word] < min_tf:
            tf_dict[word] = 0
        else:
            tf_dict[word] = (100.0 * float(tf_dict[word]) / tcf) * idf(word)
    return term_count, tf_dict
    

def main(dir_or_file, n=default_number_of_words):
    if os.path.isfile(dir_or_file):
        process_file(dir_or_file, open(dir_or_file), n)
    elif os.path.isdir(dir_or_file):
        process_directory(dir_or_file, n)
    else:
        print 'Argument should be a file or directory:', dir_or_file
        sys.exit(1)
    #for w_n in top_words(n):
    #    print "%s:%f" % w_n

def pdfcrap(w):
    return len(w) < 5 and oov(w)
    
load_word_lists()

# if called as a script, execute main()

if __name__ == '__main__':
        p = argparse.ArgumentParser()
        p.add_argument('directory', help="directory with .txt files", nargs='?', default='.')
        p.add_argument("nwords", help="maximum number of words to keep in tfidf list",  nargs='?', default=0, type=int)
        p.add_argument("-nooov", help="do not include OOV words",  action='store_true')
        a = p.parse_args()
        main(a.directory, a.nwords)
