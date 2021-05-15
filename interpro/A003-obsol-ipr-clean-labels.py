
import os, json, argparse, sys, datetime, time

"""
Loads all items with P31-->Q81408532 and their aliases/descriptions and
* removes IPR0xyz aliases
* replaces descriptions: en:InterPro family fr:famille InterPro
Optionally the script can give lists of all appearing descriptions in such items
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument('-l', '--list', action='store_true')

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
do_list = args.list
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

alias = {}
desc = {}
deset = set()
for d in jol:
    qit = d.get('item')
    A = d.get('alias')
    if A is not None:
        al = A.get('value')
        alang = A.get('lang')
        dd = alias.get(qit)
        if dd is None:
            alias[qit] = { alang: set([al]) }
        else:
            i = dd.get(alang)
            if i is not None:
                i.add(al)
            else:
                dd[alang] = set([al])
    D = d.get('desc')
    if D is not None:
        de = D.get('value')
        dlang = D.get('lang')
        i = desc.get(qit)
        if i is None:
            desc[qit] = { dlang: de }
        else:
            i[dlang] = de
        deset.add((de, dlang))

if do_list:
    for d in deset:
        print(d)
    exit()

dmap = { "en": { 'InterPro Family': 'protein family',
                'InterPro protein family': 'protein family',
                'InterPro Domain': 'protein domain',
                'InterPro Conserved Site': 'conserved site'},
        "fr": { 'Domaine InterPro': 'domaine protéique',
                'Site Conservé InterPro': 'site conservé',
                'famille InterPro': 'famille de protéines' },
        "de": { 'InterPro Proteinfamilie': 'Proteinfamilie' },
        "nn": { 'InterPro-familie': 'proteinfamilie' }}

for qit in set(desc.keys()).union(set(alias.keys())):
    newD = {}
    newA = {}
    D = desc.get(qit)
    if D is not None:
        for (lang, de) in D.items():
            i = dmap.get(lang)
            if i is not None:
                d = i.get(de)
                if d is not None:
                    newD[lang] = d
    A = alias.get(qit)
    if A is not None:
        for (lang, alset) in A.items():
            if any(a.startswith('IPR') for a in alset):
                al2set = alset.copy()
                for a in alset:
                    if a.startswith('IPR'):
                        al2set.remove(a)
                newA[lang] = list(al2set)
    if len(newA) == 0 and len(newD) == 0:
        continue
    
    j = {"id": qit}
    if len(newD) > 0:
        j['descriptions'] = newD
    if len(newA) > 0:
        j['aliases'] = newA
    print(json.dumps(j), flush=True)
