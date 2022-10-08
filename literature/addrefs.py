
import os, json, argparse, sys, datetime, time, csv

"""
output claim-ids to remove, use with wd rc
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
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise

file = open('{}.json'.format(script))
s = file.read().split()
if len(s) == 0:
    print('Nothing to do...')
    exit()
for d in s:
    print("{} P887 Q69653744".format(d), flush=True)
