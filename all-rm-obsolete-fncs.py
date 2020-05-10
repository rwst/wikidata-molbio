
import csv, os, json, argparse, sys

"""
For all molfunc statements on obsolete proteins:
remove them
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
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
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

qhash = {}
for d in jol:
    qit = d.get('p')
    stmt = d.get('stmt')
    if QS:
        print('no longer implemented')
    else:
        s = qhash.get(qit)
        if s is None:
            qhash[qit] = [stmt]
        else:
            s.append(stmt)

if not QS:
    for qit in qhash.keys():
        claims = qhash.get(qit)
        s = "'" + claims[0] + "'"
        if len(claims) > 1:
            for c in claims[1:]:
                s = s + " '" + c + "'"
        print('{} remove {}'.format(qit, s))
        ret = os.popen("wd rc {} >{}.err".format(s, script))
        if ret.close() is not None:
            print('ERROR')
