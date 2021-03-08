
import os, json, argparse, sys, datetime, time, csv

"""
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

taxa = {}    # compound --> taxon --> ref
subjs = {}   # ref --> compound
for d in jol:
    comp = d.get('comp')
    taxon = d.get('taxon')
    ref = d.get('ref')
    subj = d.get('ingr')
    t = taxa.get(comp)
    if t is None:
        taxa[comp] = { taxon : set([ref]) }
    else:
        tt = t.get(taxon)
        if tt is None:
            t[taxon] = set([ref])
        else:
            tt.add(ref)
    a = subjs.get(ref)
    if a is None:
        subjs[ref] = set([subj])
    else:
        a.add(subj)

print("number of references used: {}".format(len(subjs.keys())))

ntsubjs = {}
ncsubjs = {}
for comp in taxa.keys():
    t = taxa.get(comp)
    for taxon,refset in t.items():
        for ref in refset:
            s = subjs.get(ref)
            if s is None or (s is not None and taxon not in s):
                r = ntsubjs.get(ref)
                if r is None:
                    ntsubjs[ref] = set([taxon])
                else:
                    r.add(taxon)
            if s is None or (s is not None and comp not in s):
                r = ncsubjs.get(ref)
                if r is None:
                    ncsubjs[ref] = set([comp])
                else:
                    r.add(comp)

print("number of references with new taxon subject: {}".format(len(ntsubjs.keys())))
print("number of references with new compound subject: {}".format(len(ncsubjs.keys())))

allrefs = set(ntsubjs.keys()).union(set(ncsubjs.keys()))

print("number of references to change: {}".format(len(allrefs)))
print("don't change: {}".format(set(subjs.keys()).difference(allrefs)))

maxtclaims = 0
maxcclaims = 0

for ref in allrefs:
    claims = []
    if ref in ntsubjs.keys():
        for taxon in ntsubjs.get(ref):
            claim = { "value": taxon, "references": { "P248": "Q104225190"} }
            claims.append(claim)
        maxtclaims = max(maxtclaims, len(ntsubjs.get(ref)))
    if ref in ncsubjs.keys():
        for comp in ncsubjs.get(ref):
            claim = { "value": comp, "references": { "P248": "Q104225190"} }
            claims.append(claim)
#        if len(ncsubjs.get(ref)) > 500:
#            print("xxx {} {}".format(len(ncsubjs.get(ref)), ref))
        maxcclaims = max(maxcclaims, len(ncsubjs.get(ref)))
    j = {"id": ref, "claims": { "P921" : claims } }
    print(json.dumps(j), flush=True)

print("max taxa added per reference: {}".format(maxtclaims))
print("max compounds added per reference: {}".format(maxcclaims))

