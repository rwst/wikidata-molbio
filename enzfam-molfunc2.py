import pronto, six, csv
from sys import *

reader = csv.DictReader(open('goid.tab', 'r'), delimiter='\t')
qs = {}
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    goid = item.get('goid')
    qs[goid] = qit

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    lab = item.get('pLabel')
    act = (lab + " activity").lower().replace('-', ' ')
    #print(act.lower())
    for i in ont.terms:
        if i is None:
            continue
        it = ont.get(i)
        ns = it.other.get('namespace')
        if ns is None or ns[0] != 'molecular_function':
            continue
        #print(it.name.lower())
        gq = qs.get(it.id)
        if it.name.lower().replace('-', ' ') == act:
            print("{}|P680|{}".format(qit, gq))
            break
        else:
            for s in it.synonyms:
                if s.desc.lower().replace('-', ' ') == act:
                    print("{}|P680|{}".format(qit, gq))
                    #print("{} {} {} {}".format(qit, it.id, lab, it.name))
                break
