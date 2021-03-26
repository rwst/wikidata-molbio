
import csv, os, json, argparse, sys

"""
use with wd ee
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
MAPPING_TYPE = 'P4390'
SKOS_EXACT = 'Q39893449'
INFERRED_FROM = 'P3452'
NAME = 'Q82799'
MOLFUNC = 'Q14860489'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

for d in jol:
    it = d.get('item')
    stmt = d.get('stmt')
    val = d.get('func')

    j = { 'id': it, 'claims': { 'P680': [ {
            'id': stmt,
            'value': val,
            "qualifiers": { MAPPING_TYPE: SKOS_EXACT },
            "references": { INFERRED_FROM: [NAME, MOLFUNC] } }
            ] } }
    print(json.dumps(j), flush=True)

