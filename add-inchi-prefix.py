
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
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise

file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

for d in jol:
    stmt = d.get('stmt')
    inchi = d.get('inchi')
#    ref = d.get('ref')
    print('{} {}'.format(stmt, 'InChI='+inchi))
    #print('{{ "guid": "{}", "oldValue": "{}", "newValue": "{}" }}'.format(stmt, inchi, 'InChi='+inchi))
