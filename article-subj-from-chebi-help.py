
import os, json, argparse, sys, datetime, time
import pronto, six


with open('tt') as file:
    for line in file.readlines():
        u = line.rstrip().split(sep='|')
        if len(u) != 7:
            continue
        j = {"id": u[0],
            "claims": {
                 "P921": { "value": u[2],
                     "references": { "P248": "Q95689128", "P683": u[6][1:-1]} },
                    }
                }
        f = open('t.json', 'w')
        f.write(json.dumps(j))
        f.close()
        print(json.dumps(j), flush=True)
        ret = os.popen('wd ee t.json --summary article-subj-from-chebi')
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
