
import csv, os, json
from sys import *

"""
For all molfunc statements on obsolete proteins:
remove them
"""
QS = False
dontquery = False
script = os.path.basename(argv[0])[:-3]

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
    func = d.get('func')
    if QS:
        print('-{}|P680|{}'.format(qit, func))
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
