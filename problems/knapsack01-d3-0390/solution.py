import sys
data=sys.stdin.read().split()
i=0
n=int(data[i]);i+=1
W=int(data[i]);i+=1
dp=[0]*(W+1)
for _ in range(n):
 w=int(data[i]);v=int(data[i+1]);i+=2
 for c in range(W,w-1,-1):
  if dp[c-w]+v>dp[c]:dp[c]=dp[c-w]+v
print(dp[W])
