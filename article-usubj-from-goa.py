
import os, json, argparse, sys, datetime, time, csv

"""
bzcat latest-all.json.bz2 |wikibase-dump-filter --simplify --claim 'P698&P921' |jq '[.id,.claims.P698,.claims.P921]' -c >PMID.ndjson
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument('-t', '--taxon', action='store', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
taxon = args.taxon
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    query = """
    SELECT DISTINCT ?item ?upid
    {{
      ?item wdt:P703 wd:{}.
      ?item wdt:P352 ?upid
    }}
    """.format(taxon)
    f = open('{}.rq'.format(script), 'w')
    f.write(query)
    f.close()

    print('performing query... on taxon {}'.format(taxon))
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

uids = {}
for d in jol:
    item = d.get('item')
    upid = d.get('upid')
    g = uids.get(upid)
    if g is None:
        uids[upid] = item
    else:
        print('CANT HAPPEN: {} {}'.format(item, g))
        raise

pmids = {}
print('reading dump data...')
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

upids = {}
print('Reading GOA data')
reader = csv.DictReader(open('goa-pmid.tsv', 'r'), delimiter='\t')
for item in reader:
    ref = item.get('ref')
    if not ref.startswith('PMID'):
        continue
    pmid = ref[5:]
    upid = item.get('id')
    if upid not in uids.keys():
        continue
    u = upids.get(pmid)
    if u is None:
        upids[pmid] = [upid]
    else:
        u.append(upid)

for pmid in upids.keys():
    p = pmids.get(pmid)
    if p is None:
        print('PMID {} is missing'.format(pmid))
        continue
    upidarr = set(upids.get(pmid))
    if len(upidarr) > 14:
        continue
    for upid in upidarr:
        upit = uids.get(upid)
        if upit is None:
            print('UniProt:{} is missing'.format(upid))
            continue
        pmits,pmsbj = p
        if upit in pmsbj:
            continue
        if QS:
            print('{}|P921|{}|S248|Q96105165'.format(min(pmits), upit))
        else:
            j = {"id": min(pmits),
                "claims": {
                     "P921": { "value": upit,
                         "references": { "P248": "Q96105165"} },
                        }
                    }
            f = open('t.json', 'w')
            f.write(json.dumps(j))
            f.close()
            print(json.dumps(j), flush=True)
            ret = os.popen('wd ee t.json --summary article-usubj-from-goa')
            print(ret.read())
            if ret.close() is not None:
                print('ERROR')
