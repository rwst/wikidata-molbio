
import pronto, six, csv, os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
UPDATE class-subclass.json before starting!

For every family with referenced molfunc:
    - ignore fams with only narrow mappings
    - having one exact mapping makes fam exact
    - the rest are inexact fams
Output all missing P279 claims. For exact fams, the superfams according to GO,
for inexact fams, one P279 per broad molfunc. IFF they exist AND iff an existing
P279 stmt isn't more specific (checked by loading the subclass tree). Use with wd ee.
"""
# Walk reverse ontology subgraph (root = hitem) upwards, depth first.
# Return True if citem is encountered (i.e. citem is superclass of hitem)
def walk_find(sitems, hitem, citem):
    try:
        ch = sitems.get(hitem)
        # print('{} {} {}'.format(hitem, citem, ch))
        if ch is None:
            return False
        if citem in ch:
            return True
        for c in ch:
            if walk_find(sitems, c, citem):
                return True
        return False
    except RecursionError:
        print((hitem, citem))
        raise

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
MAPPING_TYPE = 'P4390'
SKOS_EXACT = 'Q39893449'
SKOS_BROAD = 'Q39894595'

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

exact = {}
exgoids = {}
funcs = {}
iprs = {}
for d in jol:
    it = d.get('item')
    goid = d.get('goid')
    mtype = d.get('skos')
    ipr = d.get('ipr')
    if mtype == SKOS_EXACT:
        exact[it] = goid
        g = exgoids.get(goid)
        if g is None:
            exgoids[goid] = it
        else:
            raise
    f = funcs.get(it)
    if f is None:
        funcs[it] = [(goid, mtype)]
    else:
        f.append((goid, mtype))
    if ipr is not None and len(ipr) > 0:
        i = iprs.get(it)
        if i is None:
            iprs[it] = ipr
        elif i != ipr:
            print('{}: {} {}'.format(it, ipr, i))
            raise

#print(exgoids.get("GO:0004459"), file=sys.stderr)

narrow_only = set()
for it,flist in funcs.items():
    if all([mtype == 'Q39893967' for goid,mtype in flist]):
        narrow_only.add(it)

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq1 >{}.json1'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json1'.format(script))
s = file.read()
jol = json.loads(s)

sups = {}
suprefs = set()
for d in jol:
    it = d.get('item')
    sup = d.get('super')
    supref = d.get('supref')
    if supref is not None and len(supref) > 0:
        suprefs.add((it, sup))
    s = sups.get(it)
    if s is None:
        sups[it] = [sup]
    else:
        s.append(sup)

childs = {}
sitems = {}
# filling subclass structure
with open('class-subclass.json', 'r') as f:
    print('reading superclass data', file=sys.stderr)
    s = f.read()
    jol = json.loads(s)

for d in jol:
    it = d.get('item')
    sup = d.get('super')
    i = sitems.get(it)
    if i is not None:
        i.append(sup)
    else:
        sitems[it] = [sup]
    c = childs.get(sup)
    if c is not None:
        c.append(it)
    else:
        childs[sup] = [it]

#print(walk_find(sitems, 'Q24721492', 'Q409464'))
#print(walk_find(sitems, 'Q409464', 'Q24721492'))

ont = pronto.Ontology('/home/ralf/wikidata/go.obo')
for it,flist in funcs.items():
    if it in narrow_only:
        continue
    if it in exact.keys():
        goid = exact.get(it)
        term = ont.get(goid)
        for supterm in term.superclasses(distance=1, with_self=False):
            supit = exgoids.get(supterm.id)
            if supit is None or supit in sups.get(it)\
            or walk_find(sitems, it, supit):
                continue
            j = {"id": it,
                 "claims": {
                    "P279": { "value": supit,
                        "references": { "P887": "Q94996521"}
                        }
                    }
                }
            print(json.dumps(j), flush=True)
    else:
        for goid,mtype in flist:
            #if it == "Q24721492":
            #    print((goid,mtype), file=sys.stderr)
            if mtype == SKOS_BROAD:
                #term = ont.get(goid)
                supit = exgoids.get(goid)
                if supit is None or supit in sups.get(it)\
                or walk_find(sitems, it, supit):
                    continue
                j = {"id": it,
                     "claims": {
                        "P279": { "value": supit,
                            "references": { "P887": "Q94996521"}
                            }
                        }
                    }
                print(json.dumps(j), flush=True)

