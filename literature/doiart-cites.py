
import os, json, argparse, sys, datetime, time, csv, datetime
import urllib.request as ureq
from curses import wrapper

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
nodoi = 0
missing = set()
for ref in reflist:
    doi = ref.get('DOI')
    if doi is None:
        nodoi = nodoi + 1
        continue
    doi = doi.upper()
    if doi[len(doi)-1:] == '.':
        doi = doi[:-1]
    d = dois.get(doi)
    if d is None:
        missing.add(doi)
        continue
    c = { "value": d,
            "references": { "P248": "Q5188229", "P854": crossref,
                "P813": datetime.date.today().isoformat() } }
    P2860claims.append(c)

if nodoi > 0:
    print('{} references without DOI received'.format(nodoi), file=sys.stderr)

inp = ''
while len(missing) > 0 and inp != 'y':
    print('querying {} missing DOIs'.format(len(missing)), file=sys.stderr)
    query="""
    SELECT ?item ?doi
    WHERE
    {{
      VALUES ?doi {{ '{}' }}
      ?item wdt:P31 wd:Q13442814.
      ?item wdt:P356 ?doi.
    }}
    """.format("' '".join(missing))
    f = open('{}-1.rq'.format(script), 'w')
    f.write(query)
    f.close()

    print('performing query... ', file=sys.stderr)
    ret = os.popen('wd sparql {}-1.rq >{}-1.json'.format(script, script))
    time.sleep(5)
    f = open('{}-1.json'.format(script))
    s = ''
    s = f.read()
    f.close()
    jol = []
    try:
        jol = json.loads(s)
    except json.JSONDecodeError:
        pass
    for d in jol:
        c = { "value": d.get('item'),
            "references": { "P248": "Q5188229", "P854": crossref,
                "P813": datetime.date.today().isoformat() } }
        P2860claims.append(c)
        missing.remove(d.get('doi'))
    for doi in missing:
        print('{}'.format(doi))
    inp = input("Press y to continue...")

j = {"id": item,
    "claims": { "P2860": P2860claims } }
f = open('{}.out'.format(script), 'w')
f.write(json.dumps(j))
f.close()

