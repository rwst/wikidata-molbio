
import os, json, argparse, sys, datetime, time, csv, datetime

"""
bzcat latest-all.json.bz2 |grep '"site":"enwiki"' |wikibase-dump-filter --simplify 'keepRichValues=false' |jq '[.id,.sitelinks.enwiki,.claims.P31,.claims.P279]' -c >enwiki.ndjson
"""
def sortdict(d):
    pass

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--articles', action='store', required=True)

# Read arguments from the command line
args = parser.parse_args()
articles = args.articles
script = os.path.basename(sys.argv[0])[:-3]

arts = {}
print('reading dump data...', file=sys.stderr)
file = open(articles)
for line in file.readlines():
    arr = json.loads(line.strip())
    qit = arr[0]
    art = arr[1].replace(' ', '_')
    P31 = arr[2]
    P279 = arr[3]
    if art is None or len(art) == 0:
        raise
    a = arts.get(art)
    if a is not None:
        continue
    arts[art] = (qit, P31, P279)

reader = csv.DictReader(open('catscan.tsv', 'r'), delimiter='\t')
cats = set()
for item in reader:
    cat = item.get('title')
    cats.add(cat)
print(len(cats))

fresh = []
noboth = []
noP31 = []
allP31 = {}
allP279 = {}
onlyP279 = {}
for art in cats:
    a = arts.get(art)
    if a is None:
        fresh.append(art)
        continue
    qit = a[0]
    P31 = a[1]
    P279 = a[2]
    if type(P279) is str:
        P279 = [P279]
    if P31 is None:
        if P279 is None:
            noboth.append(qit)
            continue
        noP31 = (qit, P279)
        for p in P279:
            g = onlyP279.get(p)
            if g is None:
                onlyP279[p] = [qit]
            else:
                g.append(qit)
            g = allP279.get(p)
            if g is None:
                allP279[p] = [qit]
            else:
                g.append(qit)
        continue
    if P279 is None:
        P279 = [None]
    if type(P31) is str:
        P31 = [P31]
    for p in P279:
        g = allP279.get(p)
        if g is None:
            allP279[p] = [qit]
        else:
            g.append(qit)
    continue
    for p in P31:
        g = allP31.get(p)
        if g is None:
            allP31[p] = [qit]
        else:
            g.append(qit)
    continue

for f in fresh:
    print('* https://de.wikipedia.org/wiki/{}'.format(f))

for i in noboth:
    print('* {{{{Q|{}}}}}'.format(i))

