from sys import *

#s1 = set(open('wd-inst-of-gene', 'r').readlines())
s2 = set(open('wd-uniprot', 'r').readlines())
s3 = set(open('wd-refseqp', 'r').readlines())
#s4 = set(open('wd-ec-with-goid', 'r').readlines())
for i in s3.difference(s2):
    print('{}'.format(i.rstrip()))
