
import os, json, argparse, sys, datetime

"""
Use query manually to find families that don't fit the function exactly.
Then run with query and use 'wd ar' to add reference.
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
GORELEASE = "Q102066615"

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

ndate = datetime.date.today().isoformat()
for d in jol:
    it = d.get('item')
    stmt = d.get('stmt')

    j = {"guid": stmt,
            "snaks": { "P248": GORELEASE,
                        "P813": ndate },
            }
    print(json.dumps(j), flush=True)
