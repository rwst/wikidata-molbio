
import csv, os, json, argparse, sys

"""
writes to stdout
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--topic", help="base name", required=True)

# Read arguments from the command line
args = parser.parse_args()
#print(args)

topic = args.topic
script = os.path.basename(sys.argv[0])[:-3]

deaditems = set()
try:
    with open('{}.deaditems.txt'.format(topic)) as file:
        for line in file.readlines():
            line = line.rstrip()
            deaditems.add(line)
except FileNotFoundError:
    print('WARNING: empty database')

query = """SELECT ?doi
WHERE
{{
  VALUES ?item {{ {} }}
  ?item wdt:P356 ?doi.
}}
""".format('wd:' + ' wd:'.join(deaditems))
f = open('{}.rq'.format(script), 'w')
f.write(query)
f.close()
print('performing query for {} items...', file=sys.stderr)
ret = os.popen('wd sparql {}.rq'.format(script, script))
if ret.close() is not None:
    raise
