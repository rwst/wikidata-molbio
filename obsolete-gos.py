
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

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

goids = {}
items = []
for d in jol:
    goid = d.get('goid')
    gorank = d.get('rank')
    if gorank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    gostmt = d.get('gostmt')
    exm = d.get('exm')
    if not exm.startswith('http://purl.obolibrary.org/obo/GO_'):
        continue
    exstmt = d.get('exstmt')
    it = d.get('item')
    git = goids.get(goid)
    if git is None:
        goids[goid] = (it,gostmt,exm,exstmt)
        items.append(it)
    else:
        print("CAN'T HAPPEN: {}".format(goid))

print('reading GO')
ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')
check = True
obids = []
obitems = []
for goid in goids.keys():
    term = ont.get(goid)
    if term is not None and term.obsolete is False:
        continue
    obids.append(goid)
    obitems.append(goids.get(goid)[0])

als = {}
if args.query1:
    itstr = " ".join(list(map(str, obitems)))
    print('Fetching aliases for {} items'.format(len(obitems)), flush=True)
    ret = os.popen('echo {}| wd data --simplify --props aliases >t.json'.format(itstr))
    print(ret.read())
    if ret.close() is not None:
        print('ERROR')
with open('t.json'.format(script)) as file:
    lines = file.readlines()
    for s in lines:
        jol = json.loads(s)
        it = jol.get('id')
        als[it] = jol.get('aliases')

ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'
for goid in obids:
    it,gostmt,exm,exstmt = goids.get(goid)
    term = ont.get(goid)
    repl_id = None
    if term is not None and len(term.replaced_by) > 0:
        repl_id = term.replaced_by.pop().id
    if QS:
        print('{}|P31|Q93740491|S248|Q93741199|S813|+{}/11'.format(it, newd))
        print('-{}|P686|"{}"'.format(it, goid))
        print('-{}|P2888|"{}"'.format(it, exm))
        aldir = als.get(it)
        if aldir is not None:
            for lang,allist in aldir.items():
                for al in allist:
                    if al.startswith('GO:'):
                        print('-{}|A{}|"{}"'.format(it, lang, al))
        if repl_id is not None:
            print('{}|P1366|{}|S248|Q93741199|S813|+{}/11'.format(it, goids.get(repl_id)[0], newd))
    else:
        aldir = als.get(it)
        ald = {}
        if aldir is not None:
            for lang,allist in aldir.items():
                for al in allist:
                    if al.startswith('GO:'):
                        ald[lang] = { "value":al, "remove":True }
        j = {"id": it,
            "claims": {
                "P31": [ { "value": "Q93740491",
                                "references": { "P248": "Q93741199",
                                    "P813": ndate }}],
                "P686": [{"id":gostmt, "remove":True}],
                "P2888": [{"id":exstmt, "remove":True}]
                } }
        if repl_id is not None:
            j.get('claims')['P1366'] = { "value": goids.get(repl_id)[0],
                                    "references": { "P248": "Q93741199",
                                        "P813": ndate }}
        if len(ald) > 0:
            j['aliases'] = ald
        f = open('t.json', 'w')
        f.write(json.dumps(j))
        f.close()
        print(json.dumps(j), flush=True)
        ret = os.popen('wd ee t.json --summary obsolete-gos')
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
