
import pronto, six, csv
from sys import *

"""
Input:
SELECT DISTINCT ?p ?l ?a ?go
{
    ?p p:P680 [ ps:P680 ?func; pq:P4390 wd:Q39893449; ].
    ?func wdt:P686 ?go.
    ?p rdfs:label ?l.
      FILTER( LANG(?l) = 'en' )
    OPTIONAL {
      ?p skos:altLabel ?a.
      FILTER( LANG(?l) = LANG(?a) )
    }
}

"""

def reduce(s): return "".join([c.lower() for c in s if c.isalnum()])

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
efs = {}
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    goid = item.get('go')
    lab = item.get('l')
    al = item.get('a')
    ef = efs.get(qit)
    if ef is None or len(ef) == 0:
        if al is None:
            efs[qit] = (set([reduce(lab)]),goid)
        else:
            efs[qit] = (set([reduce(lab),reduce(al)]),goid)
    else:
        ef[0].add(reduce(al))


ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
id_als = set()

for qit in efs.keys():
    names,goid = efs.get(qit)
    term = ont.terms.get(goid)
    if term is None:
        #print(goid)
        continue
    exact = False
    for s in term.synonyms:
        d = s.desc.replace(' activity', '')
        if s.scope == 'EXACT' and reduce(d) not in names:
            print('{}|Aen|"{}"'.format(qit, d))

