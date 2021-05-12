
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Find aliases on GO items that are GO synonyms but not exact, and
remove them. Also make sure the GO: id exists as alias.
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-Q", "--query1", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'

famtypes = ['Q670158838', 'Q417841', 'Q78155096', 'Q67101749', 'Q81505329',
 'Q84467700', 'Q83343207', 'Q7251477', 'Q68461428', 'Q67141865',
 'GO:0008534']

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

def reduce(s): return "".join([c.lower() for c in s if c.isalnum()])   

fams = {}
exactgo = []
for d in jol:
    itd = d.get('item')
    it = itd.get('value')
    lab = itd.get('label')
    if lab is None:
        print('ERROR: {}'.format(it))
        exit()
    mtype = d.get('mtype')
    rank = d.get('rank')
    if rank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    go = d.get('go')
    if mtype == 'Q39893449':
        exactgo.append(go)
        continue
    if lab.endswith('family'):
        lab = lab[:-7]
    if lab.endswith('protein'):
        lab = lab[:-8]
    fams[reduce(lab)] = it

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq1 >{}1.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}1.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

goits = {}
for d in jol:
    it = d.get('item')
    go = d.get('go')
    goits[go] = it

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
blacklist = ['GO:0004103', 'GO:0003955', 'GO:0003988', 'GO:0004063',
        'GO:0050174', 'GO:0004373', 'GO:0009011', 'GO:0008910',
        'GO:0050208']
for term in ont.terms():
    if term.obsolete:
        continue
    if term.namespace is None or term.namespace != 'molecular_function':
        continue
    goid = term.id
    if goid[:3] != 'GO:':
        continue
    if goid in exactgo or goid in blacklist:
        continue
    names = [reduce(s.description).replace('activity', '')
            for s in term.synonyms
            if s.scope == 'EXACT' and s.description != term.name]
    names.append(reduce(term.name).replace('activity', ''))
    for name in names:
        if name in fams.keys():
            if QS:
#                print('{}|P680|"{}"'.format(fams.get(name), goid))
                print('{} --- {}'.format(name, ont.get(goid).name))
                break
            j = {"id": fams.get(name),
                 "claims": {
                    "P680": { "value": goits.get(goid),
                        "qualifiers": { "P4390": "Q39893449" },
                        "references": { "P248": "Q93741199"}
                        }
                        }
                    }
            f = open('t.json', 'w')
            f.write(json.dumps(j))
            f.close()
            print(json.dumps(j), flush=True)
            ret = os.popen('wd ee t.json --summary go-sync-exact-aliases')
            print(ret.read())
            if ret.close() is not None:
                print('ERROR')
            break
        break
