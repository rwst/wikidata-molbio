
import csv, os, json
from sys import *

"""
For all molfunc statements on obsolete proteins:
remove them
"""
QS = true
script = os.path.basename(sys.argv[0])
reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')

for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    iturl = item.get('stmt')
    stmt = iturl[iturl.rfind('/')+1:].replace('-', '$', 1)
    iturl = item.get('func')
    func = iturl[iturl.rfind('/')+1:]
    if QS:
        print('-{}|P680|{}'.format(qit, func))
    else:
        print(stmt)


