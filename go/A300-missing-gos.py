
import pronto, six, csv, os, json, argparse, sys, datetime

"""
wget http://purl.obolibrary.org/obo/go/extensions/go-plus.owl
use with wd ce
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
GORELEASE = "Q112968510"

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True, file=sys.stderr)

goids = {}
items = set()
for d in jol:
    goid = d.get('goid')
    gorank = d.get('rank')
    if gorank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    it = d.get('item')
    git = goids.get(goid)
    if git is None:
        goids[goid] = it
        items.add(it)
    else:
        goids[goid] = it

print('reading GO', file=sys.stderr)
ont = pronto.Ontology('go-plus.owl')
newids = set()
for term in ont.terms():
    if term.obsolete:
        continue
    goid = term.id
    if goid[:3] != 'GO:' or goid in goids.keys():
        continue
    newids.add(goid)
    # exact match
    #print(term.name)

MAPPING_TYPE = 'P4390'
SKOS_EXACT = 'Q39893449'
STATED_IN = 'P248'
namespaces = {'cellular_component': 'Q5058355',
        'biological_process': 'Q2996394',
        'molecular_function': 'Q14860489'}


for newid in newids:
    term = ont.get(newid)
    d = term.relationships
    if any(t.id in newids for rset in term.relationships.values() for t in rset):
        continue
    ent = {}
    claims = {}

    url = "http://purl.obolibrary.org/obo/GO_" + newid[3:]
    claims['P2888'] = [{ 'value': url, 'references': { STATED_IN : GORELEASE } }]
    claims['P686'] = [{ 'value': newid, 'references': { STATED_IN : GORELEASE } }]
    ent['labels'] = {'en': term.name }

    desc = str(term.definition)
    if len(desc) > 250:
        desc = desc[:250]
    ent['descriptions'] = {'en': desc }
    syns = []
    for syn in term.synonyms:
        if syn.scope == 'EXACT':
            syns.append(syn.description)
    if len(syns) > 0:
        ent['aliases'] = { 'en': syns }
    
    nsp = namespaces.get(term.namespace)
    if nsp is None:
        print('Cant happen: {}, {}'.format(newid, term.namespace))
        exit()
    claims['P31'] = [{ 'value': nsp, 'references': { STATED_IN : GORELEASE } }]

    for r in term.relationships.keys():
        if r.name == 'is a':
            tset = term.relationships.get(r)
            for t in tset:
                goid = goids.get(t.id)
                if goid is None:
                    print('Cant happen: {}, {}'.format(term.id, t.id))
                    exit()
                claims['P279'] = [{ 'value': goid, 'references': { STATED_IN : GORELEASE } }]

    ent['claims'] = claims
    print(json.dumps(ent), flush=True)



