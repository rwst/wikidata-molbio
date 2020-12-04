
import os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
Loads all items with IPR except domain families and checks InterPro release for obsoletions.
Checks also for duplicatze IPR.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument('-l', '--lag', action='store')

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
lag = args.lag
if lag is None:
    lag =0
script = os.path.basename(sys.argv[0])[:-3]
INTERPRO_RELEASE = 'Q102425430'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

input = gzip.open('interpro.xml.gz')                                   
tree = ET.parse(input)
root = tree.getroot() 

its = {}
delids = set()
for child in root:
    if child.tag == 'interpro':
        its[child.attrib.get('id')] = child

qits = {}
for d in jol:
    if d.get('prop') is not None:
        continue
    ipr = d.get('ipr')
    qit = d.get('item')
    stmt = d.get('stmt')
    if ipr in qits.keys():
        print('duplicate: {}'.format(ipr))
        exit()
    else:
        qits[ipr] = (qit, stmt)

for nipr in set(qits.keys()).difference(set(its.keys())):
    qit, stmt = qits.get(nipr)
    if QS:
        print('-{}|P2926|{}'.format(qit, nipr))
    else:
        j = {"id": qit,
             "claims": {
                 "P2926": { "id": stmt, "remove": True },
                 "P31": { "value": "Q81408532",
                     "references": { "P248": INTERPRO_RELEASE,
                         "P2926": nipr }
                     }
                }
             }
        print(json.dumps(j), flush=True)
       
