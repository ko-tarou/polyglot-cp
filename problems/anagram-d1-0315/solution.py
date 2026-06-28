import sys
l=sys.stdin.read().split('\n')
s,t=l[0],l[1]
print('Yes' if sorted(s)==sorted(t) else 'No')
