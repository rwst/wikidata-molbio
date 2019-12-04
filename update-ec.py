from sys import *
import csv

trf = dict(l.rstrip().split(sep=' ') for l in stdin.readlines())

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    ec = item.get('ec')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    if trf.get(ec) is None:
        continue
    print('-{}|P591|"{}"'.format(it, ec))
    print('{}|P591|"{}"|S248|Q26737758|S813|+2019-09-09T00:00:00Z/11'.format(it, trf.get(ec)))
