
import pronto, six, csv
from sys import *

"""
For all items with broad molfunc, and not being an InterPro family:
SELECT DISTINCT ?p ?pLabel ?funcLabel ?go
{
    ?p p:P680 [ ps:P680 ?func; pq:P4390 wd:Q39894595; ].
    MINUS {
        ?p wdt:P2926 [].
    }
    ?func wdt:P686 ?go.
    ?p rdfs:label ?pLabel.
    ?func rdfs:label ?funcLabel.
    FILTER (LANG(?pLabel) = 'en' && LANG(?funcLabel) = 'en')
}
print those items having a label that is an exact synonym of
the molfunc (minus the string "activity")

This catches wrong "broad" mappings.
"""

def reduce(s): return "".join([c.lower() for c in s if c.isalnum()])

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
id_als = set()

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')

for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    goid = item.get('go')
    lab = reduce(item.get('pLabel'))

    term = ont.get(goid)
    if term is None:
        #print(goid)
        continue

    d = term.name.replace(' activity', '')
    #print('{} "{}" "{}"'.format(goid, term.name, lab))
    if reduce(d) == lab:
        print('---{} "{}"'.format(qit, d))
        continue
    for s in list(term.synonyms):
        d = s.description.replace(' activity', '')
        if s.scope == 'EXACT' and reduce(d) == lab:
            print('{} "{}"'.format(qit, d))
            break

