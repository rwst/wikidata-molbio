
import os, json, argparse, sys, datetime, time
import pronto, six


with open('tt') as file:
    for line in file.readlines():
        u = line.rstrip().split(sep='|')
        if len(u) != 5:
            continue
        print(json.dumps([u[0], "P921", { "value": u[2],
                     "references": { "P248": "Q96105165"} }]))
