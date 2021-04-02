import os, json, argparse, sys, datetime, time

"""
Removes statements with object as value. Eyeball before usage!
Use with wd rc.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--obj', help='item that is object in all claims removed', required=True)
parser.add_argument('-p', '--prop', help='property in all claims removed', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
script = os.path.basename(sys.argv[0])[:-3]
query = """
SELECT ?stmt
{{
    ?item p:{} ?stmt .
    ?stmt ps:{} wd:{} .
}}
""".format(args.prop, args.prop, args.obj)
f = open('t.rq', 'w')
f.write(query)
f.close()

ret = os.popen('wd sparql t.rq >t.json')
if ret.close() is not None:
    raise

