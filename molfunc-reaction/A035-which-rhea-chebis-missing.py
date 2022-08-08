
import os, json, argparse, sys, datetime, time
import pronto, six, rdflib

"""
Getting Rhea xrefs from GO functions, check which CHEBIs are referred to from rhea.rdf
Print list of missing CHEBIs for usage in chebi/A100-missing-chebi-compound.py --subset
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

rheas = set()
if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq1 >{}.json1'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json1'.format(script)) as file:
    for line in file.readlines():
        line = line.rstrip()
        if not line.startswith('https://www.rhea-db.org/rhea/'):
            continue
        rhea = line[line.rfind('/rhea/')+6:]
        rheas.add(rhea)

chebis = set()
if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq2 >{}.json2'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json2'.format(script)) as file:
    for line in file.readlines():
        line = line.rstrip()
        chebis.add(line)

print('Reading Rhea', file=sys.stderr)
rhea = rdflib.Graph()
rhea.parse("/home/ralf/wikidata/rhea.rdf") 

missing = set()
for r in rheas:
    rhearef = 'RHEA:' + r
    qres = rhea.query("""PREFIX rh:<http://rdf.rhea-db.org/>
SELECT DISTINCT ?item ?prset ?acc
WHERE {{
    ?item rh:accession '{}' .
    ?item rh:bidirectionalReaction ?breac .
    ?breac rh:substratesOrProducts ?prset .
    ?prset rh:contains ?partcp .
    ?partcp rh:compound ?comp .
    ?comp rh:accession ?acc
}}""".format(rhearef))
    for row in qres:
        if not str(row[2]).startswith('CHEBI:'):
            continue
        chebid = str(row[2])[6:]
        if chebid not in chebis:
            missing.add(chebid)

print('Missing: {}'.format(len(missing)), file=sys.stderr)
for m in missing:
    print(m)

