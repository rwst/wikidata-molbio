import pronto, six, csv
from sys import *

ont = pronto.Ontology('chebi.obo')
d = {}
for term in ont.terms.values():
    xref = term.other.get('xref')
    if xref is None:
        continue
    l = [i.split()[0] for i in xref if i[:4] == 'CAS:']
    if len(l) > 0:
        d[l[0]] = term.id
        #print('{}|{}'.format(l[0], term.id))

reader = csv.DictReader(open('cas-without-chebi.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    cas = item.get('cas')
    ch = d.get('CAS:'+cas)
    if ch is not None:
        print('{}|P683|"{}"|S248|Q69633402'.format(qit, ch[ch.find(':')+1:]))
