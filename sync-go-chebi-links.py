
import os, json, argparse, sys, datetime, time
import pronto, six

"""
grep ^in.*CHEBI /home/ralf/go-ontology/src/ontology/go-edit.obo |sed 's+ CHEB.*++g' |sort|uniq

The relevant data to sync is in these lines in the Gene Ontology:
intersection_of: PROPERTY CHEBI:

where PROPERTY is one of:
has_part --> has part 
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
"""
wdeecnt = 0
def wdee(j):
    global wdeecnt
    wdeecnt = wdeecnt + 1
#    if wdeecnt > 10:
#        exit()
    f = open('t.json', 'w')
    f.write(json.dumps(j))
    f.close()
    print(json.dumps(j), flush=True)
    ret = os.popen('wd ee t.json')
    print(ret.read())
    if ret.close() is not None:
        print('ERROR')

def ensure(subit, obit, role, prop):
    print('ensure {} {}'.format(subit, obit))
    GOREF = "Q93741199"   
    ss = stmts.get(subit)
    qprop = 'P3831'
    if prop == 'P361':
        qprop = 'P2868'
    if ss is not None:
        os = ss.get(obit)
        if os is not None and os[0] == prop:
            if ((os[2] is not None) or
                (role is None and (os[3] is not None or os[4] is not None))):
                return
            if role is None:
                # add ref to stmt
                j = {"id": subit, "claims": { prop: [{ "id": os[1],
                    "value": obit,
                    "references": { "P248": GOREF }}] } }
                wdee(j)
                return
            # add ref to stmt
            j = {"id": subit, "claims": { prop: [{ "id": os[1],
                "value": obit,
                "qualifiers": { qprop: role },
                "references": { "P248": GOREF }}] } }
            wdee(j)
            return
    # create stmt
    if role is None:
        j = {"id": subit, "claims": { prop: [{ "value": obit,
            "references": { "P248": GOREF }}] } }
    else:
        j = {"id": subit, "claims": { prop: [{ "value": obit,
            "qualifiers": { qprop: role },
            "references": { "P248": GOREF }}] } }
    wdee(j)


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
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

chits = {}
goits = {}
stmts = {}
for d in jol:
    item = d.get('item')
    chid = d.get('chid')
    goid = d.get('goid')
    if (chid is None) == (goid is None):
        print('CANT HAPPEN: {}'.format(chid))
        exit()
    if chid is not None:
        chits[chid] = item
    else:
        goits[goid] = item
    prop = d.get('prop')
    if prop is not None:
        prop = prop[prop.rfind('/')+1:]
        s = stmts.get(item)
        obj = d.get('obj')
        tup = (prop, d.get('stmt'), d.get('ref'),
                d.get('srole'), d.get('orole'))
        if s is not None:
            if s.get(obj) is not None:
                if s.get(obj)[1] == tup[1]:
                    continue
                print('CANT HAPPEN: {} {}'.format(item, obj))
                exit()
            s[obj] = tup
        else:
            stmts[item] = { obj : tup }

print('Reading GO')
ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')

for term in ont.terms():
    goid = term.id
    if not goid.startswith('GO:'):
        continue
    goit = goits.get(goid)
    if goit is None:
        continue
    try:
        for i in term.intersection_of:
            if (not type(i) is tuple) or (not type(i[0]) is pronto.Relationship):
                continue
            chid = i[1].id
            if not chid.startswith('CHEBI:'):
                continue
            chid = chid[6:]
            chit = chits.get(chid)
            if chit is None:
                continue
            type_ = i[0].name
            print(goid, chit, type_)
            
            if (type_ == 'has output'
            or type_ == 'has primary output'):
                ensure(goit, chit, 'Q542929', 'P527')
                ensure(chit, goit, 'Q542929', 'P361')
            if (type_ == 'has input'
            or type_ == 'has primary input'):
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
            if type_ == 'has part':
                ensure(goit, chit, None, 'P527')
                ensure(chit, goit, None, 'P361')
    except KeyError:
        pass

