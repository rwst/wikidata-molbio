from sys import *
import csv

reader = csv.DictReader(open('uniprot-wd.tab', 'r'), delimiter='\t')
unips = {}
dups = set()
for item in reader:
    uid = item.get('unip')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    git = unips.get(uid)
    if git is None or git == it:
        unips[uid] = it
    else:
        #print('more than one value: {} ({}, {})'.format(uid, git, it))
        dups.add(uid)
for k in dups:
    unips.pop(k)

uids = set(unips.keys())
full = set(l.rstrip() for l in stdin.readlines())
s = uids.difference(full)
print(len(uids))
print(len(s))
for uid in s:
    print(unips[uid.strip()])
