import sys
d=sys.stdin.read().split()
n=int(d[0])
print(max(map(int,d[1:1+n])))
