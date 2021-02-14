
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
print(args)

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
        ref = { 'P887': 'Q105487974', 'P3452': func }
        refs.append(ref)
    j = {"id": it, "claims": { 'P31': [{
        "value": "Q67015883",
        "references": refs }] } }
    print(json.dumps(j))

