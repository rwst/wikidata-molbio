from sys import *
import csv

reader = csv.DictReader(open('refseqp-wd.tab', 'r'), delimiter='\t')
refs = {}
dups = set()
for item in reader:
    uid = item.get('refseq')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    git = refs.get(uid)
    if git is None or git == it:
        refs[it] = uid
    else:
        #print('more than one value: {} ({}, {})'.format(uid, git, it))
        dups.add(it)
for k in dups:
    refs.pop(k)

reader = csv.DictReader(open('uniprot-refseq.tab', 'r'), delimiter='\t')
unips = {}
dups = set()
for item in reader:
    uid = item.get('uniprot')
    if '-' in uid:
        continue
    ref = item.get('refseq')
    if ref.find('.') > -1:
        ref = ref[:ref.find('.')]
    git = unips.get(ref)
    if git is None or git == it:
        unips[ref] = uid
    else:
        #print('more than one value: {} ({}, {})'.format(uid, git, it))
        dups.add(ref)
for k in dups:
    unips.pop(k)

#uids = set(unips.keys())
ids = set(l.rstrip() for l in open('wd-refseq-without-uniprot', 'r').readlines())
#s = uids.difference(full)
#print(len(uids))
#print(len(s))
for it in ids:
    r = refs.get(it)
    if r is not None:
        u = unips.get(refs[it])
        if u is not None:
            print('{}|P352|"{}"'.format(it, u))
