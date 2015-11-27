#! /usr/bin/python

""" convert all pdf files in indir to text and put in outdir by year"""

import subprocess
import os, sys
import MySQLdb

source_dir = "/home/websites/ebiquity/v2.1/_file_directory_/papers/"

query = "SELECT FROM_UNIXTIME(date, '%Y'), url FROM eb_publication as p, eb_publication_resource as r WHERE p.id = r.publication;"

def get_papers():
    try:
        conn = MySQLdb.Connection(db='ebwebsite', host='localhost', user='ebuser', passwd='ebpass20')
        cur = conn.cursor()
        cur.execute(query)
        return cur.fetchall()
    except:
        print "Unable to access ebwebsite database"
        return []

def main(outdir="."):
    for (year, paper) in get_papers():
        year_path = os.path.join(outdir, year)
        print 'Processing', paper, year
        if not os.path.exists(year_path):
            os.makedirs(year_path)
        if paper.endswith('.pdf'):
            in_path = os.path.join(source_dir, paper)
            out_path = os.path.join(year_path, paper + '.txt')
            print '  Converting %s to %s' % (in_path, out_path)

            try:
                subprocess.check_call(['pdftotext', '-enc', 'ASCII7', in_path, out_path])
            # except subprocess.CalledProcessError:
            except Exception as e:
                print '  pdftotext failed conversion:', str(e)
        else:
            print '  Skipping non-pdf', paper, year
            
if __name__ == "__main__":
    if len(sys.argv) > 2:
        print "USAGE: pdf2text outdir"
        sys.exit(1)
    elif len(sys.argv) == 2:
        outdir = sys.argv[1]
    else:
        outdir = './text'
    main(outdir)
    
                                    

