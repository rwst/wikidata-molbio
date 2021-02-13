
import os, json, argparse, sys, datetime, time
import pronto, six

"""
bzcat latest-all.json.bz2 |wikibase-dump-filter --simplify --claim 'P698&P921' |jq '[.id,.claims.P698,.claims.P921]' -c >PMID.ndjson
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
print('reading {} part-of statements'.format(len(jol)))
partofs = set()
for d in jol:
    item = d.get('item')
    fam = d.get('fam')
    partofs.add((item, fam))

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq1 >{}1.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}1.json'.format(script))
s = file.read()
jol = json.loads(s)
print('considering {} has-part statements'.format(len(jol)))
for d in jol:
    item = d.get('item')
    fam = d.get('fam')
    if (item, fam) not in partofs:
        j = {"id": item,
            "claims": {
                 "P361": { "value": fam,
                     "references": { "P887": "Q96775080" } },
                    }
                }
        print(json.dumps(j), flush=True)
