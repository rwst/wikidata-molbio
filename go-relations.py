
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

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')

for term in ont.terms.values():
    goid = term.id
    if goid[:3] != 'GO:':
        continue
    goit = efs.get(goid)
    if goit is None:
        continue
    rel = term.relations
    for relstr in ['has_input', 'has_intermediate', 'has_output', 'has_participant', 'has_part', 'exports', 'transports_or_maintains_localization_of']:
        R = pronto.relationship.Relationship(relstr)
        ix = rel.get(R)
        if ix is None:
            continue
        #ns = term.other.get('namespace')
        #if ns[0] != 'biological_process':
        #    continue
        for term in ix:
            chid = term.id
            chit = qs.get(chid)
            if chid in dups or chit is None:
                continue
            type = relstr
            if type == 'has_output' or type == 'has_primary_output':
                print('{}|P527|{}|P3831|Q542929|S248|Q75154902'.format(goit, chit))
                #print('-{}|P361|{}'.format(chit, goit))
                print('{}|P361|{}|P2868|Q542929|S248|Q75154902'.format(chit, goit))
            if type == 'has_input' or type == 'has_primary_input':
                print('{}|P527|{}|P3831|Q45342565|S248|Q75154902'.format(goit, chit))
                #print('-{}|P361|{}'.format(chit, goit))
                print('{}|P361|{}|P2868|Q45342565|S248|Q75154902'.format(chit, goit))
            if type == 'has_intermediate':
                print('{}|P527|{}|P3831|Q7458208|S248|Q75154902'.format(goit, chit))
                #print('-{}|P361|{}'.format(chit, goit))
                print('{}|P361|{}|P2868|Q7458208|S248|Q75154902'.format(chit, goit))
            if type == 'has_participant' or type == 'has_primary_input_or_output':
                print('{}|P527|{}|P3831|Q75232720|S248|Q75154902'.format(goit, chit))
                #print('-{}|P361|{}'.format(chit, goit))
                print('{}|P361|{}|P2868|Q75232720|S248|Q75154902'.format(chit, goit))
            if type == 'has_part':
                print('{}|P527|{}|S248|Q75154902'.format(goit, chit))
                print('{}|P361|{}|S248|Q75154902'.format(chit, goit))
            if type == 'transports_or_maintains_localization_of' or type == 'exports':
                print('{}|P527|{}|P3831|Q75152245|S248|Q75154902'.format(goit, chit))
                print('{}|P361|{}|P2868|Q75152245|S248|Q75154902'.format(chit, goit))
"""
"""

