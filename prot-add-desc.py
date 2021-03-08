
import pronto, six, csv, os, json, argparse, sys, datetime, time

"""
Add missing descriptions
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument('-t', '--taxon', action='store')
parser.add_argument('-k', '--kingdom', action='store')
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

species = ['Q61779006']

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

'''
Adds standard descriptions to proteins without one.
Parameters (mandatory): taxon item ID, kingdom adjective
'''

print('performing query...')
ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
if ret.close() is not None:
    raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True)

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
        print('{} en "{}"'.format(it, dstr))
        #ret = os.popen('wd sd {} en "{}"'.format(it, dstr))
        #print(ret.read())
        #if ret.close() is not None:
        #    print('ERROR')
        #time.sleep(int(lag))
