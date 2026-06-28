import sys
d=sys.stdin.read().split()
n=int(d[0])
a=list(map(int,d[1:1+n]))
print(max(a)-min(a))
