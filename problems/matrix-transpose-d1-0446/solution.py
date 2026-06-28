import sys
data=sys.stdin.read().split()
r=int(data[0]);c=int(data[1])
m=[[int(data[2+i*c+j]) for j in range(c)] for i in range(r)]
out=[]
for j in range(c):
 out.append(' '.join(str(m[i][j]) for i in range(r)))
print('\n'.join(out))
