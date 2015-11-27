import os
import sys
# from collections import defaultdict

max = 20
dir = sys.argv[1]
years = sys.argv[2:]

# ranks = defaultdict(lambda : defaultdict(int))
ranks = {}

def write(s):
    sys.stdout.write(s)
    
for year in years:
    f = os.path.join(dir, year, 'tfidf.txt')
    for rank,line in enumerate(open(f)):
        if rank >= max:
            break
        word, score = line.split()
        # ranks[word][year] = rank
        if word not in ranks: ranks[word] = {}
        ranks[word][year] = max - rank

for word in ranks.keys():
    write(word)
    for year in years:
        write("\t%s" % ranks[word].get(year,0))
    write("\n")
    
