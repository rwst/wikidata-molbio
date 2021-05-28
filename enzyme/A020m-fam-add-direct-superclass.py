
import pronto, six, csv, os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
For every family with referenced molfunc:
    - ignore fams with only narrow mappings
    - having one exact mapping makes fam exact
    - the rest are inexact fams
Output all missing P279 claims. For exact fams, the superfams according to GO,
for inexact fams, one P279 per broad molfunc. IFF they existi AND if it's not
an InterPro subclass. Use with wd ee.
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

print('reading InterPro', file=sys.stderr)
input = gzip.open('interpro.xml.gz')                                   
tree = ET.parse(input)
root = tree.getroot() 
its = {}
for child in root:
    if child.tag == 'interpro':
        its[child.attrib.get('id')] = child
 
ont = pronto.Ontology('/home/ralf/wikidata/go-plus.owl')
for it,flist in funcs.items():
    if it in narrow_only:
        continue
    if it in exact.keys():
        goid = exact.get(it)
        term = ont.get(goid)
        for supterm in term.superclasses(distance=1, with_self=False):
            supit = exgoids.get(supterm.id)
            if supit is None or supit in sups.get(it):
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
        nipr = iprs.get(it)
        if nipr is not None:
            entry = its.get(nipr)
            if entry is None:
                print('not found: {}'.format(nipr), file=sys.stderr)
                exit()
            if any([ch.tag == 'parent_list' for ch in entry]):
                continue
        for goid,mtype in flist:
            if mtype == SKOS_BROAD:
                term = ont.get(goid)
                supit = exgoids.get(goid)
                if supit is None or supit in sups.get(it):
                    continue
                j = {"id": it,
                     "claims": {
                        "P279": { "value": supit,
                            "references": { "P887": "Q94996521"}
                            }
                        }
                    }
                print(json.dumps(j), flush=True)

