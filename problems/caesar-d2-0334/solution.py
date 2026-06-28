import sys
l=sys.stdin.read().split('\n')
s=l[0]
k=int(l[1])
print(''.join(chr((ord(c)-97+k)%26+97) for c in s))
