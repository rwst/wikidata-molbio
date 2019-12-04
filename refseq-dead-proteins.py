from sys import *
import csv

reader = csv.DictReader(open('refseqp-wd.tab', 'r'), delimiter='\t')
refs = {}
for item in reader:
    rid = item.get('refseq')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    git = refs.get(rid)
    if git is None:
        refs[rid] = [it]
    else:
        git.append(it)

full = set(l.rstrip() for l in stdin.readlines())
for rid in refs.keys():
    if rid in full:
        for it in refs.get(rid):
            print('{} {}'.format(it, rid))
