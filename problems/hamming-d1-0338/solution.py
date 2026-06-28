import sys
l=sys.stdin.read().split('\n')
s,t=l[0],l[1]
print(sum(1 for a,b in zip(s,t) if a!=b))
