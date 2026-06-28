import sys
from itertools import groupby
s=sys.stdin.read().strip()
print(''.join(f'{k}{len(list(g))}' for k,g in groupby(s)))
