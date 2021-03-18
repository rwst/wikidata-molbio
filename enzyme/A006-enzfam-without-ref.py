
import csv, os, json, argparse, sys

"""
use with wd ar
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

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))

for stmt in file.readlines():
    j = {"guid": stmt.rstrip(),
            "snaks": { "P3452": ["Q82799", "Q14860489"] }
            }
    print(json.dumps(j), flush=True)

