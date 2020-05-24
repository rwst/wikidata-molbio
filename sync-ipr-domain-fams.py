
import os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
For every IPR site (Active_site/Binding_site/Conserved_site/Domain/Repeat)
create missing associated families. OTOH, mark such families of obsoleted
domains such that they can be merged with their domains.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq1 >{}.tmp'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.tmp'.format(script))
s = file.read()
obsdom = set(s.split())

input = gzip.open('interpro.xml.gz')                                   
tree = ET.parse(input)
root = tree.getroot() 

dtypes = set(['Active_site', 'Binding_site', 'Conserved_site',
    'Domain', 'Repeat'])
domids = set()
allids = set()
labels = {}
for child in root:
    if child.tag == 'interpro':
        ipr = child.attrib.get('id')
        allids.add(ipr)
        if child.attrib.get('type') in dtypes:
            domids.add(ipr)
        for ch in child:
            if ch.tag == 'name':
                labels[ipr] = ch.text

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

qits = {}
assfams = {}
print('Manual Task 1: clean obsolete families, merge with domain')
for d in jol:
    ipr = d.get('ipr')
    qit = d.get('item')
    stmt = d.get('stmt')
    q = qits.get(ipr)
    if ipr in domids and stmt is None:
        if q is not None and q != qit:
            print('duplicate IPR claim: {} {} {}'.format(q, qit, ipr))
        else:
            qits[ipr] = qit
    if stmt is not None:
        adomipr = d.get('adomipr')
        f = assfams.get(adomipr)
        if f is not None and f != qit:
            print('duplicate association: {} {} {}'.format(f, qit, adomipr))
            raise
        else:
            assfams[adomipr] = qit
        if adomipr not in allids:
            print(adomipr, qit, ipr)
            continue

for nipr in domids.difference(set(assfams.keys())):
    qit = qits.get(nipr)
    if qit is None:
        continue
    lab = labels.get(nipr)
    nlab = lab
    l = len(lab)
    ll = lab.lower()
    if (ll.rfind('family') >=0 and ll.rfind('family') >= l-16):
        label = lab
    elif (ll.rfind('protein') >=0 and ll.rfind('protein') >= l-16 or
        ll.rfind('transporter') == l-9 or
        ll.rfind('inhibitor') == l-9 or
        ll.rfind('peptide') >=0 and ll.rfind('peptide') >= l-16 or
        ll.rfind('toxin') >=0 and ll.rfind('toxin') >= l-14 or
        ll.rfind('enzyme') >=0 and ll.rfind('enzyme') >= l-15 or
        ll.rfind('ase') >=0 and ll.rfind('ase') >= l-8):
        label = lab + ' family'
    elif (ll.rfind('domain') == l-6):
        label = lab + ', protein family'
    elif (ll.rfind('binding') >=0 and ll.rfind('binding') >= l-11 or
        ll.rfind('transmembrane') >=0 and ll.rfind('transmembrane') >= l-16 or
        ll.rfind('terminal') == l-8 or
        ll.rfind('central') == l-7 or
        ll.rfind('processing') == l-10 or
        ll.rfind('associated') == l-10 or
        ll.rfind('catalytic') == l-9 or
        ll.rfind('periplasmic') == l-11 or
        ll.rfind('extracellular') == l-13 or
        ll.rfind('core') == l-4):
        label = lab + ' domain, protein family'
    else:
        label = lab + ', protein family'
    #label = label[0].lower() + label[1:]

    if QS:
        print('CREATE\nLAST|Len|"{}"\nLAST|Den|"protein family"\nLAST|Aen|"{}"\nLAST|P31|Q81505329|P642|{}|S248|Q81384305|S2926|"{}"\nLAST|P527|{}|S248|Q81384305|S2926|"{}"\nLAST|P2926|"{}"|S248|Q81384305'.format(label, nipr, qit, nipr, qit, nipr, nipr))
    else:
        j = {"labels": { "en": label },
            "descriptions": {"en": "protein family",
                    "de": "Proteinfamilie"},
            "aliases": { "en": nipr },
            "claims": {
                 "P31": { "value": "Q81505329",
                     "qualifiers": { "P642": qit },
                     "references": { "P248": "Q95046663"} },
                 "P527": { "value": qit,
                     "references": { "P248": "Q95046663"} },
                 "P2926": { "value": nipr,
                     "references": { "P248": "Q95046663"} },
                    }
                }
        f = open('t.json', 'w')
        f.write(json.dumps(j))
        f.close()
        print(json.dumps(j), flush=True)
        ret = os.popen('wd ce t.json --summary sync-ipr-domain-fams')
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
       
