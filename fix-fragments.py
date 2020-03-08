
import csv
from sys import *

reader = csv.DictReader(open('t.tsv', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('item')
    qit = iturl[iturl.rfind('/')+1:]
    piturl = item.get('pro')
    pit = piturl[piturl.rfind('/')+1:]
    em = item.get('em')
    up = em[em.rfind('/')+1:][:6]
    
    print('{}|P31|Q78782478|P642|{}|S248|Q905695\n{}|P2888|"{}"\n-{}|P31|Q8054\n-{}|P352|"{}"\n-{}|P361|{}'.format(qit, pit, qit, em, qit, qit, up, qit, pit))
