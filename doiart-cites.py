
import os, json, argparse, sys, datetime, time, csv, datetime
import urllib.request as ureq

"""
bzcat latest-all.json.bz2 |wikibase-dump-filter --simplify --claim 'P356' |jq '[.id,.claims.P356]' -c >DOI.ndjson
or use wdumper
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--item', action='store', required=True)
parser.add_argument('-d', '--doi', action='store', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
DOI = args.doi
item = args.item
script = os.path.basename(sys.argv[0])[:-3]
crossref = 'https://api.crossref.org/works/{}'.format(DOI, script)
print('contacting CrossRef', file=sys.stderr)
cref = None
with ureq.urlopen(crossref) as f:
    cref = f.read().decode('utf-8')
if cref is None:
    raise
file = open('{}.json'.format(script), "w")
file.write(cref)

jol = json.loads(cref)
reflist = jol.get('message').get('reference')
print('references received: {}'.format(len(reflist)), file=sys.stderr)

dois = {}
print('reading dump data...', file=sys.stderr)
file = open('DOI.ndjson')
for line in file.readlines():
    arr = json.loads(line.strip())
    qit = arr[0]
    doilist = arr[1]
    if len(doilist) == 0:
        continue
    for doi in doilist:
        doi = doi.upper()
        d = dois.get(doi)
        if d is not None:
            #print('duplicate DOI {}'.format(doi), file=sys.stderr)
            continue
        dois[doi] = qit

P2860claims = []
for ref in reflist:
    doi = ref.get('DOI')
    if doi is None:
        continue
    doi = doi.upper()
    d = dois.get(doi)
    if d is None:
        print('DOI {} is missing'.format(doi), file=sys.stderr)
        continue
    c = { "value": d,
            "references": { "P248": "Q5188229", "P854": crossref,
                "P813": datetime.date.today().isoformat() } }
    P2860claims.append(c)
j = {"id": item,
    "claims": { "P2860": P2860claims } }
print(json.dumps(j), flush=True)

