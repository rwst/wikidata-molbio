
import os, json, argparse, sys, datetime, time, csv, datetime

"""
bzcat latest-all.json.bz2 |wikibase-dump-filter --simplify --claim 'P698&P921' |jq '[.id,.claims.P698,.claims.P921]' -c >PMID.ndjson
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--item', action='store', required=True)
parser.add_argument('-p', '--pmc', action='store', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
PMC = args.pmc
item = args.item
script = os.path.basename(sys.argv[0])[:-3]
pmcquery = 'lynx -listonly -dump https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{}/ >{}.txt'.format(PMC,
    script)
ret = os.popen(pmcquery)
if ret.close() is not None:
    raise

lynx = open('{}.txt'.format(script)).readlines()
ii = None
for i in range(len(lynx)):
    if lynx[i].find('scholar.google.com') != -1:
        ii = i
        break
if ii is None:
    print('NO SCHOLAR', file=sys.stderr)
    raise
jj = None
refs = []
for j in range(i-3, len(lynx)):
    if lynx[j].find('twitter.com') != -1:
        jj = j
        break
    if lynx[j].find('https://www.ncbi.nlm.nih.gov/pubmed/') != -1:
        refs.append(lynx[j].strip())
if jj is None:
    print('NO TWITTER', file=sys.stderr)
    raise
print('references received: {}'.format(len(refs)), file=sys.stderr)

pmids = {}
print('reading dump data...', file=sys.stderr)
file = open('PMID.ndjson')
for line in file.readlines():
    arr = json.loads(line.strip())
    qit = arr[0]
    pma = arr[1]
    if len(pma) == 0:
        continue
    pmid = pma[0]
    subj = arr[2]
    if subj is None:
        subj = [] 
    p = pmids.get(pmid)
    if p is None:
        pmids[pmid] = ([qit], subj)
    else:
        p[0].append(qit)
        p[1].extend(subj)

P2860claims = []
pmcurl = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{}'.format(PMC)
for ref in refs:
    pmid = ref[ref.rfind('/')+1:]
    p = pmids.get(pmid)
    if p is None:
        print('PMID {} is missing'.format(pmid), file=sys.stderr)
        continue
    c = { "value": p[0][0],
            "references": { "P248": "Q229883", "P854": pmcurl,
                "P813": datetime.date.today().isoformat() } }
    P2860claims.append(c)
j = {"id": item,
    "claims": { "P2860": P2860claims } }
print(json.dumps(j), flush=True)

