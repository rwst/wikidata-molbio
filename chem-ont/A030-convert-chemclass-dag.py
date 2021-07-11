
import csv, os, json, argparse, sys

"""
Print tree of proper chemclasses
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

items = {}
labels = {}
for d in jol:
    dd = d.get('item')
    it = dd.get('value')
    lab = dd.get('label')
    sup = d.get('super')
    i = items.get(it)
    if i is not None:
        i.append(sup)
    else:
        items[it] = [sup]
    labels[it] = lab
items['Q2393187'] = 'Q43460564'
labels['Q2393187'] = 'molecular entity'
labels['Q43460564'] = 'chemical entity'

edges = {}
for it,itsuplist in items.items():
    for sup in itsuplist:
        if sup in set(items.keys()).union(set(['Q43460564'])):
            e = edges.get(sup)
            if e is None:
                edges[sup] = set([it])
            else:
                e.add(it)

seen = set()
def walk(E, edges, prefix):
    pfix = '├──'
    if E in seen:
        pfix = '╞══'
    print('{}[[{}]] {}'.format(prefix + pfix, E, labels.get(E)))
    if E in seen and edges.get(E) is not None:
        print(prefix + '... see above')
        return
    seen.add(E)
    children = edges.get(E)
    prefix = ' │   ' + prefix
    if len(prefix) > 50 or children is None:
        return
    for c in sorted(children, key=lambda c: labels.get(c)):
        walk(c, edges, prefix)

walk('Q43460564', edges, ' ')

