import os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
Loads all families with IPR and either adds missing IPR parents or removes IPR superclasses
that are no longer supported by IPR. Checks also for duplicate IPR.

Note: --rm is unusable as long as there are mixed enzfam/iprfam superclasses
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-r", "--rm", help="remove stmts not in InterPro",
        action="store_true")
parser.add_argument("-f", "--refs", help="add ref if not existing",
        action="store_true")
parser.add_argument('-i', '--iprel', help='InterPro release item', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
STATED_IN = 'P248'
INTERPRO_RELEASE = args.iprel

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise

input = gzip.open('interpro.xml.gz')                                   
tree = ET.parse(input)
root = tree.getroot() 
its = {}
for child in root:
    if child.tag == 'interpro':
        its[child.attrib.get('id')] = child

#print(set(its.keys()).intersection(delids))

# get IPR items
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)
qits = {}
stmts = {}
supiprs = {}
refs = set()
for d in jol:
    ipr = d.get('ipr')
    qit = d.get('item')
    if ipr not in qits.keys():
        qits[ipr] = qit
    stmt = d.get('stmt')
    supipr = d.get('supipr')
    if supipr is not None and len(supipr) > 0:
        s = supiprs.get(ipr)
        if s is None:
            supiprs[ipr] = set([supipr])
        else:
            s.add(supipr)
        stmts[(qit, supipr)] = stmt
        refs.add((qit, supipr))

if args.rm:
    for nipr in qits.keys():
        supis = supiprs.get(nipr)
        if supis is not None:
            qit = qits.get(nipr)
            entry = its.get(nipr)
            sups = set()
            for ch in entry:
                if ch.tag == 'parent_list':
                    pl = ch.getchildren()
                    if pl is not None and len(pl) > 0:
                        for p in pl:
                            if p.tag == 'rel_ref':
                                ref = p.attrib.get('ipr_ref')
                                sups.add(ref)
            for obsol in supis.difference(sups):
                print(stmts.get((qit, obsol)))
    exit()

for nipr in qits.keys():
    qit = qits.get(nipr)
    entry = its.get(nipr)
    if entry is None:
        print('not found: {}'.format(nipr), file=sys.stderr)
        exit()
    for ch in entry:
        if ch.tag == 'parent_list':
            pl = ch.getchildren()
            if pl is not None and len(pl) > 0:
                for p in pl:
                    if p.tag == 'rel_ref':
                        ref = p.attrib.get('ipr_ref')
                        refit = qits.get(ref)
                        if args.refs:
                            if refit is not None \
                            and (qit, ref) in stmts.keys() \
                            and (qit, ref) not in refs:
                                print((qit, refit))
                                continue
                        if refit is not None \
                        and (qit, ref) not in stmts.keys():
                            j = {"id": qit,
                                 "claims": {
                                    "P279": { "value": refit,
                                        "references": { "P248": INTERPRO_RELEASE }
                                        }
                                    }
                                }
                            print(json.dumps(j), flush=True)
                         
            
            
