from sys import *
import csv

reader = csv.DictReader(open('genes.tab', 'r'), delimiter='\t')
genes = {}
for item in reader:
    name = item.get('itemLabel')
    if genes.get(name):
        print('duplicate gene name: {} {} {}'.format(name,genes.get(name),item.get('item')))
    else:
        genes[name] = item.get('item')
#reader = csv.DictReader(open('omim-diseases.tab', 'r'), delimiter='\t')
#dises = {}
#for item in reader:
#    name = item.get('itemLabel')
#    if genes.get(name):
#        print('duplicate gene name: {}'.format(name))
#    else:
#        genes[name] = item.get('item')



