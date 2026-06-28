import sys
x=int(sys.stdin.read())
c=0
for v in (500,100,50,10,5,1):
 c+=x//v
 x%=v
print(c)
