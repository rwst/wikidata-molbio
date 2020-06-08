
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

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

goids = {}
for d in jol:
    item = d.get('item')
    goid = d.get('goid')
    g = goids.get(goid)
    if g is None:
        goids[goid] = item
    else:
        print('CANT HAPPEN: {}'.format(item))
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

blacklist = ['GO:0000115']
ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
for goid in goids.keys():
    if goid in blacklist:
        continue
    goit = goids.get(goid)
    term = ont.get(goid)
    if term is None or term.obsolete:
        print("CAN'T HAPPEN: {}".format(goid))
        continue
    pms = []
    if term.definition is not None and term.definition.xrefs is not None:
        for xref in term.definition.xrefs:
            if xref.id.startswith('PMID'):
                pms.append(xref.id[5:])
    if term.synonyms is not None:
        for syn in term.synonyms:
            if syn.scope == 'EXACT' or syn.scope == 'NARROW':
                for xref in syn.xrefs:
                    if xref.id.startswith('PMID'):
                        pms.append(xref.id[5:])
    for pmid in pms:
        p = pmids.get(pmid)
        if p is None:
            #print('PMID {} is missing'.format(pmid))
            continue
        pmits,pmsbj = p
        if goit in pmsbj:
            continue
        if QS:
            print('{}|P921|{}|S248|Q93741199|S686|{}'.format(min(pmits), goit, goid))
        else:
            j = {"id": min(pmits),
                "claims": {
                     "P921": { "value": goit,
                         "references": { "P248": "Q93741199", "P686": goid} },
                        }
                    }
            f = open('t.json', 'w')
            f.write(json.dumps(j))
            f.close()
            print(json.dumps(j), flush=True)
            ret = os.popen('wd ee t.json --summary article-subj-from-goref')
            print(ret.read())
            if ret.close() is not None:
                print('ERROR')
