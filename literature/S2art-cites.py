
import os, json, argparse, sys, datetime, time, csv, urllib
import urllib.request as ureq
from curses import wrapper

"""
bzcat latest-all.json.bz2 |wikibase-dump-filter --simplify --claim 'P356' |jq '[.id,.claims.P356]' -c >DOI.ndjson
or use wdumper
"""
def S2_wait():
    time.sleep(3.5)

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

next_ = 0
ctr = 0
reflist = []
while next_ is not None:
    ctr = ctr + 1
    #url = 'http://13.249.98.31/graph/v1/paper/{}/references?fields=title,externalIds&offset={}'.format(DOI, next_)
    url = 'https://api.semanticscholar.org/graph/v1/paper/{}/references?fields=title,externalIds&offset={}'.format(DOI, next_)
    print('{}: contacting S2 for {} ({})'.format(ctr, DOI, next_), file=sys.stderr)
    resp = None
    try:
        with ureq.urlopen(url) as f:
            resp = f.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(e)
        pass
    S2_wait()
    if resp is None:
        print("response FAIL", file=sys.stderr)
        exit(0)
    data = json.loads(resp)
    offs = data.get('offset')
    next_ = data.get('next')
    d = data.get('data')
    if d is None:
        print("data FAIL: {}".format(data), file=sys.stderr)
        exit(0)
    for p in d:
        citingPaper = p.get('citedPaper')
        e = citingPaper.get('externalIds')
        if e is None:
            continue
        reflist.append(e)

print('references received: {}'.format(len(reflist)), file=sys.stderr)

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
    missing.add(doi)

if nodoi > 0:
    print('{} references without DOI received'.format(nodoi), file=sys.stderr)

inp = ''
while len(missing) > 0 and inp != 'y':
    print('querying {} missing DOIs'.format(len(missing)), file=sys.stderr)
    query="""
    SELECT DISTINCT ?item ?doi
    WHERE
    {{
      VALUES ?art {{ wd:Q580922 wd:Q13442814 }}
      VALUES ?doi {{ '{}' }}
      ?item wdt:P31 ?art.
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
            "references": { "P248": "Q22908627", "P854": url,
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

