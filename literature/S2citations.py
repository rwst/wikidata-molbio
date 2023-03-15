import csv, json, argparse, os, sys, time, urllib
import urllib.request as ureq
from sys import *

"""
Reads existing aannotated papers from WD (like refs-sheet.py), collects unique DOIs,
and queries S2 to get all DOIs citing these DOIs, and which are neither members of the input
DOI set, nor of the deaditem set.

Output goes to S2citations.out listing DOI + title, for later filtering and eyeballing.
The list of DOIs needs to be appended to the deaddois list like
sed 's/ \([^ ]*\) .*/\1/g' deng.citations.txt >>deng.deaddois.txt

We do not memorize those papers that we have queried at S2 for citing papers, because the
time we need for full query is less than 1 hour.

To create output files for eyeballing after topic filtering use like
python3 wdlist-from-s2list.py deng.citations.txt
New items will not be many to create so is left for manual.
"""

def Len(obj):
    if obj is None:
        return 0
    else:
        return len(obj)

def S2_wait():
    time.sleep(3.5)


# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-t", "--topic", help="base name", required=True)

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
topic = args.topic

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.refs.rq >{}.refs.json'.format(topic, topic))
    if ret.close() is not None:
        raise
dois = set()
with open('{}.refs.json'.format(topic)) as file:
    s = file.read()
    jol = json.loads(s)

    # read DOIs of marked up papers
    for item in jol:
        doi = item.get('doi')
        dois.add(doi)
print('read {} DOIs of marked up papers'.format(len(dois)), file=sys.stderr)

# read dead DOIs
deaddois = set()
with open('{}.deaddois.txt'.format(topic)) as file:
    l = file.readlines()
    for doi in l:
        deaddois.add(doi.rstrip())
print('read {} dead DOIs'.format(len(deaddois)), file=sys.stderr)


failed_dois = set()
cpapers = set()
ctr = 0
dois.discard(None)
dois.discard('')
for doi in dois:
    ctr = ctr + 1
    next_ = 0
    while next_ is not None:
        url = 'https://api.semanticscholar.org/graph/v1/paper/{}/citations?fields=title,externalIds&offset={}'.format(doi, next_)
        print('{}: contacting S2 for {} ({})'.format(ctr, doi, next_), file=sys.stderr)
        resp = None
        try:
            with ureq.urlopen(url) as f:
                resp = f.read().decode('utf-8')
        except urllib.error.HTTPError:
            pass
        S2_wait()
        if resp is None:
            print("response FAIL", file=sys.stderr)
            failed_dois.add(doi)
            next_ = None
            continue
        data = json.loads(resp)
        offs = data.get('offset')
        next_ = data.get('next')
        d = data.get('data')
        if d is None:
            print("data FAIL: {}".format(data), file=sys.stderr)
            failed_dois.add(doi)
            next_ = None
            continue
        for p in d:
            citingPaper = p.get('citingPaper')
            e = citingPaper.get('externalIds')
            if e is None:
                continue
            cpdoi = e.get('DOI')
            if cpdoi is None:
                continue
            cpdoi = cpdoi.upper()
            cptitle = citingPaper.get('title')
            if cpdoi not in dois and cpdoi not in deaddois:
                cpapers.add((cpdoi, cptitle))

if len(failed_dois) > 0:
    print('FAILED DOIS: "{}'.format(failed_dois), file=sys.stderr)

with open('{}.out'.format(script), 'w') as f:
    for doi,title in cpapers:
        print(' {} {}'.format(doi, title), file=f)





