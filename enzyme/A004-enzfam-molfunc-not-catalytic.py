
import csv, os, json, argparse, sys

"""
Two queries are used to get and show all enzfams that have molfuncs but no catalytic molfuncs.
Should only give Q2449730 transport protein.

Alternatively use the A004a query.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
print(args)

# Check for --version or -V
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

funcs = {}
labels = {}
for d in jol:
    qit = d.get('item')
    func = d.get('func')
    labels[qit] = d.get('label')
    labels[func] = d.get('flabel')
    if qit in funcs.keys():
        l = funcs.get(qit)
        l.append(func)
    else:
        funcs[qit] = [func]

if dontquery is False:
    query = """
    SELECT DISTINCT ?item
    WHERE
    {
      ?item wdt:P31 wd:Q14860489.
      ?item wdt:P279/wdt:P279* wd:Q82264
    }
    """
    f = open('{}-1.rq'.format(script), 'w')
    f.write(query)
    f.close()

    print('performing query... ')
    ret = os.popen('wd sparql {}-1.rq >{}-1.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}-1.json'.format(script))

enzfunc = ['Q82264']
for d in file.readlines():
    qit = d.rstrip()
    enzfunc.append(qit)

for it in funcs.keys():
    if not any(f in enzfunc for f in funcs.get(it)):
        print('{} {}'.format(it, labels.get(it)))
