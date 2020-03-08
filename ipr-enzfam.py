import pronto, six, csv
from sys import *

fams = set()
reader = csv.DictReader(open('interpro-entries.tab', 'r'), delimiter='\t')
for item in reader:
    ipr = item.get('ENTRY_AC')
    type = item.get('ENTRY_TYPE')
    if type == 'Family':
        fams.add(ipr)

enzs = {}
reader = csv.DictReader(open('wd-ipr.tab', 'r'), delimiter='\t')
for item in reader:
    ipr = item.get('ipr')
    if ipr in fams:
        iturl = item.get('p')
        qit = iturl[iturl.rfind('/')+1:]
        lab = item.get('pLabel')
        if enzs.get(ipr) is not None:
            print(ipr)
            exit()
        enzs[ipr] = (qit, lab)

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
cat = ont.terms.get('GO:0003824') # catalytic

def walk(ont, parents, goid):
    ps = ont.terms.get(goid).other.get('is_a')
    if ps is not None:
        for p in ps:
            parents.add(p)
            walk(ont, parents, p)

for l in open('interpro2go', 'r').readlines():
    if l[:9] == 'InterPro:':
        ipr = l[9:18]
        if ipr in fams:
            go = l.rstrip().split(sep='; ')[-1]
            term = ont.terms.get(go)
            parents = set()
            walk(ont, parents, go)
            if cat.id in parents:
                print('{}|{}: {}'.format(ipr, enzs.get(ipr), (go, term.name)))
