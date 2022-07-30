
import os, json, argparse, sys, datetime, time

"""
http://geneontology.org/external2go/rhea2go
Project the newest mapping onto "exact match" (P2888) claims.
Complains about missing functions on stderr.
Use stderr with wd rc, stdout with wd ac.
TODO: merge this with add-ref
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-m", "--mult", help="check for multiple RHEA",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

goits = {}
gorh = {}
rhstmts = {}
for d in jol:
    item = d.get('item')
    goid = d.get('gofunc')
    gorank = d.get('rank')
    if gorank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    i = goits.get(goid)
    if i is not None and i != item:
        # also catches multiple Rhea claims
        print('{} duplicate: {} {}'.format(goid, i, item), file=sys.stderr)
        exit()
    goits[goid] = item
    stmt = d.get('stmt')
    if stmt is None or len(stmt) == 0:
        continue
    rh = d.get('url')[29:]
    r = gorh.get(goid)
    if r is None:
        gorh[goid] = [rh]
    else:
        r.append(rh)
    s = rhstmts.get('rh')
    if s is not None:
        print('RHEA:{} duplicate: {} {}'.format(rh, s, stmt), file=sys.stderr)
        exit(0)
    rhstmts[rh] = stmt

rhs = {}
with open('rhea2go.txt') as file:
    for line in file.readlines():
        line = line.rstrip()
        if not line.startswith('RHEA'):
            continue
        rh = line[5:line.find(' ')]
        go = line[line.find(';')+2:]
        if goits.get(go) is None:
            print('missing: {}'.format(go), file=sys.stderr)
            exit(0)
        r = rhs.get(go)
        if r is None:
            rhs[go] = [rh]
        else:
            r.append(rh)

for go in rhs.keys():
    gset = gorh.get(go)
    if gset is None:
        gset = set()
    else:
        gset = set(gset)
    rset = rhs.get(go)
    if rset is None:
        rset = set()
    else:
        rset = set(rset)
    if args.mult and len(rset) > 1:
        print("multiple RHEAs for {}: {}. Check newest go.obo and fix rhea2go!".format(go, rset))
    oldr = rset.difference(gset)
    newr = gset.difference(rset)
    #print((go,gset,rset,oldr,newr), file=sys.stderr)
    for rh in newr:
        print(rhstmts.get(rh), file=sys.stderr)
    for rh in oldr:
        print('{} P2888 https://www.rhea-db.org/rhea/{}'.format(goits.get(go), rh))


