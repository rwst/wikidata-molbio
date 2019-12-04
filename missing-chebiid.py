import pronto, six, csv
from sys import *

ont = pronto.Ontology('chebi.obo')
d = {}
for term in ont.terms.values():
    xref = term.other.get('property_value')
    if xref is None:
        continue
    l = [i.split()[1] for i in xref if i[:45] == 'http://purl.obolibrary.org/obo/chebi/inchikey']
    if len(l) > 0:
        d[l[0][1:-1]] = term.id
        #print('{}|{}'.format(l[0][1:-1], term.id))

reader = csv.DictReader(open('inchikey-without-chebi.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('item')
    qit = iturl[iturl.rfind('/')+1:]
    ik = item.get('ik')
    ch = d.get(ik)
    if ch is not None:
        print('{}|P683|"{}"|S248|Q69633402'.format(qit, ch[ch.find(':')+1:]))
