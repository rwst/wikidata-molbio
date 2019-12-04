
import pronto, six, csv
from sys import *

reader = csv.DictReader(open('chebi.tab', 'r'), delimiter='\t')
qs = {}
dups = set()
for item in reader:
    iturl = item.get('item')
    qit = iturl[iturl.rfind('/')+1:]
    chid = 'CHEBI:' + item.get('ch')
    g = qs.get(chid)
    if g is None:
        qs[chid] = qit
    else:
        dups.add(chid)

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

ignore = {'425228', '144646', '27941'}

secondary = {'365419':'64090', '12800':'46570', '24036':'72010',
        '425228':'29484', '578003':'65172', '22318':'134249',
        '30410':'42121', '3736':'48947', '593038':'49537',
        '198346':'41688', '22473':'32988', '3669':'16822',
        '23008':'16646', '3736':'48947', '578003':'65172'}

"""has_input
has_intermediate
has_output
has_participant
has_primary_input
has_primary_input_or_output
has_primary_output"""

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
check = True

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
    if ns[0] != 'biological_process' and ns[0] != 'molecular_function':
        continue
    l = []
    ix = term.other.get('intersection_of')
    if ix is not None:
        l = l + ix
    ix = term.other.get('relationship')
    if ix is not None:
        l = l + ix
    if len(l) == 0:
        continue
    for cstr in l:
        if cstr[:11] != 'transports_':
            continue
        chid = cstr.split()[1]
        chit = qs.get(chid)
        if chid in dups or chit is None:
            continue
        print('{}|P527|{}|P3831|Q75152245|S248|Q75154902'.format(goit, chit))
        print('{}|P361|{}|P2868|Q75152245|S248|Q75154902'.format(chit, goit))
"""
"""

