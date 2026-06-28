import sys
data=sys.stdin.read().split()
i=0
n=int(data[i]);i+=1
iv=[]
for _ in range(n):
 s=int(data[i]);e=int(data[i+1]);i+=2
 iv.append((e,s))
iv.sort()
cnt=0
last=-1
for e,s in iv:
 if s>=last:cnt+=1;last=e
print(cnt)
