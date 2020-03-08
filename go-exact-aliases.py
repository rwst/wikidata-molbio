
import pronto, six, csv
from sys import *

reader = csv.DictReader(open('goid.tab', 'r'), delimiter='\t')
efs = {}
for item in reader:
    go = item.get('goid')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    goit = efs.get(it)
    if goit is None:
        efs[it] = go
    else:
        print('============= {}'.format(go))

def reduce(s): return "".join([c.lower() for c in s if c.isalnum()])

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
id_als = set()

count = 0
reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    al = item.get('al')
    goid = efs.get(it)
    if goid is None:
        continue
    term = ont.terms.get(goid)
    if term is None:
        #print(goid)
        continue
    if al == term.id:
        id_als.add(al)
        continue
    count = count + 1
    exact = False
    for s in term.synonyms:
        if reduce(s.desc) == reduce(al) and s.scope == 'EXACT':
            exact = True
            break
    if not exact:
        print('-{}|Aen|"{}"'.format(it, al))
print(count, file=stderr, flush=True)
