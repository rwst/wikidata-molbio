
import os, json, argparse, sys, datetime, time, csv

"""
output claim-ids to remove, use with wd rc
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("item", nargs=1)
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

query = """
SELECT DISTINCT ?stmt 
{{
  {{
    ?item wdt:P680 {0}.
    ?item p:P680 ?stmt.
    ?stmt ps:P680 {0}
  }} UNION {{
    ?item wdt:P681 {0}.
    ?item p:P681 ?stmt.
    ?stmt ps:P681 {0}
  }} UNION {{  
    ?item wdt:P682 {0}.
    ?item p:P682 ?stmt.
    ?stmt ps:P682 {0}
  }} UNION {{  
    ?item wdt:P683 [].
    ?item wdt:P361 {0}.
    ?item p:P361 ?stmt.
    ?stmt ps:P361 {0}
  }}
}}
""".format("wd:" + args.item[0])

if dontquery is False:
    file = open('{}.rq'.format(script), 'w')
    file.write(query)
    file.close()
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
    print(d, flush=True)
