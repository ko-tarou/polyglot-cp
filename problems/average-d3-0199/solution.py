import sys
d=sys.stdin.read().split()
n=int(d[0])
a=list(map(int,d[1:1+n]))
print(f'{sum(a)/n:.2f}')
