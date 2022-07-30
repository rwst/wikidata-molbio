
import os, json, argparse, sys, datetime, time

"""
Add refs to stmts added in sync-rhea2go.
Use with wd ar.
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
#parser.add_argument('-d', '--date', help='rhea2go file version date (YYYY-MM-DD)', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
#date = args.date + 'T00:00:00Z'

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise

with open('{}.json'.format(script)) as file:
    for line in file.readlines():
        line = line.rstrip()
        print('{} P854 http://geneontology.org/external2go/rhea2go'.format(line))


