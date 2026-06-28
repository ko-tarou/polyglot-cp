import sys
d=sys.stdin.read().split()
n,x=int(d[0]),int(d[1])
c=list(map(int,d[2:2+n]))
INF=float('inf')
dp=[0]+[INF]*x
for v in range(1,x+1):
 for coin in c:
  if coin<=v and dp[v-coin]+1<dp[v]:dp[v]=dp[v-coin]+1
print(dp[x] if dp[x]!=INF else -1)
