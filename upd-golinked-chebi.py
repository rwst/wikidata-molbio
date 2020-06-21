
import os, json, argparse, sys, datetime, time
import pronto, six

"""
grep CHEBI: /home/ralf/go-ontology/src/ontology/go-edit.obo |sed 's/^.*CHEBI:\([0-9]\+\).*$/\1/g' |sort|uniq
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

gochebis = set()
with open('go-chebis') as file:
    for line in file.readlines():
        gochebis.add(line.strip())

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

print('Reading ChEBI')
ont = pronto.Ontology('chebi.obo')

obsgo = set()
for ch in gochebis:
    chebid = 'CHEBI:' + ch
    term = ont.get(chebid)
    if term is None:
        obsgo.add(ch)
        print('obsolete in GO: {}'.format(chebid))

wdchebis = set()
for d in jol:
    chebid = 'CHEBI:' + d.get('chebid')
    term = ont.get(chebid)
    if term is None:
        print('obsolete in WD: {}'.format(chebid))
        continue
    wdchebis.add(d.get('chebid'))

res = gochebis.difference(obsgo).difference(wdchebis)
if len(res) > 0:
    print('missing: {}'.format(res))

iks = {}
for ch in res:
    term = ont.get('CHEBI:' + ch)
    xref = term.xrefs
    if xref is None or len(xref) == 0:
        continue
    l = [i.split()[1] for i in xref if i[:45] == 'http://purl.obolibrary.org/obo/chebi/inchikey']
    if len(l) > 0:
        iks[l[0]] = ch
    else:
        print('not found in ChEBI: {}'.format(ch))

if len(iks) == 0:
    print('nothing to do')
    exit()

query = """
SELECT DISTINCT ?item ?ik
{{
    VALUES ?iks {{ {} }}
    ?item wdt:P235 ?iks .
    ?item wdt:P235 ?ik .
}}
""".format(' '.join(iks.keys()))
f = open('t.rq', 'w')
f.write(query)
f.close()

print('performing query...')
ret = os.popen('wd sparql t.rq >t.json')
if ret.close() is not None:
    raise
file = open('t.json')
s = file.read()
jol = json.loads(s)

found = set()
for d in jol:
    item = d.get('item')
    ik = d.get('ik')
    print('{}|P683|{}'.format(item, iks.get(ik)))
    found.add(iks.get(ik))

print(res.difference(found))
