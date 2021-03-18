
import pronto, six, csv
from sys import *

reader = csv.DictReader(open('chebi.tab', 'r'), delimiter='\t')
qs = {}
for item in reader:
    iturl = item.get('item')
    qit = iturl[iturl.rfind('/')+1:]
    chid = item.get('ch')
    qs['CHEBI:' + chid] = qit

ids = set(l.rstrip() for l in open('chebis-in-go', 'r').readlines())
ids = ids.union(set(l.rstrip() for l in open('rhea-chebis-not-in-wd', 'r').readlines()))

ignore = {'425228', '144646', '27941'}

secondary = {'365419':'64090', '12800':'46570', '24036':'72010',
        '425228':'29484', '578003':'65172', '22318':'134249',
        '30410':'42121', '3736':'48947', '593038':'49537',
        '198346':'41688', '22473':'32988', '3669':'16822',
        '23008':'16646', '3736':'48947', '578003':'65172'}

ont = pronto.Ontology('chebi.obo')

altids = {}
for term in ont.terms.values():
    alts = term.other.get('alt_id')
    if alts is None or len(alts) == 0:
        continue
    for alt in alts:
        altids[alt] = term.id

with open('t.csv', 'w', newline='') as csvfile:
    fieldnames = ['CHEBI', 'name', 'def', 'alias', 'Beilstein', 'CAS', 'Reaxys', 'sub1', 'sub2', 'sub3', 'ik', 'charge']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for idstr in ids - set(qs.keys()):
        i = idstr[6:]
        term = ont.get(idstr)
        if term is None:
            a = altids.get(idstr)
            if a is not None:
                if a in qs:
                    continue
                idstr = a
                i = idstr[6:]
                term = ont.get(idstr)
            else:
                sk = idstr[6:]
                if sk in ignore:
                    continue
                if sk in secondary.keys():
                    idstr = 'CHEBI:'+secondary.get(sk)
                    i = secondary.get(sk)
                    term = ont.get(idstr)
                else:
                    print('****************Not found: {}'.format(i))
                    break
        d = {}
        d['CHEBI'] = i
        d['name'] = term.name
        d['def'] = str(term.desc)
        l = [s.desc for s in term.synonyms if s.scope == 'EXACT' and s.desc != term.name]
        if len(l) > 0:
            d['alias'] = l
        xref = term.other.get('xref')
        if xref is None:
            pass
            #print('No xref: {} {}'.format(i, term.name))
        else:
            l = [i.split()[0] for i in xref if i[:10] == 'Beilstein:']
            if len(l) > 0:
                d['Beilstein'] = l[0]
            l = [i.split()[0] for i in xref if i[:3] == 'CAS:']
            if len(l) > 0:
                d['CAS'] = l[0]
            l = [i.split()[0] for i in xref if i[:7] == 'Reaxys:']
            if len(l) > 0:
                d['Reaxys'] = l[0]

        pv = term.other.get('property_value')
        if pv is not None:
            l = [i.split()[1] for i in pv if i[:45] == 'http://purl.obolibrary.org/obo/chebi/inchikey']
            if len(l) > 0:
                d['ik'] =l[0][1:-1]
            l = [i.split()[1] for i in pv if i[:43] == 'http://purl.obolibrary.org/obo/chebi/charge']
            if len(l) > 0:
                d['charge'] =l[0][1:-1]
        
        p1 = []
        p2 = []
        p3 = []
        # !!! parents also when other-->has_part this
        for pterm1 in term.parents:
            s = qs.get(pterm1.id)
            if s is not None:
                p1.append(s)
            else:
                print('Missing parent1: {} {}'.format(pterm1.id, pterm1.name))
                for pterm2 in pterm1.parents:
                    s = qs.get(pterm2.id)
                    if s is not None:
                        p2.append(s)
                    else:
                        print('Missing parent2: {} {}'.format(pterm2.id, pterm2.name))
                        found = False
                        m = []
                        for pterm3 in pterm2.parents:
                            s = qs.get(pterm3.id)
                            if s is not None:
                                p3.append(s)
                                found = True
                            else:
                                m.append((pterm3.id, pterm3.name, pterm2.id, pterm2.name, pterm1.id, pterm1.name))
                        if not found:
                            print('Missing parent3: {}'.format(m))
        if len(p1) > 0:
            p = p1
        elif len(p2) > 0:
            p = p2
        elif len(p3) > 0:
            p = p3
        else:
            p = []
        n = 0
        for parent in p:
            n = n + 1
            if n>3: break
            d['sub'+str(n)] = parent
        #print(d)
        writer.writerow(d)
