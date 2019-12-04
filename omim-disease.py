from sys import *
import csv

reader = csv.DictReader(open('disease-omim.tab', 'r'), delimiter='\t')
omims = {}
names = {}
for item in reader:
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    om = item.get('omim')
    omim = omims.get(om)
    name = item.get('itemLabel')
    if names.get(it) is None:
        names[it] = name
    if omim is None:
        omims[om] = [(it,name)]
    else:
        omim.append((it,name))
for item in omims.items():
    print('{}: {}'.format(item[0], item[1]))
