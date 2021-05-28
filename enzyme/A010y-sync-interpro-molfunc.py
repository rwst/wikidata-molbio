import os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
Loads all items with IPR except domain families and checks InterPro release for M annotations.
Checks also for duplicate IPR.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-r", "--rm", help="remove stmts not in InterPro",
        action="store_true")
parser.add_argument('-i', '--iprel', help='InterPro release item', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
MAPPING_TYPE = 'P4390'
SKOS_BROAD = 'Q39894595'
STATED_IN = 'P248'
INTERPRO_RELEASE = args.iprel

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise

### get GO F items
query = """
SELECT DISTINCT ?item ?goid
{{
    ?item wdt:P31 wd:Q14860489 .
    ?item wdt:P686 ?goid .
}}
"""
f = open('t.rq', 'w')
f.write(query)
f.close()

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql t.rq >t.json')
    if ret.close() is not None:
        raise

input = gzip.open('interpro.xml.gz')                                   
tree = ET.parse(input)
root = tree.getroot() 

its = {}
for child in root:
    if child.tag == 'interpro':
        its[child.attrib.get('id')] = child

#print(set(its.keys()).intersection(delids))

# get IPR items
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)
qits = {}
goids = {}
stmts = {}
for d in jol:
    ipr = d.get('ipr')
    qit = d.get('item')
    p = d.get('prop')
    if p is not None and len(p) > 0:
        continue
    if ipr not in qits.keys():
        qits[ipr] = qit
    goid = d.get('goid')
    stmt = d.get('stmt')
    if goid is not None:
        g = goids.get(ipr)
        if g is None:
            goids[ipr] = set([goid])
        else:
            g.add(goid)
        stmts[(qit, goid)] = stmt

file = open('t.json')
s = file.read()
jol = json.loads(s)
goits = {}
for d in jol:
    goid = d.get('goid')
    qit = d.get('item')
    if goid in qits.keys():
        print('duplicate: {}'.format(goid), file=sys.stderr)
        exit()
    else:
        goits[goid] = qit


qual = { MAPPING_TYPE: SKOS_BROAD }
for nipr in qits.keys():
    entry = its.get(nipr)
    if entry is None:
        print('not found: {}'.format(nipr), file=sys.stderr)
        exit()
    type = entry.attrib.get('type')
    ch = None
    cl = None
    claims = []
    refipr = { STATED_IN: INTERPRO_RELEASE }
    if args.rm:
        for ch in entry:
            if ch.tag == 'class_list':
                cl = ch.getchildren()
                g = goids.get(nipr)
                if g is None:
                    g = set()
                for c in cl:
                    if c.tag == 'classification' and c.attrib.get('class_type') == 'GO':
                        id = c.attrib.get('id')
                        if id in g:
                            g.remove(id)
                for goid in g:
                    print(stmts.get((qits.get(nipr), goid)))
    else:
        for ch in entry:
            if ch.tag == 'class_list':
                cl = ch.getchildren()
                for c in cl:
                    if c.tag == 'classification' and c.attrib.get('class_type') == 'GO':
                        id = c.attrib.get('id')
                        g = goids.get(nipr)
                        if g is None:
                            g = set()
                        if id in goits.keys() and id not in g:
                            claims.append( { 'value': goits.get(id),
                                'qualifiers': qual,
                                'references': refipr } )
        if len(claims) > 0:
            j = { "id": qits.get(nipr), "claims": { 'P680': claims } }
            print(json.dumps(j), flush=True)
