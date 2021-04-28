
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Compare en labels on GO items and output a line if different in GO
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

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

print('reading GO')
ont = pronto.Ontology('go-plus.owl')
for d in jol:
    goid = d.get('goid')
    it = d.get('item')
    lab = d.get('label')
    term = ont.get(goid)
    if term is None:
        print("CAN'T HAPPEN: {}".format(goid))
        exit()
    if lab != term.name:
        print('{} {}---{}'.format(it, lab, term.name))

