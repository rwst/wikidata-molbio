
import pronto, six, csv, os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
For every family with referenced molfunc:
    - ignore fams with only narrow mappings
    - having one exact mapping makes fam exact
    - the rest are inexact fams
Output all molfuncs that have no items, sorted by most needed first.
If -c option given, output commands suitable as input to wd ce -b.
CHECK THE LABELS OF THIS OUTPUT. 
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-c", "--create", help="print commands for item creation",
        default = 0, type = int)

# Read arguments from the command line
args = parser.parse_args()
MAPPING_TYPE = 'P4390'
SKOS_EXACT = 'Q39893449'
SKOS_BROAD = 'Q39894595'

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

print('reading InterPro', file=sys.stderr)
input = gzip.open('interpro.xml.gz')                                   
tree = ET.parse(input)
root = tree.getroot() 
its = {}
for child in root:
    if child.tag == 'interpro':
        its[child.attrib.get('id')] = child

count = {}
ont = pronto.Ontology('/home/ralf/wikidata/go-plus.owl')
for it,flist in funcs.items():
    if it in narrow_only:
        continue
    if it in exact.keys():
        goid = exact.get(it)
        term = ont.get(goid)
        for supterm in term.superclasses(distance=1, with_self=False):
            supit = exgoids.get(supterm.id)
            if supit is None:
                tup = (supterm.id,supterm.name)
                t = count.get(tup)
                if t is None:
                    count[tup] = 1
                else:
                    count[tup] = t+1
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
                if supit is None:
                    tup = (goid,term.name)
                    t = count.get(tup)
                    if t is None:
                        count[tup] = 1
                    else:
                        count[tup] = t+1


if args.create > 0:
    goids = [tup[0][0] for tup in count.items() if tup[1] >= args.create]
    if dontquery is False:
        query = """
        SELECT ?item ?goid
        WHERE
        {{
          VALUES ?goid {{ '{}' }}
          ?item wdt:P31 wd:Q14860489.
          ?item wdt:P686 ?goid.
        }}
        """.format("' '".join(goids))
        f = open('{}-2.rq'.format(script), 'w')
        f.write(query)
        f.close()

        print('performing query... ', file=sys.stderr)
        ret = os.popen('wd sparql {}-2.rq >{}-2.json'.format(script, script))
        if ret.close() is not None:
            raise
    file = open('{}-2.json'.format(script))
    s = file.read()
    jol = json.loads(s)
    goits = {}
    for d in jol:
        goits[d.get('goid')] = d.get('item')

for tu,c in sorted(count.items(), key=lambda tup: tup[1], reverse=True):
    if args.create < 1:
        print('{}: {}'.format(c, tu))
    else:
        if c < args.create:
            continue
        goid,goname = tu
        typ = 'p'
        if goname.find('activity'):
            label = goname.replace(' activity', '')
        if goname[-8:] == ' binding':
            label = (goname + ' protein').replace(' ion', '')
        if label[-3:] == 'ase':
            typ = 'e'
        if typ == 'e':
            desc = {"en": "class of enzymes",
                "de": "Enzymklasse", "fr": "famille d'enzymes"}
            val = 'Q67015883'
        else:
            desc = {"en": "class of proteins", "de": "Proteinklasse"}
            val = 'Q84467700'
        j = {"labels": { "en": label },
            "descriptions": desc,
            "claims": {
                 "P31": { "value": val,
                     "references": { "P3452": ["Q82799", "Q14860489"] } },
                 "P680": { "value": goits.get(goid),
                     "qualifiers": { MAPPING_TYPE: SKOS_EXACT },
                     "references": { "P3452": "Q82799" },
                    }
                }
            }
        print(json.dumps(j), flush=True)

