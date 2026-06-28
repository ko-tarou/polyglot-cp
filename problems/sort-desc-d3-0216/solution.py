import sys
d=sys.stdin.read().split()
n=int(d[0])
a=sorted(map(int,d[1:1+n]),reverse=True)
print(' '.join(map(str,a)))
