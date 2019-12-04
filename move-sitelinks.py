import csv
from sys import *

reader = csv.DictReader(open('genes-wikipedia.tab', 'r'), delimiter='\t')
gqs = {}
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    lang = item.get('lang')
    lemma = item.get('lemma')
    d = gqs.get(qit)
    if d is None:
        d = {}
        d[lang] = lemma
        gqs[qit] = d
    else:
        d[lang] = lemma

reader = csv.DictReader(open('proteins-wikipedia.tab', 'r'), delimiter='\t')
pqs = {}
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    lang = item.get('lang')
    lemma = item.get('lemma')
    d = pqs.get(qit)
    if d is None:
        d = {}
        d[lang] = lemma
        pqs[qit] = d
    else:
        d[lang] = lemma
"""
its = set()
dits = set()
reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('g')
    git = iturl[iturl.rfind('/')+1:]
    if git in its:
        dits.add(git)
    else:
        its.add(git)

reader = csv.DictReader(open('tt.tab', 'r'), delimiter='\t')
labs = {}
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    lab = item.get('pLabel')
    uni = item.get('u')
    labs[qit] = (lab,uni)

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('g')
    git = iturl[iturl.rfind('/')+1:]
    if git not in dits:
        continue
    iturl = item.get('p')
    pit = iturl[iturl.rfind('/')+1:]
    pl = item.get('pLabel')
    lem = item.get('lemma')
    print('"","{}","{}","{}","{}"'.format(lem,labs.get(pit),git,pit))
"""
reader = csv.DictReader(open('ttt.csv', 'r'), delimiter=',')
for item in reader:
    git = item.get('G')
    pit = item.get('P')
    lem = item.get('Name')
    g = gqs.get(git)
    p = pqs.get(pit)
    l = []
    if g is None:
        continue
    for glang in g.keys():
        if p is None or p.get(glang) is None:
            l.append((glang, g.get(glang)))
    for link in l:
        print('-{}|S{}wiki|""'.format(git, link[0]))
    print('{}|Lde|"{}"'.format(pit,lem))
    print('{}|Dde|"Protein in Homo sapiens"'.format(pit))
    for link in l:
        print('{}|S{}wiki|"{}"'.format(pit, link[0], link[1]))
