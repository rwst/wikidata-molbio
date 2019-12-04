from sys import *
import csv

reader = csv.DictReader(open('uniprot-wd.tab', 'r'), delimiter='\t')
unips = {}
dups = set()
for item in reader:
    uid = item.get('unip')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    git = unips.get(it)
    if git is None or git == uid:
        unips[it] = uid
    else:
        #print('more than one value: {} ({}, {})'.format(uid, git, it))
        dups.add(it)
for k in dups:
    unips.pop(k)

ids = set(l.rstrip() for l in open('t', 'r').readlines())
dels = set(l.rstrip() for l in open('uniprot-sp+tr-delac', 'r').readlines())
for it in ids:
    uid = unips.get(it)
    if uid is not None:
        if uid in dels:
            print(it)
            #print('{}|P31|Q66826848|S248|Q905695|S813|+2019-08-30T00:00:00Z/11|S352|"{}"'.format(it.rstrip(), uid))
            #print('-{}|P352|"{}"'.format(it.rstrip(), uid))
