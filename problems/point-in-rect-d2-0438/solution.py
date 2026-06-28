import sys
d=list(map(int,sys.stdin.read().split()))
x1,y1,x2,y2,px,py=d
print('Yes' if x1<=px<=x2 and y1<=py<=y2 else 'No')
