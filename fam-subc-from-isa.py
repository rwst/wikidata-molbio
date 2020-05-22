
import pronto, six, csv, os, json, argparse, sys, datetime, time

"""
For every family with exact molfunc: if there is no subclass-of claim
to the direct superclass according to GO, then add it.
  family A: mofunc---> activity a
  family B: mofunc---> activity b
  then A: P279---> B if in Gene Ontology: term a: is_a term b
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument('-l', '--lag', action='store')

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
lag = args.lag
if lag is None:
    lag =0
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

goids = {}
for d in jol:
    rank = d.get('rank')
    if rank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    p = d.get('p')
    goid = d.get('goid')
    qit = d.get('item')
    mtype = d.get('mtype')
    if mtype != 'Q39893449':
        continue
    supit = d.get('supc')
    if goid in goids.keys():
        g = goids.get(goid)
        g[1].append(supit)
    else:
        goids[goid] = (qit,[supit])

ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
for goid in goids.keys():
    term = ont.get(goid)
    qit,supclaims = goids.get(goid)
    for supterm in term.superclasses(distance=1, with_self=False):
        supit = goids.get(supterm.id)
        if supit is None or supit[0] in supclaims:
            continue
        supqit = supit[0]
        if QS:
            print('{}|P279|{}|S887|Q94996521'.format(qit, supqit))
        else:
            j = {"id": qit,
                 "claims": {
                    "P279": { "value": supqit,
                        "references": { "P887": "Q94996521"}
                        }
                        }
                    }
            f = open('t.json', 'w')
            f.write(json.dumps(j))
            f.close()
            print(json.dumps(j), flush=True)
            ret = os.popen('wd ee t.json --summary fam-subc-from-isa')
            print(ret.read())
            if ret.close() is not None:
                print('ERROR')
            time.sleep(int(lag))
