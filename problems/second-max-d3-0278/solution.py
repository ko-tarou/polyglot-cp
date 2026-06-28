import sys
d=sys.stdin.read().split()
n=int(d[0])
u=sorted(set(map(int,d[1:1+n])),reverse=True)
print(u[1] if len(u)>=2 else -1)
