
import os, json, argparse, sys, datetime, time
import pronto, six

"""
Check all existing ChEBI items have their InChi keys and the current ChEBI
release as source.
"""
script = os.path.basename(sys.argv[0])[:-3]

def write_line_to(name, string):
    f = write_line_to._hdl.get(name)
    if f is None:
        f = open('{}.{}'.format(script, name), 'w')
        write_line_to._hdl[name] = f
    f.write(string + '\n')

write_line_to._hdl = {}

def new_ikey(it, ikey):
    j = {"id": it, "claims": { "P235": [{
        "value": ikey,
        "references": { "P248": CHEBREF }}] } }
    write_line_to('ee1', json.dumps(j))
    
def add_ikey(it, ikey):
    j = {"id": it, "claims": { "P235": [{
        "value": ikey,
        "references": { "P248": CHEBREF }}] } }
    write_line_to('ee2', json.dumps(j))
    
def add_ref(stmt):
    write_line_to('ar', '{} P248 {}'.format(stmt, CHEBREF))

def del_ref(stmt, ref):
    write_line_to('rr', '{} {}'.format(stmt, ref))

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--release-date", help="ChEBI release item",
        required=True,
        action="store")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
print(args)

# Check for --version or -V
dontquery = not args.query
rdate = args.release_date
CHEBREF = 'Q98915402'
if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

blacklist = ['Q11786072', 'Q420138', 'Q412742', 'Q5201339', 'Q904668',
        'Q5198686', 'Q417504', 'Q27289582', 'Q27278834', 'Q5102966',
        'Q27255739', 'Q27292730', 'Q27092937', 'Q41874783', 'Q920900',
        'Q716544', 'Q27263575', 'Q27274220', 'Q27279584', 'Q27257875',
        'Q2102184', 'Q3530618', 'Q4021823', 'Q27110377', 'Q27110219',
        'Q5404490', 'Q27292191', 'Q1452081', 'Q7334473', 'Q5045786',
        'Q416827', 'Q27106184', 'Q5210829', 'Q27122191']

chbits = {}
chebst = {}
stmref = {}
items = set()
dupes = set()
for d in jol:
    item = d.get('item')
    if item in blacklist:
        continue
    chebi = d.get('chebi')
    x = chbits.get(chebi)
    if x is not None and x != item:
        print(x, item)
        raise
    chbits[chebi] = item
    if item in items:
        dupes.add(item)
        continue
    else:
        items.add(item)
    stmt = d.get('stmt')
    ikey = d.get('ikey')
    if stmt is None or len(stmt) == 0:
        continue
    x = chebst.get(chebi)
    if x is None:
        chebst[chebi] = set([(stmt, ikey)])
    else:
        x.add((stmt, ikey))
    ref = d.get('refnode')
    if ref is None or len(ref) == 0:
        continue
    src = d.get('src')
    if src is None or len(src) == 0:
        continue
    sdate = d.get('sdate')
    s = stmref.get(stmt)
    if s is None:
        stmref[stmt] = set([(ref, sdate)])
    else:
        s.add((ref, sdate))

print('Reading ChEBI')
ont = pronto.Ontology('chebi.obo')
print('Writing wikibase-cli input files')
for chebi in chbits.keys():
    term = ont.get('CHEBI:' + chebi)
    it = chbits.get(chebi)
    if it is not None and it in dupes:
        continue
    if term is None:
        print('obsolete: CHEBI:{} {}'.format(chebi, chbits.get(chebi)))
        continue
    xref = term.annotations
    if xref is None:
        continue
    l = [i.literal for i in xref if i.property == 'http://purl.obolibrary.org/obo/chebi/inchikey']
    if len(l) == 0:
        continue    
    ikey = l[0]
    ss = chebst.get(chebi)
    if ss is None:
        new_ikey(chbits.get(chebi), ikey)
        continue
    s = [stmt for stmt,ik in chebst.get(chebi) if ik == ikey]
    if len(s) == 0:
        it = chbits.get(chebi)
        if it is None:
            print(it, chebi)
            raise
        add_ikey(it, ikey)
        continue
    if len(s) > 1:
        print(chebi, s)
        raise
    stmt = s[0]
    refs = stmref.get(stmt)
    if ref is None or len(ref) == 0:
        add_ref(stmt)
        continue
    if all(sdate != rdate + 'T00:00:00Z' for _,sdate in refs): 
        add_ref(stmt)
    for ref,sdate in refs:
        if sdate != rdate + 'T00:00:00Z':
            del_ref(stmt, ref)
