
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Find obsolete GO items (either "is_obsolete" or not existing) and:
Remove "exact match" and deprecate "Gene Ontology ID" claims.
In case the GO entry has "replaced_by" add "replaced by" (P1366)
Change "instance of"-->"F/C/P obsoleted in GO"
Remove any GO: alias
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
    git = goids.get(goid)
    if git is None:
        goids[goid] = [it, al]
    else:
        git.append(al)

blacklist = ['GO:0004104']
print('reading GO')
ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
for goid in goids.keys():
    if goid in blacklist:
        continue
    term = ont.get(goid)
    if term is None:
        print("CAN'T HAPPEN: {}".format(goid))
        exit()
    data = goids.get(goid)
    qit = data[0]
    als = data[1:]
    rmals = []
    newals = set(als + [goid])
    for syn in term.synonyms:
        if syn.scope != 'EXACT' and syn.description in als:
            newals.remove(syn.description)
        if syn.scope == 'EXACT':
            newals.add(syn.description)
    if newals == set(als):
        continue
    if QS:
        for al in newals:
            print('{}|Aen|"{}"'.format(qit, al))
    else:
        j = {"id": qit,
                "aliases": { "en": list(newals) }
                }
        f = open('t.json', 'w')
        f.write(json.dumps(j))
        f.close()
        print(json.dumps(j), flush=True)
        ret = os.popen('wd ee t.json --summary go-sync-exact-aliases')
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
