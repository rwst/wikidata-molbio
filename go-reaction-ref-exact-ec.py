
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Find obsolete GO items (either "is_obsolete" or not existing) and:
Remove "exact match" and deprecate "Gene Ontology ID" claims.
In case the GO entry has "replaced_by" add "replaced by" (P1366)
Change "instance of"-->"F/C/P obsoleted in GO"
Remove any GO: alias
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-Q", "--query1", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

blacklist = ['GO:0004757', 'GO:0052901', 'GO:0008948', 'GO:0052883', 'GO:0045548', 'GO:0120159',
        'GO:0042602', 'GO:0046353', 'GO:0106029', 'GO:0030266', 'GO:0019152', 'GO:0052902',
        'GO:0052729', 'GO:0050347', 'GO:0004471', 'GO:0052903', 'GO:0052730', 'GO:0015451',
        'GO:0052904', 'GO:0047617', 'GO:0052873', 'GO:0015450', 'GO:0017174', 'GO:0008725']
goids = {}
for d in jol:
    goid = d.get('goid')
    if goid in blacklist:
        continue
    gorank = d.get('rank')
    if gorank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    mtype = d.get('mtype')
    if mtype is not None and mtype.endswith('Q39893449'):
        continue
    gostmt = d.get('gostmt')
    it = d.get('p')
    ec = d.get('ec')
    git = goids.get(goid)
    if git is None:
        goids[goid] = (it,ec,gostmt)
    else:
        print("CAN'T HAPPEN: {}".format(goid))
        exit()

print('reading GO')
ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
for goid in goids.keys():
    term = ont.get(goid)
    if term is None:
        print("CAN'T HAPPEN: {}".format(goid))
        exit()
    for xref in term.definition.xrefs:
        if not xref.id.startswith('EC:'):
            continue
        it,ec,gostmt = goids.get(goid)
        goec = xref.id[3:]
        if QS:
            print('-{}|P591|"{}"'.format(it, ec))
            print('{}|P591|{}|P4390|Q39893449|S248|Q93741199|S813|+{}/11'.format(it, goec, newd))
        else:
            j = {"id": it,
                "claims": {
                    "P591": [ { "id": gostmt,
                                "value": goec,
                                "qualifiers": { "P4390": "Q39893449" },
                                "references": { "P248": "Q93741199",
                                        "P813": ndate }}],
                    } }
            f = open('t.json', 'w')
            f.write(json.dumps(j))
            f.close()
            print(json.dumps(j), flush=True)
            ret = os.popen('wd ee t.json --summary obsolete-gos')
            print(ret.read())
            if ret.close() is not None:
                print('ERROR')
