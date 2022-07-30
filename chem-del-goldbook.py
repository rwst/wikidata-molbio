
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Cleans and moves all items chunkwise (CHUNKSIZE).
TODO: NO CHECK IS DONE FOR TARGET ITEMS LINKING TO SOURCE ITEMS. MERGE WILL FAIL!
"""
CHUNKSIZE = 7
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", help="don't call wd",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

done = set()
from_to = {}
if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file1 = open('{}.json'.format(script))
s1 = file1.read()
jol = json.loads(s1)

curr_chunk = 0
d0 = []
wd0 = []
for dd in jol:
    b = dd.get('badItem') 
    bad = b.get('value')
    d0.append(bad)
    wd0.append('wd:' + bad)
    g = dd.get('goodItem')
    good = g.get('value')
    from_to[bad] = good
    curr_chunk = curr_chunk + 1
    if curr_chunk < CHUNKSIZE:
        continue

    query = """
    SELECT ?it ?prop ?val  (LANG(?val) AS ?lang)
    WHERE 
    {{
      VALUES ?it {{ {} }}
      ?it ?prop ?val.
    }}
    """.format(' '.join(wd0))
    f = open('{}.rq1'.format(script), 'w')
    f.write(query)
    f.close()
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq1 >{}.json1'.format(script, script))
    if ret.close() is not None:
        raise
    file = open('{}.json1'.format(script))
    s = file.read()
    jol1 = json.loads(s)

    items = {}
    for d in jol1:
        it = d.get('it')
        p = d.get('prop')
        v = d.get('val')
        l = d.get('lang')
        i = items.get(it)
        if i is None:
            items[it] = [(p,v,l)]
        else:
            i.append((p,v,l))
    jj = ''
    for it in items.keys():
        alangs = set()
        dlangs = set()
        llangs = set()
        stmts = {}
        for p,v,l in items.get(it):
            if p[:29] == 'http://www.wikidata.org/prop/':
                s = stmts.get(p[29:])
                if s is None:
                    stmts[p[29:]] = [v]
                else:
                    s.append(v)
            if p == 'http://www.w3.org/2004/02/skos/core#altLabel':
                alangs.add(l)
            if p == 'http://schema.org/description':
                dlangs.add(l)
            if p == 'http://www.w3.org/2000/01/rdf-schema#label':
                llangs.add(l)
        j = { 'id': it }
        if len(alangs) > 0:
            al = {}
            for alang in alangs:
                al[alang] = []
            j['aliases'] = al
        if len(dlangs) > 0:
            dl = {}
            for dlang in dlangs:
                dl[dlang] = None
            j['descriptions'] = dl
        if len(llangs) > 0:
            ll = {}
            for llang in llangs:
                ll[llang] = None
            j['labels'] = ll
        claims = {}
        for p in stmts.keys():
            if p == 'P356' or p == 'direct-normalized/P356':
                continue
            c = []
            for stmt in stmts.get(p):
                c.append({ 'id': stmt, 'remove': True })
            claims[p] = c
        if len(claims) > 0:
            j['claims'] = claims
        jj = jj + json.dumps(j) + '\n'

    f = open('{}.json2'.format(script), 'w')
    f.write(jj)
    f.close()
    if not args.test:
        ret = os.popen('wd ee -bv -s merge-goldbook-entities-see-WPChemistry --no-exit-on-error <{}.json2'.format(script))
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')

    f = open('{}.mtxt'.format(script), 'w')
    for fr in d0:
        f.write('{} {}\n'.format(fr, from_to.get(fr)))
    f.close()

    if not args.test:
        ret = os.popen('wd me -bv -s merge-goldbook-entities-see-WPChemistry --no-exit-on-error <{}.mtxt'.format(script))
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
    else:
        break
    curr_chunk = 0
    d0 = []
    wd0 = []

