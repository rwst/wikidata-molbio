
import pronto, six, csv, os, json, argparse, sys, datetime, time

"""
Add missing descriptions, use with wd ee
Adds standard descriptions to proteins without one.
Parameters (mandatory): taxon item ID, kingdom adjective
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument('-t', '--taxon', action='store', required=True)
parser.add_argument('-k', '--kingdom', action='store', required=True)
parser.add_argument('-l', '--lag', action='store')

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
script = os.path.basename(sys.argv[0])[:-3]
QS = args.output_qs
taxon = args.taxon
lag = args.lag
if len(taxon) == 0:
    raise
kingdom = args.kingdom
if len(kingdom) == 0:
    raise

query = """
SELECT DISTINCT ?item ?glabel ?desc
{{
   ?item wdt:P31 wd:Q8054 .
   ?item wdt:P703 wd:{}.
   ?item wdt:P702 ?gitem.
   ?item rdfs:label ?label.
   FILTER ( LANG(?label) = 'en' ).
   ?gitem rdfs:label ?glabel.
   FILTER ( LANG(?glabel) = 'en' ).
   OPTIONAL {{ ?item schema:description ?desc.
               FILTER (LANG(?desc) = 'en') }}.
}}
""".format(taxon)
f = open('{}.rq'.format(script), 'w')
f.write(query)
f.close()


print('performing query...', file=sys.stderr)
ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
if ret.close() is not None:
    raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), file=sys.stderr, flush=True)

ret = os.popen('wd l {} -l en'.format(taxon))
tstr = ret.read()
if ret.close() is not None:
    print('ERROR')
    raise

itld = set()
for d in jol:
    label = d.get('label')
    desc = d.get('desc')
    itld.add((label, desc))

for d in jol:
    it = d.get('item')
    label = d.get('label')
    desc = d.get('desc')
    if desc is not None and len(desc) > 0:
        continue
    if (label,desc) in itld:
        gene = d.get('glabel')
        dstr = '{} protein found in {}, encoded by {}'.format(kingdom, tstr.rstrip(), gene)
    else:
        dstr = '{} protein found in {}'.format(kingdom, tstr.rstrip())
    if QS:
        print('{}|Den|"{}"'.format(it, dstr))
    else:
        j = { 'id': it, 'descriptions': { 'en': dstr } }
        print(json.dumps(j))
        #ret = os.popen('wd sd {} en "{}"'.format(it, dstr))
        #print(ret.read())
        #if ret.close() is not None:
        #    print('ERROR')
        #time.sleep(int(lag))
