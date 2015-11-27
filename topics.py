import os
import sys

old = set()
new = set()

f1 = os.path.join(sys.argv[1], 'tfidf.txt')
f2 = os.path.join(sys.argv[2], 'tfidf.txt')

if len(sys.argv) < 4:
    n = 20
else:
    n = int(sys.argv[3])

for i,line in enumerate(open(f1)):
    if i > n:
        break
    old.add(line.split()[0])

for i,line in enumerate(open(f2)):
    if i > n:
        break
    new.add(line.split()[0])

print 'OLD:',
for word in old.difference(new):
    print word,
print

print 'BOTH:',
for word in new.intersection(old):
    print word,
print

print 'NEW:',
for word in new.difference(old):
    print word,
print

    

    
    
