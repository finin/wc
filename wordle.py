import math
import argparse

# if called as a script, execute main()

def main(infile, n):
    for line in open(infile):
        word, score = line.split()
        score = float(score) ** (2.0/3.0)
        print "%s:%s" % (word,score)
        n = n - 1
        if n < 1:
            break
        

if __name__ == '__main__':
        p = argparse.ArgumentParser()
        p.add_argument('infile', help="tfidf file")
        p.add_argument("nwords", help="maximum number of words to keep in tfidf list",  nargs='?', default=200, type=int)
        a = p.parse_args()
        main(a.infile, a.nwords)
