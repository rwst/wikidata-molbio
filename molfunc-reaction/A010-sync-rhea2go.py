
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
    i = goits.get(goid)
    if i is not None:
        # also catches multiple Rhea claims
        print('{} duplicate: {} {}'.format(goid, i, item), file=sys.stderr)
        exit()
    goits[goid] = item
    stmt = d.get('stmt')
    if stmt is not None and len(stmt) > 0:
        rh = d.get('url')[29:]
        gorh[goid] = rh
        s = rhstmts.get('rh')
        if s is not None:
            print('RHEA:{} duplicate: {} {}'.format(rh, s, stmt), file=sys.stderr)
        rhstmts[rh] = stmt

with open('rhea2go.txt') as file:
    for line in file.readlines():
        line = line.rstrip()
        if not line.startswith('RHEA'):
            continue
        rh = line[5:line.find(' ')]
        go = line[line.find(';')+2:]
        if goits.get(go) is not None:
            #print('missing: {}'.format(go), file=sys.stderr)
            grh = gorh.get(go)
            if grh is not None:
                if rh == grh:
                    continue
                print(rhstmts.get(grh), file=sys.stderr)
            print('{} P2888 https://www.rhea-db.org/rhea/{}'.format(goits.get(go), rh))


