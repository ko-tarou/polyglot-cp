import sys
d=sys.stdin.read().split()
n,x=int(d[0]),int(d[1])
a=list(map(int,d[2:2+n]))
print(sum(1 for v in a if v>x))
