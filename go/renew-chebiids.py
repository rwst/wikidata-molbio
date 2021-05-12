
import pronto, six, csv
from sys import *

reader = csv.DictReader(open('chebi.tab', 'r'), delimiter='\t')
qs = {}
cs = {}
for item in reader:
    iturl = item.get('item')
    qit = iturl[iturl.rfind('/')+1:]
    chid = 'CHEBI:' + item.get('ch')
    qs[chid] = qit
    c = cs.get(qit)
    if c is None:
        cs[qit] = [chid]
    else:
        c.append(chid)

ont = pronto.Ontology('chebi.obo')
altids = {}
for term in ont.terms.values():
    alts = term.other.get('alt_id')
    if alts is None or len(alts) == 0:
        continue
    for alt in alts:
        altids[alt] = term.id

for q in cs.keys():
    alts = []
    coms = []
    alt_found = False
    for c in cs.get(q):
        newc = altids.get(c)
        if newc is None:
            continue
        alt_found = True
        nc = newc
        coms.append('-{}|P683|"{}"'.format(q, c[6:]))
    if alt_found:
        print('{}|P683|"{}"|S248|Q69633402'.format(q, nc[6:]))
        for c in coms:
            print(c)
