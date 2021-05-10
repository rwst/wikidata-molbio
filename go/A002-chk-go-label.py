
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Compare en labels on GO items and output a line if different in GO
First add items to blacklist, run -w for use with wd sl.
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-w", "--write", help="write lines for use with wd sl",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True, file=sys.stderr)

blacklist = ['Q1057', 'Q2996394', 'Q211935', 'Q22279621', 'Q3346925', 'Q14819852',
        'Q14860489', 'Q2792936', 'Q6921783', 'Q14860372', 'Q13416689', 'Q22327418',
        'Q5058355']
print('reading GO', file=sys.stderr)
ont = pronto.Ontology('go-plus.owl')
for d in jol:
    goid = d.get('goid')
    it = d.get('item')
    if it in blacklist:
        continue
    lab = d.get('label')
    term = ont.get(goid)
    if term is None:
        print("CAN'T HAPPEN: {}".format(goid), file=sys.stderr)
        exit()
    if lab != term.name:
        if args.write:
            print('{} en "{}"'.format(it, term.name))
        else:
            print('{} {}---{}'.format(it, lab, term.name))

