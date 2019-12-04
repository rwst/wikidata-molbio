import pronto, six, csv
from sys import *

ont = pronto.Ontology('chebi.obo')
d = {}
dupes = []
for term in ont.terms.values():
    xref = term.other.get('property_value')
    if xref is None:
        continue
    l = [i.split()[1] for i in xref if i[:45] == 'http://purl.obolibrary.org/obo/chebi/inchikey']
    if len(l) > 0:
        if d.get(l[0][1:-1]) is not None:
            dupes.append(l[0][1:-1])
            continue
        d[l[0][1:-1]] = term.id
        #print('{}|{}'.format(l[0][1:-1], term.id))

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('item')
    qit = iturl[iturl.rfind('/')+1:]
    ik = item.get('ik')
    if ik in dupes:
        continue
    ch = item.get('ch')
    chid = d.get(ik)
    if chid is not None and len(chid)>0:
        if chid[6:] != ch:
            #print('{}   {}'.format(chid[6:], ch))
            print('-{}|P683|"{}"'.format(qit, ch))
