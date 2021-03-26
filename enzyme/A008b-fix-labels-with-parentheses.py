
import csv, os, json, argparse, sys

"""
use with wd ee
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise

with open('{}.json'.format(script)) as file:
    items = ''
    for line in file.readlines():
        items = items + line.rstrip() + ' '
    if dontquery is False:
        ret = os.popen('wd data --props sitelinks {} >{}.json1'.format(items, script))
        if ret.close() is not None:
            raise
    with open('{}.json1'.format(script)) as file1:
        for line in file1.readlines():
            j = json.loads(line)
            it = j.get('id')
            if it is None:
                raise
            labels = {}
            for site, data in j.get('sitelinks').items():
                lang = data.get('site')[:2]
                label = data.get('title')
                labels[lang] = label
            j = { 'id': it, 'labels': labels }
            print(json.dumps(j), flush=True)

