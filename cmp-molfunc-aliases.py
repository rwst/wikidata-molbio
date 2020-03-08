
import pronto, six, csv
from sys import *

reader = csv.DictReader(open('goid.tab', 'r'), delimiter='\t')
efs = {}
for item in reader:
    go = item.get('goid')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    git = efs.get(go)
    if git is None:
        efs[go] = it
    else:
        print('============= {}'.format(go))

def reduce(s): return "".join([c.lower() for c in s if c.isalnum()])   

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
odict = {}

for term in ont.terms.values():
    goid = term.id
    if goid[:3] != 'GO:':
        continue
    goit = efs.get(goid)
    if goit is None:
        continue
    ns = term.other.get('namespace')
    if ns is None:
        continue
    if ns[0] != 'molecular_function':
        continue
    odict[reduce(term.name).replace('activity', '')] = goit
    for s in term.synonyms:
        if s.scope == 'EXACT':
            odict[reduce(s.desc).replace('activity', '')] = goit

reader = csv.DictReader(open('enzfam+func.tab', 'r'), delimiter='\t')
efus = {}
for item in reader:
    lab = item.get('pLabel')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    furl = item.get('func')
    if furl is None or len(furl) == 0:
        fit = None
    else:
        fit = furl[furl.rfind('/')+1:]
    m = odict.get(reduce(lab))
    if m is None:
        if fit is None:
            continue
        else:
            print('{}|P680|{}|P4390|Q39894595|S248|Q77546004'.format(it, fit))
    else:
        print('{}|P680|{}|P4390|Q39893449|S248|Q77546004'.format(it, m))

