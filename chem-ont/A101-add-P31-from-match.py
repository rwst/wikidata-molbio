import csv, os, json, argparse, sys
from rdkit import Chem

"""

"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-Q", "--query1", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-p", "--pattern", help="SMARTS to match")
parser.add_argument("-s", "--smiles", help="SMILES to match")
parser.add_argument("-c", "--classitem", help="WD class item",
        required=True)
#parser.add_argument("-f", "--refstmt", help="WD class item stmt used for reference",
#        required=True)
parser.add_argument("-r", "--refadd", help="output suited for wd ar",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
dontquery1 = not args.query1
script = os.path.basename(sys.argv[0])[:-3]
REF_URL = 'P854'
HEURISTIC = 'P887'
INFERRED_FROM = 'P3452'
IDENTICAL_SMILES = 'Q107494711'


nohit = False
if dontquery is False:
    if args.smiles is not None and len(args.smiles) > 0:
        q = Chem.MolFromSmiles(args.smiles)
        idpat = Chem.MolFromSmiles(args.smiles)
        idsm = Chem.MolToSmiles(idpat, isomericSmiles=False)
        idstereo = len(Chem.FindPotentialStereo(idpat))
        print('{}'.format(idstereo))
        ps = Chem.AdjustQueryParameters()
        ps.adjustDegreeFlags = Chem.AdjustQueryWhichFlags.ADJUST_IGNOREDUMMIES
        pat = [Chem.AdjustQueryProperties(q, ps)]
    elif args.pattern is not None and len(args.pattern) > 0:
        pat = [Chem.MolFromSmarts(args.pattern)]
    else:
        # take SMARTS from class item
        print('querying class item', file=sys.stderr)
        query="""
        SELECT ?smarts
        WHERE
        {{
          wd:{} wdt:P8533 ?smarts.
        }}
        """.format(args.classitem)
        f = open('{}.rq'.format(script), 'w')
        f.write(query)
        f.close()
        ret = os.popen('wd sparql {}.rq >{}.pat'.format(script, script))
        if ret.close() is not None:
            print('classitem has no SMARTS')
            exit()

if args.smiles is None and args.pattern is None:
    with open('{}.pat'.format(script), 'r') as f:
        pat = [ Chem.MolFromSmarts(line.strip()) for line in f.readlines() ]
print('read {} SMARTS pattern(s)'.format(len(pat)))

if dontquery is False:
    c = 0
    its = set()
    reader = csv.DictReader(open('inchi.tsv', 'r'), delimiter='\t')
    for d in reader:
        c = c + 1
        if (c % 50000) == 0:
            print(c)
        iturl = d.get('item')
        it = iturl[iturl.rfind('/')+1:]
        inchi = d.get('inchi')
        mol = Chem.MolFromInchi(inchi)
        if mol is None:
            continue
        for p in pat:
            if mol.HasSubstructMatch(p):
                its.add(it)
                print('--------- {}'.format(it))
                break

    if len(its) == 0:
        exit()

if dontquery is False or dontquery1 is False:
    inp = input("Press y to continue...")
    print('querying {} items...'.format(len(its)))
    query="""
    SELECT DISTINCT ?item
    WHERE
    {{
      VALUES ?item {{ {} }}
      ?item wdt:P703 []
    }}
    """.format("wd:" + " wd:".join(its), args.classitem)
    f = open('{}.rq'.format(script), 'w')
    f.write(query)
    f.close()

    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.hits'.format(script, script))
    if ret.close() is not None:
        exit()

with open('{}.hits'.format(script), 'r') as f:
    its = [ line.strip() for line in f.readlines() ]

nohit = False
if dontquery is False or dontquery1 is False:
    print('querying {} items...'.format(len(its)))
    query="""
    SELECT DISTINCT ?item ?stmt ?ref
    WHERE
    {{
      VALUES ?item {{ {} }}
      {{ ?item wdt:P31 wd:Q11173. }} UNION {{ ?item wdt:P31 wd:Q43460564. }}
      OPTIONAL {{
        ?item p:P31 ?stmt.
        ?stmt ps:P31 wd:{}.
        OPTIONAL {{ ?stmt prov:wasDerivedFrom ?ref }}
        }}
    }}
    """.format("wd:" + " wd:".join(its), args.classitem)
    f = open('{}.rq'.format(script), 'w')
    f.write(query)
    f.close()

    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}1.json'.format(script, script))
    if ret.close() is not None:
        nohit = True

f = open('{}.out'.format(script), 'w')

items = {}
refstmt = set()
if not nohit:
    file = open('{}1.json'.format(script))
    s = file.read()
    jol = json.loads(s)

    for d in jol:
        it = d.get('item')
        st = d.get('stmt')
        ref = d.get('ref')
        i = items.get(it)
        if i is not None:
            print('dbl stmt: {}'.format(it))
            exit()
        items[it] = st
        if ref is not None:
            refstmt.add(st)

ref = { INFERRED_FROM: args.classitem }
for it in items.keys():
    st = items.get(it)
    if st is None:
        # add new stmt
        j = {"id": it,
            "claims": { "P31": [{ 
                "value": args.classitem,
                "references": [ref]
                }]
                } }
        f.write(json.dumps(j) + '\n')
    elif st not in refstmt and args.refadd:
        j = {"guid": st,
                "snaks": ref
            }
        f.write(json.dumps(j) + '\n')

nohit = False
if dontquery is False or dontquery1 is False:
    print('querying {} items...'.format(len(its)), file=sys.stderr)
    query="""
    SELECT DISTINCT ?item ?stmt ?ref
    WHERE
    {{
      VALUES ?item {{ {} }}
      VALUES ?class {{ wd:Q47154513 wd:Q72044356 wd:Q72070508 wd:Q56256086 wd:Q15711994 wd:Q59199015 wd:Q55640664 wd:Q55662747 wd:Q55663030 wd:Q55662548 wd:Q55662456 }}
      ?item wdt:P31 ?class.
      OPTIONAL {{
        ?item p:P279 ?stmt.
        ?stmt ps:P279 wd:{}.
        OPTIONAL {{ ?stmt prov:wasDerivedFrom ?ref }}
        }}
    }}
    """.format("wd:" + " wd:".join(its), args.classitem)
    ff = open('{}.rq'.format(script), 'w')
    ff.write(query)
    ff.close()

    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}2.json'.format(script, script))
    if ret.close() is not None:
        nohit = True

items = {}
refstmt = set()
if not nohit:
    file = open('{}2.json'.format(script))
    s = file.read()
    jol = json.loads(s)

    for d in jol:
        it = d.get('item')
        st = d.get('stmt')
        ref = d.get('ref')
        i = items.get(it)
        if i is not None:
            print('dbl stmt: {}'.format(it))
            exit()
        items[it] = st
        if ref is not None:
            refstmt.add(st)

ref = { INFERRED_FROM: args.classitem }
for it in items.keys():
    st = items.get(it)
    if st is None:
        # add new stmt
        j = {"id": it,
            "claims": { "P279": [{ 
                "value": args.classitem,
                "references": [ref]
                }]
                } }
        f.write(json.dumps(j) + '\n')
    elif st not in refstmt and args.refadd:
        j = {"guid": st,
                "snaks": ref
            }
        f.write(json.dumps(j) + '\n')


