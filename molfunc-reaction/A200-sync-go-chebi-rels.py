
import os, json, argparse, sys, datetime, time
import pronto, six

"""
Intended to add stmts with qual "subj/obj has role" on GO/ChEBI items.

The relevant data to sync is in these lines in the Gene Ontology:
intersection_of: PROPERTY CHEBI:

where PROPERTY is one of:
has_input
has_intermediate
has_output
has_participant
has_primary_input
has_primary_input_or_output
has_primary_output
process_has_causal_agent
regulates_levels_of
exports
imports
transports_or_maintains_localization_of

To check this list:
wget https://raw.githubusercontent.com/geneontology/go-ontology/master/src/ontology/go-edit.obo
grep ^in.*CHEBI /home/ralf/go-ontology/src/ontology/go-edit.obo |sed 's+ CHEB.*++g' |sort|uniq

Use stdout with wd ee.
"""
GOREF = "Q112968510"   

def ensure(subit, obit, role, prop):
#    print('ensure {} {}'.format(subit, obit), file=sys.stderr)
    ss = gstmts.get(subit)
    qprop = 'P3831'
    if prop == 'P361':
        ss = cstmts.get(subit)
        qprop = 'P2868'
    if ss is not None:
        os = ss.get(obit)
        if os is not None:
            if os[1] is not None:
                return
            # add ref to stmt
            j = {"id": subit, "claims": { prop: [{ "id": os[0],
                "value": obit,
                "qualifiers": { qprop: role },
                "references": { "P248": GOREF }}] } }
            print(json.dumps(j), flush=True)
            return
    # create stmt
    j = {"id": subit, "claims": { prop: [{ "value": obit,
        "qualifiers": { qprop: role },
        "references": { "P248": GOREF }}] } }
    print(json.dumps(j), flush=True)


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

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq1 >{}.json1'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json1'.format(script))
s = file.read()
jol = json.loads(s)

goits = {}
gstmts = {}
cstmts = {}
for d in jol:
    item = d.get('item')
    goid = d.get('goid')
    goits[goid] = item
    s = gstmts.get(item)
    obj = d.get('obj')
    tup = (d.get('stmt'), d.get('ref'), d.get('orole'))
    if s is not None:
        if s.get(obj) is not None:
            print('CANT HAPPEN: {} {}'.format(item, obj), file=sys.stderr)
            exit()
        s[obj] = tup
    else:
        gstmts[item] = { obj : tup }

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq2 >{}.json2'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json2'.format(script))
s = file.read()
jol = json.loads(s)

chdups = set()
chits = {}
for d in jol:
    item = d.get('item')
    chid = d.get('chid')
    ch = chits.get(chid)
    if ch is not None and ch != item:
        chdups.add(ch)
    chits[chid] = item
    s = cstmts.get(item)
    obj = d.get('obj')
    tup = (d.get('stmt'), d.get('ref'), d.get('srole'))
    if s is not None:
        s[obj] = tup
    else:
        cstmts[item] = { obj : tup }

print('Reading GO', file=sys.stderr)
ont = pronto.Ontology('/home/ralf/wikidata/go-edit.obo')

for term in ont.terms():
    goid = term.id
    if not goid.startswith('GO:'):
        continue
    goit = goits.get(goid)
    if goit is None:
        continue
    try:
        if len(term.intersection_of) == 0:
            continue
        term2 = None
        for i in term.intersection_of:
            if (not type(i) is tuple) or (not type(i[0]) is pronto.Relationship):
                term2 = i
                continue
            else:
                term1 = i
        chid = term1[1].id
        if not chid.startswith('CHEBI:'):
            continue
        chid = chid[6:]
        chit = chits.get(chid)
        if chid in chdups:
            print('CANT HAPPEN: CHEBI:{}'.format(chid), file=sys.stderr)
            exit()
        if chit is None:
            continue
        type_ = term1[0].name
        #print(goid, chit, type_, term2, file=sys.stderr)
        
        if (type_ == 'has output'
        or type_ == 'has primary output'):
            ensure(goit, chit, 'Q542929', 'P527')
            ensure(chit, goit, 'Q542929', 'P361')
        if (type_ == 'has input'
        or type_ == 'has primary input'):
            if term2.name.find('transport') >= 0:
                ensure(goit, chit, 'Q75152245', 'P527')
                ensure(chit, goit, 'Q75152245', 'P361')
            else:
                ensure(goit, chit, 'Q45342565', 'P527')
                ensure(chit, goit, 'Q45342565', 'P361')
        if type_ == 'has intermediate':
            ensure(goit, chit, 'Q7458208', 'P527')
            ensure(chit, goit, 'Q7458208', 'P361')
        if (type_ == 'has participant'
        or type_ == 'has primary input or output'):
            ensure(goit, chit, 'Q75232720', 'P527')
            ensure(chit, goit, 'Q75232720', 'P361')
        if (type_ == 'transports or maintains localization_of'
        or type_ == 'exports'
        or type_ == 'imports'):
            ensure(goit, chit, 'Q75152245', 'P527')
            ensure(chit, goit, 'Q75152245', 'P361')
        if type_ == 'regulates levels of':
            ensure(goit, chit, 'Q7247312', 'P527')
            ensure(chit, goit, 'Q7247312', 'P361')
        if type_ == 'process has causal agent':
            ensure(goit, chit, 'Q2574811', 'P527')
            ensure(chit, goit, 'Q2574811', 'P361')
    except KeyError:
        pass

