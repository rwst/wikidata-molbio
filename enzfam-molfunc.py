from sys import *
import csv

set_ef = set(l.rstrip() for l in stdin.readlines())

reader = csv.DictReader(open('ef.tab', 'r'), delimiter='\t')
efs = {}
for item in reader:
    ec = item.get('ec')
    lab = item.get('pLabel')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    if it in set_ef:
        continue
    git = efs.get(ec)
    if git is None:
        efs[ec] = [(lab, it)]
    else:
        git.append((lab, it))

reader = csv.DictReader(open('mf.tab', 'r'), delimiter='\t')
mfs = {}
for item in reader:
    ec = item.get('ec')
    lab = item.get('pLabel')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    git = mfs.get(ec)
    if git is None:
        mfs[ec] = [(lab, it)]
    else:
        git.append((lab, it))

for tup in efs.items():
    ec = tup[0]
    efval = tup[1]
    mfval = mfs.get(ec)
    if mfval is None:
        continue#print("http://www.wikidata.org/entity/{}".format(efval[0][1]))
    else:
        for ttup in efval:
            for mtup in mfval:
                print("{}\t{}\t{}\t{}".format(ttup[1], mtup[1], ttup[0], mtup[0]))
