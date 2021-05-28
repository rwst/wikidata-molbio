
import csv, os, json, argparse, sys

"""
Everything with catalytic mol. function that's not a single protein or some
other type should be a group or class of enzymes, with reference to that
molecular function.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
print(args, file=sys.stderr)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
BASED_ON_HEURISTIC = 'P887'
INFERRED_FROM_FUNCTION = 'Q105487974'
INFERRED_FROM = 'P3452'
GROUP_OF_ENZYMES = 'Q67015883'

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

funcs = {}
for d in jol:
    rank = d.get('rank')
    if rank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    qit = d.get('item')
    func = d.get('func')
    if qit in funcs.keys():
        l = funcs.get(qit)
        l.append(func)
    else:
        funcs[qit] = [func]

for it in funcs.keys():
    refs = []
    for func in funcs.get(it):
        ref = { BASED_ON_HEURISTIC: INFERRED_FROM_FUNCTION, INFERRED_FROM: func }
        refs.append(ref)
    j = {"id": it, "claims": { 'P31': [{
        "value": GROUP_OF_ENZYMES,
        "references": refs }] } }
    print(json.dumps(j))

