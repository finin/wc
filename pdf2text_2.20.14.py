#! /usr/bin/python

""" convert all pdf files in source_dir to text and put in outdir by year"""

from subprocess import call
import os, sys


source_dir = "/home/websites/ebiquity/v2.1/_file_directory_/papers/"

def main(outdir="."):
    for line in open('year_paper.txt'):
        if not line or line[0] == '#':
            continue
        (year, paper) = line.split()
        year_path = os.path.join(outdir, year)
        if not os.path.exists(year_path):
            os.makedirs(year_path)
        if paper.endswith('.pdf'):
            in_path = os.path.join(source_dir, paper)
            out_path = os.path.join(year_path, paper + '.txt')
            print 'Converting', in_path, 'to', out_path
            call(['pdftotext', in_path, out_path])
        else:
            print 'Skipping', in_path
            
    

def main_old(indir, outdir):
    for file in os.listdir(indir):
        in_path = os.path.join(indir, file)
        if os.path.isfile(in_path) and file.endswith('.pdf'):
            out_path = os.path.join(outdir, file + '.txt')
            print 'Converting', in_path, 'to', out_path
            call(['pdftotext', in_path, out_path])
        else:
            print 'Skipping', in_path
    print 'done'

if __name__ == "__main__":
    outdir = './text'
    if len(sys.argv) > 2:
        print "USAGE: pdf2text outdir"
    elif len(sys.argv) == 1:
        outdir = sys.argv[1]
    main(outdir)
    
                                    

