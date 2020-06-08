
import os, json, argparse, sys, datetime, time
import pronto, six

"""
bzcat latest-all.json.bz2 |wikibase-dump-filter --simplify --claim 'P698&P921' |jq '[.id,.claims.P698,.claims.P921]' -c >PMID.ndjson
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

print('Reading ChEBI')
ont = pronto.Ontology('chebi.obo')

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

dups_with_pmid = False
for d in jol:
    chebid = 'CHEBI:' + d.get('value').get('value')
    items = d.get('items')
    lab = d.get('itemLabels')
    term = ont.get(chebid)
    if any(xref.id.startswith('PMID') for xref in term.xrefs):
        dups_with_pmid = True
        print('{} items:{} |{}|'.format(chebid, items, lab))
if dups_with_pmid:
    print('!!!')

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq1 >{}1.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}1.json'.format(script))
s = file.read()
jol = json.loads(s)

chebits = {}
for d in jol:
    item = d.get('item')
    chebid = 'CHEBI:' + d.get('chebi')
    chebits[chebid] = item

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

blacklist = []
for chebid in chebits.keys():
    if chebid in blacklist:
        continue
    term = ont.get(chebid)
    if term is None or term.obsolete:
        print("CAN'T HAPPEN: {}".format(chebid))
        continue
    chebit = chebits.get(chebid)
    pms = []
    if term.definition is not None and term.xrefs is not None:
        for xref in term.xrefs:
            if xref.id.startswith('PMID'):
                pms.append(xref.id[5:])
    for pmid in pms:
        p = pmids.get(pmid)
        if p is None:
            print('PMID {} is missing'.format(pmid))
            continue
        pmits,pmsbj = p
        if chebit in pmsbj:
            continue
        if QS:
            print('{}|P921|{}|S248|Q95689128|S683|"{}"'.format(min(pmits), chebit, chebid[6:]))
        else:
            j = {"id": min(pmits),
                "claims": {
                     "P921": { "value": chebit,
                         "references": { "P248": "Q95689128", "P683": chebid[6:]} },
                        }
                    }
            f = open('t.json', 'w')
            f.write(json.dumps(j))
            f.close()
            print(json.dumps(j), flush=True)
            ret = os.popen('wd ee t.json --summary article-subj-from-chebi')
            print(ret.read())
            if ret.close() is not None:
                print('ERROR')
