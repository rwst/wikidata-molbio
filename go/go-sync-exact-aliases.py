
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Find aliases on GO items that are GO synonyms but not exact, and
remove them. Also make sure the GO: id exists as alias.
Use with wd ee.
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-d", "--diff", help="print changes in human readable form",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'
MODUS = 'lenient'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

goids = {}
for d in jol:
    goid = d.get('go')
    it = d.get('p')
    al = d.get('al')
    lab = d.get('lab')
    git = goids.get(goid)
    if git is None:
        goids[goid] = [it, lab, al]
    else:
        git.append(al)

blacklist = ['GO:0004104']
print('reading GO', file=sys.stderr)
ont = pronto.Ontology('go-plus.owl')
for goid in goids.keys():
    if goid in blacklist:
        continue
    term = ont.get(goid)
    if term is None:
        print("CAN'T HAPPEN: {}".format(goid))
        exit()
    if term.name == None or term.obsolete = True: #alt_id
        continue
    data = goids.get(goid)
    qit = data[0]
    lab = data[1]
    als = set(data[2:])
    exs = set()
    for syn in term.synonyms:
        if syn.scope == 'EXACT' and len(syn.description) <= 250:
            if term.name.endswith('activity') and not syn.description.endswith('activity'):
                continue
            exs.add(syn.description)
    exs.add(goid)
    exs.add(lab)
    exs.add(term.name)
    if exs == als:
        continue
    for syn in als:
        if syn.lower() in exs or syn+'s' in exs:
            exs.add(syn)
    if args.diff:
        if MODUS != 'lenient' and len(als.difference(exs)):
            print("{} --- {}".format(term.name, als.difference(exs)))
        if len(exs.difference(als)):
            print("{} +++ {}".format(term.name, exs.difference(als)))
        continue
    if MODUS == 'lenient':
        exs = exs.union(als)
    exs.remove(lab)
    if exs == set([goid]) or exs == als:
        continue
    j = {"id": qit,
        "aliases": { "en": list(exs) }
        }
    print(json.dumps(j), flush=True)
