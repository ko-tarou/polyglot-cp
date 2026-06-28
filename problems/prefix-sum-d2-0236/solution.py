import sys
data=sys.stdin.read().split()
i=0
n=int(data[i]);i+=1
q=int(data[i]);i+=1
a=[int(data[i+j]) for j in range(n)];i+=n
p=[0]*(n+1)
for j in range(n):p[j+1]=p[j]+a[j]
out=[]
for _ in range(q):
 l=int(data[i]);r=int(data[i+1]);i+=2
 out.append(str(p[r]-p[l-1]))
print('\n'.join(out))
