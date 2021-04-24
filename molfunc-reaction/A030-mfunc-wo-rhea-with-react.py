
import os, json, argparse, sys, datetime, time

"""
Use with wd rc.
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

stmts1 = set()
stmts2 = set()
for d in jol:
    stmts1.add(d.get('stmt1'))
    s = d.get('stmt2')
    if s is not None and len(s)>0:
        stmts2.add(s)

for s in stmts2:
    print(s)
for s in stmts1:
    print(s)
