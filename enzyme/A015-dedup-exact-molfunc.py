
import csv, os, json, argparse, sys

"""
sed 's+^.*GO:+GO:+g' query.tsv |sed 's/^GO:\([0-9]\+\).*$/GO:\1/g' |sort |uniq -d
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

goids = {}
for d in jol:
    rank = d.get('rank')
    if rank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    goid = d.get('p')
    qit = d.get('item')
    if goid in goids.keys():
        print('{}: {} {}'.format(goid, goids.get(goid), qit))
    else:
        goids[goid] = qit

