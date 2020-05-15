
import csv, os, json, argparse, sys, rdflib

"""
For all EC statements with obsolete EC: deprecate deleted entries,
change transferred entries by deleting and creating new without mapping.
Needs the current ftp://ftp.ebi.ac.uk/pub/databases/intenz/enzyme/enzyme.rdf
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
ndate = '2020-04-22'
newd = ndate + 'T00:00:00Z'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

g = rdflib.Graph()
print('Loading Enzyme')
g.load('file:///home/ralf/wikidata/enzyme.rdf')
qres = g.query( 
    """PREFIX up: <http://purl.uniprot.org/core/>
    SELECT DISTINCT ?a ?b
    WHERE { 
    ?a up:obsolete true .
    OPTIONAL { ?a up:replacedBy ?b }
    }""")
obs = {}
for row in qres:
    a = row.a
    ec = a[a.rfind('/')+1:] 
    b = row.b 
    if b is None: 
        obs[ec] = ''
    else: 
        obs[ec] = b[b.rfind('/')+1:]        

for d in jol:
    qit = d.get('p')
    stmt = d.get('stmt')
    ec = d.get('ec')
    rank = d.get('rank')
    repl = obs.get(ec)
    if repl is None or rank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    if len(repl) == 0:
        print('Is {} obsolete?'.format(qit))
    if QS:
        print('-{}|P591|"{}"'.format(qit, ec))
        if len(repl) > 0:
            print('{}|P591|"{}"|S248|Q26737758|S813|+{}/11'.format(qit, repl, newd))
    else:
        p591 = [{"id":stmt, "value":ec, "rank":"deprecated",
            "qualifiers":
                    {"P2241":"Q67125514"},
            "references":
                    { "P248": "Q26737758", "P813": ndate },
                }]
        if len(repl) > 0:
            p591.append({"value":repl,
                        "references":
                            { "P248": "Q26737758", "P813": ndate } })
        j = {"id": qit,
            "claims": {"P591": p591}
                }
        f = open('t.json', 'w')
        f.write(json.dumps(j))
        f.close()
        print(json.dumps(j), flush=True)
        ret = os.popen('wd ee t.json --summary all-depr-obsolete-ec')
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
