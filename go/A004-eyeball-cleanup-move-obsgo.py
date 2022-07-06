
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Print list of obsolete item + possible nonobsolete superclasses.
Chose best superclass, remove alternative lines.
Result will be fed to A005 for automatic move.
"""
def collect(parent_dir, it, the_set):
    if it not in parent_dir.keys():
        the_set.add(it)
        return
    pset = parent_dir.get(it)
    if pset is not None:
        for p in pset:
            collect(parent_dir, p, the_set)

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
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True, file=sys.stderr)

obsoletes = set()
parents = {}
labels = {}
for d in jol:
    i = d.get('item')
    iv = i.get('value')
    obsoletes.add(iv)
    il = i.get('label')
    l = labels.get(iv)
    if l is None:
        labels[iv] = il
    p = d.get('parent')
    if p is not None and len(p) > 0:
        pv = p.get('value')
        pl = p.get('label')
        l = labels.get(pv)
        if l is None:
            labels[pv] = pl
        p = parents.get(iv)
        if p is None:
            parents[iv] = set([pv])
        else:
            p.add(pv)

l = []
for o in parents.keys():
    the_set = set()
    try:
        collect(parents, o, the_set)
    except RecursionError:
        pass
    if len(the_set) == 0:
        print(o, file=sys.stderr)
        continue
        #exit()
    if type(the_set) == 'str':
        raise
    for p in the_set:
        l.append('{}|{}| {} | {}'.format(o, p, labels.get(o), labels.get(p)))

for line in sorted(l):
    print(line)

