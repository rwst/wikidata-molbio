
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Uses eyeballed A004.txt. Cleans and moves all items chunkwise (CHUNKSIZE).
"""
CHUNKSIZE = 10
# Initiate the parser
parser = argparse.ArgumentParser()

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
script = os.path.basename(sys.argv[0])[:-3]

done = set()
with open('A004.txt', 'r') as af:
    curr_chunk = 0
    d0 = []
    wd0 = []
    d1 = []
    for line in af.readlines():
        d = line.rstrip().split('|')
        d0.append(d[0])
        wd0.append('wd:' + d[0])
        d1.append(d[1])
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
        f = open('{}.rq'.format(script), 'w')
        f.write(query)
        f.close()
        print('performing query...', file=sys.stderr)
        ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
        if ret.close() is not None:
            raise
        file = open('{}.json'.format(script))
        s = file.read()
        jol = json.loads(s)

        items = {}
        for d in jol:
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
                c = []
                for stmt in stmts.get(p):
                    c.append({ 'id': stmt, 'remove': True })
                claims[p] = c
            if len(claims) > 0:
                j['claims'] = claims
            jj = jj + json.dumps(j) + '\n'

        f = open('{}.json1'.format(script), 'w')
        f.write(jj)
        f.close()
        ret = os.popen('wd ee -bv -s del-manually-selected-obsolete-go-entities --no-exit-on-error <{}.json1'.format(script))
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')

        f = open('{}.mtxt'.format(script), 'w')
        for (fr,to) in zip(d0, d1):
            f.write('{} {}\n'.format(fr, to))
        f.close()

        ret = os.popen('wd me -bv -s del-manually-selected-obsolete-go-entities --no-exit-on-error <{}.mtxt'.format(script))
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
        curr_chunk = 0
        d0 = []
        wd0 = []
        d1 = []
