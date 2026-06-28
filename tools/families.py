"""Problem families for the Polyglot CP generator.

Each family is a parametric template that produces many concrete problems.
A family declares:
  key          short slug used in the problem id
  topic        topic tag (math / array / string / dp / greedy / geometry / search ...)
  tags         extra tags
  difficulties list of difficulty levels this family supports (1..4)
  per_diff     how many concrete problems to emit per difficulty level
  title(diff)  -> str
  statement(diff) -> markdown body (constraints + I/O format, no samples)
  solution     full standalone python program (the reference solution; reads stdin,
               writes stdout). This file IS the source of truth: the generator runs it
               on every generated input to produce the expected output.
  gen(diff, rng) -> input string (one random test case)
  edges(diff)  -> list of deterministic edge-case input strings (optional)

Statements are Markdown. Code blocks hold only I/O examples (ASCII only, no box-drawing).
"""

import random


# ---------------------------------------------------------------------------
# small helpers shared by gen functions
# ---------------------------------------------------------------------------

def _rint(rng, lo, hi):
    return rng.randint(lo, hi)


def _rlist(rng, n, lo, hi):
    return [rng.randint(lo, hi) for _ in range(n)]


# size ranges per difficulty for array-style problems
N_BY_DIFF = {1: (1, 8), 2: (1, 50), 3: (1, 2000), 4: (1, 100000)}
V_BY_DIFF = {1: (0, 20), 2: (-100, 100), 3: (-10**6, 10**6), 4: (-10**9, 10**9)}


def _n(rng, diff):
    lo, hi = N_BY_DIFF[diff]
    return rng.randint(lo, hi)


def _v(rng, diff):
    lo, hi = V_BY_DIFF[diff]
    return rng.randint(lo, hi)


FAMILIES = []


def family(**kw):
    FAMILIES.append(kw)
    return kw


# ===========================================================================
# MATH / ARITHMETIC
# ===========================================================================

family(
    key="add-two", topic="math", tags=["arithmetic", "io"],
    difficulties=[1, 2, 3], per_diff=4,
    title=lambda d: "A + B",
    statement=lambda d: (
        "2 つの整数 A, B が空白区切りで 1 行に与えられる。A + B を出力せよ。\n\n"
        "## 制約\n\n"
        f"- |A|, |B| <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nA B\n```\n\n## 出力\n\nA + B を 1 行で出力する。\n"
    ),
    solution="import sys\na,b=map(int,sys.stdin.read().split())\nprint(a+b)\n",
    gen=lambda d, rng: f"{_v(rng,d)} {_v(rng,d)}\n",
    edges=lambda d: ["0 0\n", f"{V_BY_DIFF[d][1]} {V_BY_DIFF[d][1]}\n", f"{V_BY_DIFF[d][0]} {V_BY_DIFF[d][1]}\n"],
)

family(
    key="double-n", topic="math", tags=["arithmetic", "io"],
    difficulties=[1, 2], per_diff=4,
    title=lambda d: "N を 2 倍",
    statement=lambda d: (
        "整数 N が 1 行で与えられる。N を 2 倍した値を出力せよ。\n\n"
        f"## 制約\n\n- |N| <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n2N を 1 行で出力する。\n"
    ),
    solution="import sys\nn=int(sys.stdin.read())\nprint(n*2)\n",
    gen=lambda d, rng: f"{_v(rng,d)}\n",
    edges=lambda d: ["0\n", "1\n", "-1\n"],
)

family(
    key="sum-n", topic="math", tags=["array", "sum"],
    difficulties=[1, 2, 3, 4], per_diff=3,
    title=lambda d: "N 個の整数の総和",
    statement=lambda d: (
        "1 行目に整数 N、2 行目に N 個の整数が空白区切りで与えられる。"
        "それらの総和を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 a_2 ... a_N\n```\n\n## 出力\n\n総和を 1 行で出力する。\n"
    ),
    solution="import sys\nd=sys.stdin.read().split()\nn=int(d[0])\nprint(sum(map(int,d[1:1+n])))\n",
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, d)),
    edges=lambda d: ["1\n0\n", "1\n%d\n" % V_BY_DIFF[d][1]],
)

family(
    key="factorial", topic="math", tags=["bignum", "loop"],
    difficulties=[1, 2], per_diff=4,
    title=lambda d: "階乗 N!",
    statement=lambda d: (
        "整数 N が与えられる。N! (N の階乗) を出力せよ。\n\n"
        f"## 制約\n\n- 0 <= N <= {20 if d==1 else 100}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\nN! を 1 行で出力する。\n"
    ),
    solution="import sys,math\nprint(math.factorial(int(sys.stdin.read())))\n",
    gen=lambda d, rng: f"{rng.randint(0, 20 if d==1 else 100)}\n",
    edges=lambda d: ["0\n", "1\n", "%d\n" % (20 if d == 1 else 100)],
)

family(
    key="fib", topic="math", tags=["dp", "sequence"],
    difficulties=[1, 2, 3], per_diff=4,
    title=lambda d: "フィボナッチ数 F(N)",
    statement=lambda d: (
        "F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2) と定める。整数 N に対し F(N) を出力せよ。\n\n"
        f"## 制約\n\n- 0 <= N <= {30 if d==1 else (90 if d==2 else 1000)}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\nF(N) を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nn=int(sys.stdin.read())\na,b=0,1\n"
        "for _ in range(n):\n a,b=b,a+b\nprint(a)\n"
    ),
    gen=lambda d, rng: f"{rng.randint(0, 30 if d==1 else (90 if d==2 else 1000))}\n",
    edges=lambda d: ["0\n", "1\n", "2\n"],
)

family(
    key="gcd", topic="math", tags=["number-theory"],
    difficulties=[1, 2, 3], per_diff=4,
    title=lambda d: "最大公約数 gcd(A, B)",
    statement=lambda d: (
        "2 つの正整数 A, B が与えられる。最大公約数 gcd(A, B) を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= A, B <= {100 if d==1 else (10**6 if d==2 else 10**12)}\n\n"
        "## 入力\n\n```\nA B\n```\n\n## 出力\n\ngcd(A, B) を 1 行で出力する。\n"
    ),
    solution="import sys,math\na,b=map(int,sys.stdin.read().split())\nprint(math.gcd(a,b))\n",
    gen=lambda d, rng: (lambda h: f"{rng.randint(1,h)} {rng.randint(1,h)}\n")(100 if d == 1 else (10**6 if d == 2 else 10**12)),
    edges=lambda d: ["1 1\n", "12 18\n", "100 10\n"],
)

family(
    key="lcm", topic="math", tags=["number-theory"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "最小公倍数 lcm(A, B)",
    statement=lambda d: (
        "2 つの正整数 A, B が与えられる。最小公倍数 lcm(A, B) を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= A, B <= {100 if d==1 else (10**5 if d==2 else 10**9)}\n\n"
        "## 入力\n\n```\nA B\n```\n\n## 出力\n\nlcm(A, B) を 1 行で出力する。\n"
    ),
    solution="import sys,math\na,b=map(int,sys.stdin.read().split())\nprint(a//math.gcd(a,b)*b)\n",
    gen=lambda d, rng: (lambda h: f"{rng.randint(1,h)} {rng.randint(1,h)}\n")(100 if d == 1 else (10**5 if d == 2 else 10**9)),
    edges=lambda d: ["1 1\n", "4 6\n", "7 7\n"],
)

family(
    key="is-prime", topic="math", tags=["number-theory"],
    difficulties=[1, 2, 3], per_diff=4,
    title=lambda d: "素数判定",
    statement=lambda d: (
        "整数 N が与えられる。N が素数なら `Yes`、そうでなければ `No` を出力せよ。\n\n"
        f"## 制約\n\n- 2 <= N <= {100 if d==1 else (10**6 if d==2 else 10**12)}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n`Yes` または `No` を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nn=int(sys.stdin.read())\n"
        "def p(n):\n if n<2:return False\n i=2\n while i*i<=n:\n  if n%i==0:return False\n  i+=1\n return True\n"
        "print('Yes' if p(n) else 'No')\n"
    ),
    gen=lambda d, rng: (lambda h: f"{rng.randint(2,h)}\n")(100 if d == 1 else (10**6 if d == 2 else 10**12)),
    edges=lambda d: ["2\n", "4\n", "97\n"],
)

family(
    key="count-primes", topic="math", tags=["sieve", "number-theory"],
    difficulties=[2, 3], per_diff=4,
    title=lambda d: "N 以下の素数の個数",
    statement=lambda d: (
        "整数 N が与えられる。N 以下の素数の個数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {1000 if d==2 else 10**6}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n素数の個数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nn=int(sys.stdin.read())\n"
        "if n<2:\n print(0)\nelse:\n s=[True]*(n+1)\n s[0]=s[1]=False\n i=2\n"
        " while i*i<=n:\n  if s[i]:\n   for j in range(i*i,n+1,i):s[j]=False\n  i+=1\n print(sum(s))\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1, 1000 if d==2 else 10**6)}\n",
    edges=lambda d: ["1\n", "2\n", "10\n"],
)

family(
    key="power-mod", topic="math", tags=["number-theory", "mod"],
    difficulties=[2, 3], per_diff=4,
    title=lambda d: "べき乗の剰余 A^B mod M",
    statement=lambda d: (
        "整数 A, B, M が与えられる。A^B を M で割った余りを出力せよ。\n\n"
        f"## 制約\n\n- 0 <= A <= 10^9\n- 0 <= B <= {1000 if d==2 else 10**18}\n- 1 <= M <= 10^9\n\n"
        "## 入力\n\n```\nA B M\n```\n\n## 出力\n\nA^B mod M を 1 行で出力する。\n"
    ),
    solution="import sys\na,b,m=map(int,sys.stdin.read().split())\nprint(pow(a,b,m))\n",
    gen=lambda d, rng: f"{rng.randint(0,10**9)} {rng.randint(0, 1000 if d==2 else 10**18)} {rng.randint(1,10**9)}\n",
    edges=lambda d: ["2 10 1000\n", "0 0 7\n", "5 0 13\n"],
)

family(
    key="sum-digits", topic="math", tags=["string", "digit"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "各桁の和",
    statement=lambda d: (
        "非負整数 N が与えられる。N の各桁の数字の和を出力せよ。\n\n"
        f"## 制約\n\n- 0 <= N < 10^{ {1:5,2:18,3:1000}[d] }\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n各桁の和を 1 行で出力する。\n"
    ),
    solution="import sys\nprint(sum(int(c) for c in sys.stdin.read().strip()))\n",
    gen=lambda d, rng: f"{rng.randint(0, 10**{1:5,2:18,3:60}[d]-1)}\n",
    edges=lambda d: ["0\n", "9\n", "1000000\n"],
)

family(
    key="reverse-int", topic="math", tags=["digit"],
    difficulties=[1, 2], per_diff=4,
    title=lambda d: "整数の桁反転",
    statement=lambda d: (
        "非負整数 N が与えられる。N の桁を反転した整数を出力せよ (先頭の 0 は除く)。\n\n"
        f"## 制約\n\n- 0 <= N < 10^{ {1:5,2:18}[d] }\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n桁を反転した整数を 1 行で出力する。\n"
    ),
    solution="import sys\nprint(int(sys.stdin.read().strip()[::-1]))\n",
    gen=lambda d, rng: f"{rng.randint(0, 10**{1:5,2:18}[d]-1)}\n",
    edges=lambda d: ["0\n", "120\n", "1000\n"],
)

family(
    key="collatz", topic="math", tags=["simulation"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "コラッツ数列の長さ",
    statement=lambda d: (
        "正整数 N に対し、偶数なら 2 で割り、奇数なら 3 倍して 1 を足す操作を繰り返す。"
        "N が 1 になるまでの操作回数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {100 if d==1 else (10**5 if d==2 else 10**7)}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n操作回数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nn=int(sys.stdin.read())\nc=0\n"
        "while n!=1:\n n=n//2 if n%2==0 else 3*n+1\n c+=1\nprint(c)\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1, 100 if d==1 else (10**5 if d==2 else 10**7))}\n",
    edges=lambda d: ["1\n", "2\n", "27\n"],
)

family(
    key="count-divisors", topic="math", tags=["number-theory"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "約数の個数",
    statement=lambda d: (
        "正整数 N の約数の個数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {100 if d==1 else (10**6 if d==2 else 10**12)}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n約数の個数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nn=int(sys.stdin.read())\nc=0\ni=1\n"
        "while i*i<=n:\n if n%i==0:\n  c+=1 if i*i==n else 2\n i+=1\nprint(c)\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1, 100 if d==1 else (10**6 if d==2 else 10**12))}\n",
    edges=lambda d: ["1\n", "12\n", "36\n"],
)

family(
    key="divisor-sum", topic="math", tags=["number-theory"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "約数の総和",
    statement=lambda d: (
        "正整数 N の正の約数すべての和を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {100 if d==1 else (10**6 if d==2 else 10**12)}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n約数の総和を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nn=int(sys.stdin.read())\ns=0\ni=1\n"
        "while i*i<=n:\n if n%i==0:\n  s+=i\n  if i*i!=n:s+=n//i\n i+=1\nprint(s)\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1, 100 if d==1 else (10**6 if d==2 else 10**12))}\n",
    edges=lambda d: ["1\n", "6\n", "28\n"],
)

family(
    key="triangular", topic="math", tags=["formula"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "1 から N までの和",
    statement=lambda d: (
        "整数 N が与えられる。1 + 2 + ... + N を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {1000 if d==1 else 10**9}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n総和を 1 行で出力する。\n"
    ),
    solution="import sys\nn=int(sys.stdin.read())\nprint(n*(n+1)//2)\n",
    gen=lambda d, rng: f"{rng.randint(1, 1000 if d==1 else 10**9)}\n",
    edges=lambda d: ["1\n", "100\n", "1000\n"],
)

family(
    key="arithmetic-sum", topic="math", tags=["formula", "sequence"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "等差数列の和",
    statement=lambda d: (
        "初項 a、公差 d、項数 n の等差数列の和を出力せよ。\n\n"
        "## 制約\n\n- |a|, |d| <= 10^6\n- 1 <= n <= 10^6\n\n"
        "## 入力\n\n```\na d n\n```\n\n## 出力\n\n数列の和を 1 行で出力する。\n"
    ),
    solution="import sys\na,d,n=map(int,sys.stdin.read().split())\nprint(n*(2*a+(n-1)*d)//2)\n",
    gen=lambda d, rng: f"{rng.randint(-10**6,10**6)} {rng.randint(-10**6,10**6)} {rng.randint(1,10**6)}\n",
    edges=lambda d: ["1 1 1\n", "0 0 5\n", "1 2 100\n"],
)

# ===========================================================================
# ARRAY / AGGREGATION
# ===========================================================================

family(
    key="max-array", topic="array", tags=["aggregate"],
    difficulties=[1, 2, 3, 4], per_diff=3,
    title=lambda d: "配列の最大値",
    statement=lambda d: (
        "1 行目に N、2 行目に N 個の整数が与えられる。最大値を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n最大値を 1 行で出力する。\n"
    ),
    solution="import sys\nd=sys.stdin.read().split()\nn=int(d[0])\nprint(max(map(int,d[1:1+n])))\n",
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, d)),
    edges=lambda d: ["1\n0\n", "3\n-1 -2 -3\n"],
)

family(
    key="min-array", topic="array", tags=["aggregate"],
    difficulties=[1, 2, 3, 4], per_diff=3,
    title=lambda d: "配列の最小値",
    statement=lambda d: (
        "1 行目に N、2 行目に N 個の整数が与えられる。最小値を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n最小値を 1 行で出力する。\n"
    ),
    solution="import sys\nd=sys.stdin.read().split()\nn=int(d[0])\nprint(min(map(int,d[1:1+n])))\n",
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, d)),
    edges=lambda d: ["1\n0\n", "3\n5 1 9\n"],
)

family(
    key="count-even-odd", topic="array", tags=["count"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "偶数と奇数の個数",
    statement=lambda d: (
        "N 個の整数のうち、偶数の個数と奇数の個数を空白区切りで出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n偶数の個数 奇数の個数 を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=list(map(int,d[1:1+n]))\n"
        "e=sum(1 for x in a if x%2==0)\nprint(e,n-e)\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, d)),
    edges=lambda d: ["1\n2\n", "1\n3\n"],
)

family(
    key="average", topic="array", tags=["aggregate", "float"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "平均値 (小数第 2 位)",
    statement=lambda d: (
        "N 個の整数の平均値を小数第 2 位まで出力せよ (四捨五入)。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n平均値を小数第 2 位まで出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=list(map(int,d[1:1+n]))\n"
        "print(f'{sum(a)/n:.2f}')\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,0,V_BY_DIFF[d][1])))}\n")(_n(rng, d)),
    edges=lambda d: ["1\n5\n", "2\n1 2\n"],
)

family(
    key="sort-asc", topic="array", tags=["sort"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "昇順ソート",
    statement=lambda d: (
        "N 個の整数を昇順に並べ替えて空白区切りで 1 行に出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n昇順に並べた数列を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=sorted(map(int,d[1:1+n]))\n"
        "print(' '.join(map(str,a)))\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, min(d, 3))),
    edges=lambda d: ["1\n0\n", "3\n3 1 2\n"],
)

family(
    key="sort-desc", topic="array", tags=["sort"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "降順ソート",
    statement=lambda d: (
        "N 個の整数を降順に並べ替えて空白区切りで 1 行に出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n降順に並べた数列を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=sorted(map(int,d[1:1+n]),reverse=True)\n"
        "print(' '.join(map(str,a)))\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, min(d, 3))),
    edges=lambda d: ["1\n0\n", "3\n1 3 2\n"],
)

family(
    key="kth-smallest", topic="array", tags=["sort", "select"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "K 番目に小さい値",
    statement=lambda d: (
        "N 個の整数と整数 K が与えられる。昇順に並べたとき K 番目に小さい値を出力せよ (1-indexed)。\n\n"
        f"## 制約\n\n- 1 <= K <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN K\na_1 ... a_N\n```\n\n## 出力\n\nK 番目に小さい値を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn,k=int(d[0]),int(d[1])\n"
        "a=sorted(map(int,d[2:2+n]))\nprint(a[k-1])\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n} {rng.randint(1,n)}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, min(d, 3)) or 1),
    edges=lambda d: ["1 1\n5\n", "3 2\n3 1 2\n"],
)

family(
    key="median", topic="array", tags=["sort", "stats"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "中央値",
    statement=lambda d: (
        "奇数個 N の整数が与えられる。中央値 (昇順に並べた真ん中の値) を出力せよ。\n\n"
        f"## 制約\n\n- N は奇数, 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n中央値を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=sorted(map(int,d[1:1+n]))\n"
        "print(a[n//2])\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")((_n(rng, min(d, 3)) | 1)),
    edges=lambda d: ["1\n7\n", "3\n3 1 2\n"],
)

family(
    key="mode", topic="array", tags=["count", "stats"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "最頻値",
    statement=lambda d: (
        "N 個の整数のうち最も多く出現する値を出力せよ。複数あれば最小の値を出力する。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 0 <= 各要素 <= {max(20,V_BY_DIFF[d][1]//1000)}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n最頻値を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nfrom collections import Counter\nd=sys.stdin.read().split()\nn=int(d[0])\n"
        "a=list(map(int,d[1:1+n]))\nc=Counter(a)\nm=max(c.values())\n"
        "print(min(k for k,v in c.items() if v==m))\n"
    ),
    gen=lambda d, rng: (lambda n, hi: f"{n}\n{' '.join(str(rng.randint(0,hi)) for _ in range(n))}\n")(_n(rng, min(d, 3)), max(20, V_BY_DIFF[d][1] // 1000)),
    edges=lambda d: ["1\n0\n", "5\n1 1 2 2 3\n"],
)

family(
    key="prefix-sum", topic="array", tags=["prefix-sum", "query"],
    difficulties=[2, 3], per_diff=4,
    title=lambda d: "区間和クエリ",
    statement=lambda d: (
        "長さ N の配列と Q 個のクエリが与えられる。各クエリ l r について"
        " a_l + a_{l+1} + ... + a_r を出力せよ (1-indexed)。\n\n"
        f"## 制約\n\n- 1 <= N, Q <= {200 if d==2 else 10**5}\n- 各要素の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nN Q\na_1 ... a_N\nl_1 r_1\n...\nl_Q r_Q\n```\n\n"
        "## 出力\n\n各クエリの答えを 1 行ずつ出力する。\n"
    ),
    solution=(
        "import sys\ndata=sys.stdin.read().split()\ni=0\nn=int(data[i]);i+=1\nq=int(data[i]);i+=1\n"
        "a=[int(data[i+j]) for j in range(n)];i+=n\n"
        "p=[0]*(n+1)\nfor j in range(n):p[j+1]=p[j]+a[j]\n"
        "out=[]\nfor _ in range(q):\n l=int(data[i]);r=int(data[i+1]);i+=2\n out.append(str(p[r]-p[l-1]))\n"
        "print('\\n'.join(out))\n"
    ),
    gen=lambda d, rng: _gen_prefix(d, rng),
    edges=lambda d: ["3 1\n1 2 3\n1 3\n", "1 1\n5\n1 1\n"],
)


def _gen_prefix(d, rng):
    n = rng.randint(1, 200 if d == 2 else 3000)
    q = rng.randint(1, 200 if d == 2 else 3000)
    a = _rlist(rng, n, -10**6, 10**6)
    lines = [f"{n} {q}", " ".join(map(str, a))]
    for _ in range(q):
        l = rng.randint(1, n)
        r = rng.randint(l, n)
        lines.append(f"{l} {r}")
    return "\n".join(lines) + "\n"


family(
    key="max-subarray", topic="array", tags=["dp", "kadane"],
    difficulties=[2, 3], per_diff=4,
    title=lambda d: "最大連続部分和",
    statement=lambda d: (
        "N 個の整数からなる数列の、連続する部分列の和の最大値を出力せよ"
        " (空でない部分列を選ぶ)。\n\n"
        f"## 制約\n\n- 1 <= N <= {200 if d==2 else 10**5}\n- 各要素の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n最大の部分和を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=list(map(int,d[1:1+n]))\n"
        "best=cur=a[0]\nfor x in a[1:]:\n cur=max(x,cur+x)\n best=max(best,cur)\nprint(best)\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,-10**6,10**6)))}\n")(rng.randint(1, 200 if d == 2 else 3000)),
    edges=lambda d: ["1\n-5\n", "5\n-2 1 -3 4 -1\n"],
)

family(
    key="gcd-array", topic="array", tags=["number-theory", "aggregate"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "配列全体の最大公約数",
    statement=lambda d: (
        "N 個の正整数すべての最大公約数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {200 if d==2 else 10**5}\n- 1 <= 各要素 <= 10^9\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n最大公約数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys,math\nfrom functools import reduce\nd=sys.stdin.read().split()\nn=int(d[0])\n"
        "a=list(map(int,d[1:1+n]))\nprint(reduce(math.gcd,a))\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(str(rng.randint(1,10**9)) for _ in range(n))}\n")(rng.randint(1, 200 if d == 2 else 3000)),
    edges=lambda d: ["1\n7\n", "3\n12 18 24\n"],
)

family(
    key="two-sum-exists", topic="array", tags=["search", "set"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "2 数の和が K になるか",
    statement=lambda d: (
        "N 個の整数と目標値 K が与えられる。異なる 2 要素の和が K になる組が"
        "存在すれば `Yes`、なければ `No` を出力せよ。\n\n"
        f"## 制約\n\n- 2 <= N <= {200 if d==2 else 10**5}\n- 各要素, K の絶対値 <= 10^9\n\n"
        "## 入力\n\n```\nN K\na_1 ... a_N\n```\n\n## 出力\n\n`Yes` または `No` を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn,k=int(d[0]),int(d[1])\na=list(map(int,d[2:2+n]))\n"
        "seen=set()\nok=False\nfor x in a:\n if k-x in seen:ok=True;break\n seen.add(x)\n"
        "print('Yes' if ok else 'No')\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n} {rng.randint(-50,50)}\n{' '.join(str(rng.randint(-30,30)) for _ in range(n))}\n")(rng.randint(2, 50 if d == 2 else 1000)),
    edges=lambda d: ["2 3\n1 2\n", "2 100\n1 2\n"],
)

family(
    key="count-greater", topic="array", tags=["count", "threshold"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "閾値より大きい要素数",
    statement=lambda d: (
        "N 個の整数と閾値 X が与えられる。X より大きい要素の個数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素, X の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN X\na_1 ... a_N\n```\n\n## 出力\n\n個数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn,x=int(d[0]),int(d[1])\na=list(map(int,d[2:2+n]))\n"
        "print(sum(1 for v in a if v>x))\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n} {_v(rng,d)}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, min(d, 3))),
    edges=lambda d: ["1 0\n5\n", "3 5\n1 2 3\n"],
)

family(
    key="second-max", topic="array", tags=["aggregate"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "2 番目に大きい値",
    statement=lambda d: (
        "N 個の整数のうち、2 番目に大きい (異なる) 値を出力せよ。"
        " 異なる値が 2 種類未満なら `-1` を出力する。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n2 番目に大きい値、または `-1` を出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\nu=sorted(set(map(int,d[1:1+n])),reverse=True)\n"
        "print(u[1] if len(u)>=2 else -1)\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, min(d, 3))),
    edges=lambda d: ["1\n5\n", "3\n2 2 2\n"],
)

# ===========================================================================
# STRING
# ===========================================================================

def _rstr(rng, n, alphabet="abcdefghijklmnopqrstuvwxyz"):
    return "".join(rng.choice(alphabet) for _ in range(n))


S_LEN = {1: (1, 10), 2: (1, 100), 3: (1, 5000)}


def _slen(rng, d):
    lo, hi = S_LEN[d]
    return rng.randint(lo, hi)


family(
    key="str-len", topic="string", tags=["basic"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "文字列の長さ",
    statement=lambda d: (
        "英小文字からなる文字列 S が与えられる。その長さを出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\n```\n\n## 出力\n\n|S| を 1 行で出力する。\n"
    ),
    solution="import sys\nprint(len(sys.stdin.read().strip()))\n",
    gen=lambda d, rng: _rstr(rng, _slen(rng, d)) + "\n",
    edges=lambda d: ["a\n", "abc\n"],
)

family(
    key="str-reverse", topic="string", tags=["basic"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "文字列の反転",
    statement=lambda d: (
        "英小文字からなる文字列 S が与えられる。S を逆順にして出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\n```\n\n## 出力\n\n反転した文字列を 1 行で出力する。\n"
    ),
    solution="import sys\nprint(sys.stdin.read().strip()[::-1])\n",
    gen=lambda d, rng: _rstr(rng, _slen(rng, d)) + "\n",
    edges=lambda d: ["a\n", "abcde\n"],
)

family(
    key="str-upper", topic="string", tags=["basic"],
    difficulties=[1], per_diff=4,
    title=lambda d: "大文字に変換",
    statement=lambda d: (
        "英小文字からなる文字列 S を、すべて大文字に変換して出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[1][1]}\n\n"
        "## 入力\n\n```\nS\n```\n\n## 出力\n\n大文字に変換した文字列を出力する。\n"
    ),
    solution="import sys\nprint(sys.stdin.read().strip().upper())\n",
    gen=lambda d, rng: _rstr(rng, _slen(rng, 1)) + "\n",
    edges=lambda d: ["a\n", "abc\n"],
)

family(
    key="char-count", topic="string", tags=["count"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "指定文字の出現回数",
    statement=lambda d: (
        "文字列 S と 1 文字 c が与えられる。S 中の c の出現回数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\nc\n```\n\n## 出力\n\n出現回数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nlines=sys.stdin.read().split('\\n')\ns=lines[0]\nc=lines[1][0]\nprint(s.count(c))\n"
    ),
    gen=lambda d, rng: _rstr(rng, _slen(rng, d)) + "\n" + rng.choice("abc") + "\n",
    edges=lambda d: ["banana\na\n", "abc\nz\n"],
)

family(
    key="vowel-count", topic="string", tags=["count"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "母音の数",
    statement=lambda d: (
        "英小文字からなる文字列 S 中の母音 (a, e, i, o, u) の総数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\n```\n\n## 出力\n\n母音の数を 1 行で出力する。\n"
    ),
    solution="import sys\ns=sys.stdin.read().strip()\nprint(sum(1 for c in s if c in 'aeiou'))\n",
    gen=lambda d, rng: _rstr(rng, _slen(rng, d)) + "\n",
    edges=lambda d: ["aeiou\n", "xyz\n"],
)

family(
    key="palindrome", topic="string", tags=["check"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "回文判定",
    statement=lambda d: (
        "英小文字からなる文字列 S が回文 (前から読んでも後ろから読んでも同じ) なら"
        " `Yes`、そうでなければ `No` を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\n```\n\n## 出力\n\n`Yes` または `No` を 1 行で出力する。\n"
    ),
    solution="import sys\ns=sys.stdin.read().strip()\nprint('Yes' if s==s[::-1] else 'No')\n",
    gen=lambda d, rng: _gen_palindrome(d, rng),
    edges=lambda d: ["level\n", "abc\n", "a\n"],
)


def _gen_palindrome(d, rng):
    if rng.random() < 0.4:  # bias toward actual palindromes
        half = _rstr(rng, _slen(rng, d) // 2 + 1, "abc")
        s = half + (half[-2::-1] if rng.random() < 0.5 else half[::-1])
        return s + "\n"
    return _rstr(rng, _slen(rng, d), "abc") + "\n"


family(
    key="anagram", topic="string", tags=["check", "count"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "アナグラム判定",
    statement=lambda d: (
        "2 つの文字列 S, T が与えられる。並べ替えで一致する (アナグラムである) なら"
        " `Yes`、そうでなければ `No` を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S|, |T| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\nT\n```\n\n## 出力\n\n`Yes` または `No` を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nl=sys.stdin.read().split('\\n')\ns,t=l[0],l[1]\n"
        "print('Yes' if sorted(s)==sorted(t) else 'No')\n"
    ),
    gen=lambda d, rng: _gen_anagram(d, rng),
    edges=lambda d: ["listen\nsilent\n", "abc\nabd\n"],
)


def _gen_anagram(d, rng):
    s = _rstr(rng, _slen(rng, d), "abcde")
    if rng.random() < 0.5:
        t = list(s)
        rng.shuffle(t)
        return s + "\n" + "".join(t) + "\n"
    return s + "\n" + _rstr(rng, _slen(rng, d), "abcde") + "\n"


family(
    key="count-words", topic="string", tags=["parse"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "単語数を数える",
    statement=lambda d: (
        "空白区切りの単語からなる 1 行 S が与えられる。単語の個数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= 単語数 <= {10 if d==1 else 1000}\n\n"
        "## 入力\n\n```\nS\n```\n\n## 出力\n\n単語数を 1 行で出力する。\n"
    ),
    solution="import sys\nprint(len(sys.stdin.read().split()))\n",
    gen=lambda d, rng: " ".join(_rstr(rng, rng.randint(1, 5)) for _ in range(rng.randint(1, 10 if d == 1 else 100))) + "\n",
    edges=lambda d: ["hello world\n", "one\n"],
)

family(
    key="run-length", topic="string", tags=["encode"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "ランレングス圧縮",
    statement=lambda d: (
        "英小文字からなる文字列 S を、連続する同じ文字を `文字+個数` にまとめて"
        "出力せよ。例: `aaabbc` -> `a3b2c1`。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\n```\n\n## 出力\n\n圧縮した文字列を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nfrom itertools import groupby\ns=sys.stdin.read().strip()\n"
        "print(''.join(f'{k}{len(list(g))}' for k,g in groupby(s)))\n"
    ),
    gen=lambda d, rng: "".join(rng.choice("abc") * rng.randint(1, 4) for _ in range(rng.randint(1, _slen(rng, d) // 2 + 1))) + "\n",
    edges=lambda d: ["aaabbc\n", "abc\n"],
)

family(
    key="caesar", topic="string", tags=["cipher"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "シーザー暗号",
    statement=lambda d: (
        "英小文字からなる文字列 S と整数 K が与えられる。各文字を"
        "アルファベット上で K だけ後ろにずらして (z の次は a に循環) 出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| <= {S_LEN[d][1]}\n- 0 <= K <= 25\n\n"
        "## 入力\n\n```\nS\nK\n```\n\n## 出力\n\n変換後の文字列を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nl=sys.stdin.read().split('\\n')\ns=l[0]\nk=int(l[1])\n"
        "print(''.join(chr((ord(c)-97+k)%26+97) for c in s))\n"
    ),
    gen=lambda d, rng: _rstr(rng, _slen(rng, d)) + "\n" + str(rng.randint(0, 25)) + "\n",
    edges=lambda d: ["abc\n1\n", "xyz\n3\n"],
)

family(
    key="hamming", topic="string", tags=["compare"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "ハミング距離",
    statement=lambda d: (
        "同じ長さの 2 つの文字列 S, T が与えられる。対応する位置で異なる"
        "文字の個数 (ハミング距離) を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= |S| = |T| <= {S_LEN[d][1]}\n\n"
        "## 入力\n\n```\nS\nT\n```\n\n## 出力\n\nハミング距離を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nl=sys.stdin.read().split('\\n')\ns,t=l[0],l[1]\n"
        "print(sum(1 for a,b in zip(s,t) if a!=b))\n"
    ),
    gen=lambda d, rng: _gen_hamming(d, rng),
    edges=lambda d: ["abc\nabd\n", "aaa\naaa\n"],
)


def _gen_hamming(d, rng):
    n = _slen(rng, d)
    s = _rstr(rng, n, "abc")
    t = "".join(c if rng.random() < 0.6 else rng.choice("abc") for c in s)
    return s + "\n" + t + "\n"


# ===========================================================================
# SEARCH
# ===========================================================================

family(
    key="binary-search", topic="search", tags=["binary-search"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "二分探索 (存在判定)",
    statement=lambda d: (
        "昇順にソート済みの N 個の整数と目標値 X が与えられる。X が含まれていれば"
        " `Yes`、なければ `No` を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {200 if d==2 else 10**5}\n- 各要素, X の絶対値 <= 10^9\n\n"
        "## 入力\n\n```\nN X\na_1 ... a_N (昇順)\n```\n\n## 出力\n\n`Yes` または `No` を 1 行で出力する。\n"
    ),
    solution=(
        "import sys,bisect\nd=sys.stdin.read().split()\nn,x=int(d[0]),int(d[1])\n"
        "a=list(map(int,d[2:2+n]))\ni=bisect.bisect_left(a,x)\n"
        "print('Yes' if i<n and a[i]==x else 'No')\n"
    ),
    gen=lambda d, rng: _gen_sorted_search(d, rng),
    edges=lambda d: ["3 2\n1 2 3\n", "3 5\n1 2 3\n"],
)


def _gen_sorted_search(d, rng):
    n = rng.randint(1, 200 if d == 2 else 2000)
    a = sorted(_rlist(rng, n, -10**6, 10**6))
    x = rng.choice(a) if rng.random() < 0.5 else rng.randint(-10**6, 10**6)
    return f"{n} {x}\n{' '.join(map(str,a))}\n"


family(
    key="linear-index", topic="search", tags=["linear"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "線形探索 (最初の位置)",
    statement=lambda d: (
        "N 個の整数と目標値 X が与えられる。X が最初に現れる位置 (1-indexed) を"
        "出力せよ。存在しなければ `-1` を出力する。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素, X の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN X\na_1 ... a_N\n```\n\n## 出力\n\n位置、または `-1` を出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn,x=int(d[0]),int(d[1])\na=list(map(int,d[2:2+n]))\n"
        "ans=-1\nfor i,v in enumerate(a):\n if v==x:ans=i+1;break\nprint(ans)\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n} {_v(rng,d)}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, min(d, 3))),
    edges=lambda d: ["3 2\n1 2 3\n", "3 9\n1 2 3\n"],
)

family(
    key="count-pairs-target", topic="search", tags=["count", "two-pointer"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "和が K になる組の数",
    statement=lambda d: (
        "N 個の整数と目標値 K が与えられる。和が K になる相異なる添字の組 (i<j) の"
        "個数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {200 if d==2 else 3000}\n- 各要素, K の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nN K\na_1 ... a_N\n```\n\n## 出力\n\n組の個数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nfrom collections import Counter\nd=sys.stdin.read().split()\nn,k=int(d[0]),int(d[1])\n"
        "a=list(map(int,d[2:2+n]))\nc=Counter()\nans=0\n"
        "for x in a:\n ans+=c[k-x]\n c[x]+=1\nprint(ans)\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n} {rng.randint(-20,20)}\n{' '.join(str(rng.randint(-10,10)) for _ in range(n))}\n")(rng.randint(1, 100 if d == 2 else 500)),
    edges=lambda d: ["4 4\n1 3 2 2\n", "3 100\n1 2 3\n"],
)

# ===========================================================================
# DP
# ===========================================================================

family(
    key="climb-stairs", topic="dp", tags=["dp", "counting"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "階段の登り方",
    statement=lambda d: (
        "N 段の階段を、一度に 1 段または 2 段ずつ登る。登り方の総数を"
        " 1000000007 で割った余りで出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {30 if d==1 else 10**6}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n登り方の数 (mod 1000000007) を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nM=10**9+7\nn=int(sys.stdin.read())\na,b=1,1\n"
        "for _ in range(n):\n a,b=b,(a+b)%M\nprint(a)\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1, 30 if d==1 else 10**6)}\n",
    edges=lambda d: ["1\n", "2\n", "5\n"],
)

family(
    key="lcs", topic="dp", tags=["dp", "string"],
    difficulties=[3], per_diff=6,
    title=lambda d: "最長共通部分列",
    statement=lambda d: (
        "2 つの文字列 S, T が与えられる。最長共通部分列 (LCS) の長さを出力せよ。\n\n"
        "## 制約\n\n- 1 <= |S|, |T| <= 1000\n\n"
        "## 入力\n\n```\nS\nT\n```\n\n## 出力\n\nLCS の長さを 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nl=sys.stdin.read().split('\\n')\ns,t=l[0],l[1]\nm,n=len(s),len(t)\n"
        "dp=[0]*(n+1)\nfor i in range(m):\n nd=[0]*(n+1)\n for j in range(n):\n"
        "  nd[j+1]=dp[j]+1 if s[i]==t[j] else max(dp[j+1],nd[j])\n dp=nd\nprint(dp[n])\n"
    ),
    gen=lambda d, rng: _rstr(rng, rng.randint(1, 60), "abc") + "\n" + _rstr(rng, rng.randint(1, 60), "abc") + "\n",
    edges=lambda d: ["abcde\nace\n", "abc\nxyz\n"],
)

family(
    key="edit-distance", topic="dp", tags=["dp", "string"],
    difficulties=[3], per_diff=6,
    title=lambda d: "編集距離",
    statement=lambda d: (
        "2 つの文字列 S, T が与えられる。1 文字の挿入・削除・置換で S を T に"
        "変える最小操作回数 (編集距離) を出力せよ。\n\n"
        "## 制約\n\n- 1 <= |S|, |T| <= 1000\n\n"
        "## 入力\n\n```\nS\nT\n```\n\n## 出力\n\n編集距離を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nl=sys.stdin.read().split('\\n')\ns,t=l[0],l[1]\nm,n=len(s),len(t)\n"
        "dp=list(range(n+1))\nfor i in range(1,m+1):\n prev=dp[0]\n dp[0]=i\n"
        " for j in range(1,n+1):\n  cur=dp[j]\n"
        "  dp[j]=prev if s[i-1]==t[j-1] else 1+min(prev,dp[j],dp[j-1])\n  prev=cur\nprint(dp[n])\n"
    ),
    gen=lambda d, rng: _rstr(rng, rng.randint(1, 50), "abc") + "\n" + _rstr(rng, rng.randint(1, 50), "abc") + "\n",
    edges=lambda d: ["kitten\nsitting\n", "abc\nabc\n"],
)

family(
    key="coin-change", topic="dp", tags=["dp", "knapsack"],
    difficulties=[3], per_diff=6,
    title=lambda d: "最小硬貨枚数",
    statement=lambda d: (
        "硬貨の種類 N と金額 X、続けて N 種類の硬貨の額面が与えられる。"
        "ちょうど X を支払う最小枚数を出力せよ。支払えなければ `-1` を出力する。\n\n"
        "## 制約\n\n- 1 <= N <= 20\n- 1 <= X <= 20000\n- 1 <= 額面 <= 20000\n\n"
        "## 入力\n\n```\nN X\nc_1 ... c_N\n```\n\n## 出力\n\n最小枚数、または `-1` を出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn,x=int(d[0]),int(d[1])\nc=list(map(int,d[2:2+n]))\n"
        "INF=float('inf')\ndp=[0]+[INF]*x\n"
        "for v in range(1,x+1):\n for coin in c:\n  if coin<=v and dp[v-coin]+1<dp[v]:dp[v]=dp[v-coin]+1\n"
        "print(dp[x] if dp[x]!=INF else -1)\n"
    ),
    gen=lambda d, rng: _gen_coin(rng),
    edges=lambda d: ["3 11\n1 2 5\n", "1 3\n2\n"],
)


def _gen_coin(rng):
    n = rng.randint(1, 6)
    coins = sorted(set(rng.randint(1, 50) for _ in range(n)))
    x = rng.randint(1, 2000)
    return f"{len(coins)} {x}\n{' '.join(map(str,coins))}\n"


family(
    key="knapsack01", topic="dp", tags=["dp", "knapsack"],
    difficulties=[3], per_diff=6,
    title=lambda d: "0/1 ナップサック",
    statement=lambda d: (
        "N 個の品物 (重さ w_i, 価値 v_i) と容量 W が与えられる。重さの合計が W 以下"
        "となるよう品物を選んだときの価値の最大値を出力せよ。\n\n"
        "## 制約\n\n- 1 <= N <= 100\n- 1 <= W <= 10000\n- 1 <= w_i, v_i <= 1000\n\n"
        "## 入力\n\n```\nN W\nw_1 v_1\n...\nw_N v_N\n```\n\n## 出力\n\n価値の最大値を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\ndata=sys.stdin.read().split()\ni=0\nn=int(data[i]);i+=1\nW=int(data[i]);i+=1\n"
        "dp=[0]*(W+1)\n"
        "for _ in range(n):\n w=int(data[i]);v=int(data[i+1]);i+=2\n"
        " for c in range(W,w-1,-1):\n  if dp[c-w]+v>dp[c]:dp[c]=dp[c-w]+v\nprint(dp[W])\n"
    ),
    gen=lambda d, rng: _gen_knap(rng),
    edges=lambda d: ["3 4\n2 3\n1 2\n3 4\n", "1 1\n2 5\n"],
)


def _gen_knap(rng):
    n = rng.randint(1, 30)
    W = rng.randint(1, 200)
    lines = [f"{n} {W}"]
    for _ in range(n):
        lines.append(f"{rng.randint(1,50)} {rng.randint(1,100)}")
    return "\n".join(lines) + "\n"


family(
    key="lis", topic="dp", tags=["dp", "sequence"],
    difficulties=[3], per_diff=6,
    title=lambda d: "最長増加部分列",
    statement=lambda d: (
        "N 個の整数からなる数列の、最長の狭義増加部分列の長さを出力せよ。\n\n"
        "## 制約\n\n- 1 <= N <= 100000\n- 各要素の絶対値 <= 10^9\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n最長増加部分列の長さを 1 行で出力する。\n"
    ),
    solution=(
        "import sys,bisect\nd=sys.stdin.read().split()\nn=int(d[0])\na=list(map(int,d[1:1+n]))\n"
        "t=[]\nfor x in a:\n i=bisect.bisect_left(t,x)\n"
        " if i==len(t):t.append(x)\n else:t[i]=x\nprint(len(t))\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,-1000,1000)))}\n")(rng.randint(1, 2000)),
    edges=lambda d: ["5\n1 3 2 4 3\n", "1\n5\n"],
)

# ===========================================================================
# GREEDY
# ===========================================================================

family(
    key="max-meetings", topic="greedy", tags=["greedy", "interval"],
    difficulties=[2, 3], per_diff=4,
    title=lambda d: "区間スケジューリング",
    statement=lambda d: (
        "N 個の区間 (開始 s_i, 終了 e_i) が与えられる。互いに重ならないように選べる"
        "区間の最大数を出力せよ (端点の一致は重ならないとみなす)。\n\n"
        f"## 制約\n\n- 1 <= N <= {200 if d==2 else 10**5}\n- 0 <= s_i < e_i <= 10^9\n\n"
        "## 入力\n\n```\nN\ns_1 e_1\n...\ns_N e_N\n```\n\n## 出力\n\n選べる区間の最大数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\ndata=sys.stdin.read().split()\ni=0\nn=int(data[i]);i+=1\n"
        "iv=[]\nfor _ in range(n):\n s=int(data[i]);e=int(data[i+1]);i+=2\n iv.append((e,s))\n"
        "iv.sort()\ncnt=0\nlast=-1\n"
        "for e,s in iv:\n if s>=last:cnt+=1;last=e\nprint(cnt)\n"
    ),
    gen=lambda d, rng: _gen_intervals(d, rng),
    edges=lambda d: ["3\n1 2\n2 3\n1 3\n", "1\n0 5\n"],
)


def _gen_intervals(d, rng):
    n = rng.randint(1, 100 if d == 2 else 1000)
    lines = [str(n)]
    for _ in range(n):
        s = rng.randint(0, 1000)
        e = s + rng.randint(1, 100)
        lines.append(f"{s} {e}")
    return "\n".join(lines) + "\n"


family(
    key="min-coins-greedy", topic="greedy", tags=["greedy"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "硬貨の最小枚数 (正準系)",
    statement=lambda d: (
        "額面 1, 5, 10, 50, 100, 500 の硬貨を使って金額 X をちょうど支払う"
        "最小枚数を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= X <= {1000 if d==1 else 10**9}\n\n"
        "## 入力\n\n```\nX\n```\n\n## 出力\n\n最小枚数を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nx=int(sys.stdin.read())\nc=0\n"
        "for v in (500,100,50,10,5,1):\n c+=x//v\n x%=v\nprint(c)\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1, 1000 if d==1 else 10**9)}\n",
    edges=lambda d: ["1\n", "999\n", "500\n"],
)

family(
    key="max-product-pair", topic="greedy", tags=["greedy", "array"],
    difficulties=[2, 3], per_diff=3,
    title=lambda d: "2 数の積の最大値",
    statement=lambda d: (
        "N 個の整数から 2 つを選んだときの積の最大値を出力せよ。\n\n"
        f"## 制約\n\n- 2 <= N <= {200 if d==2 else 10**5}\n- 各要素の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n積の最大値を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=sorted(map(int,d[1:1+n]))\n"
        "print(max(a[-1]*a[-2],a[0]*a[1]))\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,-1000,1000)))}\n")(rng.randint(2, 100 if d == 2 else 1000)),
    edges=lambda d: ["2\n3 4\n", "4\n-5 -4 1 2\n"],
)

# ===========================================================================
# GEOMETRY
# ===========================================================================

family(
    key="rect-area", topic="geometry", tags=["formula"],
    difficulties=[1], per_diff=4,
    title=lambda d: "長方形の面積",
    statement=lambda d: (
        "長方形の幅 W と高さ H が与えられる。面積を出力せよ。\n\n"
        "## 制約\n\n- 1 <= W, H <= 10^9\n\n"
        "## 入力\n\n```\nW H\n```\n\n## 出力\n\n面積を 1 行で出力する。\n"
    ),
    solution="import sys\nw,h=map(int,sys.stdin.read().split())\nprint(w*h)\n",
    gen=lambda d, rng: f"{rng.randint(1,10**9)} {rng.randint(1,10**9)}\n",
    edges=lambda d: ["1 1\n", "3 4\n"],
)

family(
    key="manhattan", topic="geometry", tags=["distance"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "マンハッタン距離",
    statement=lambda d: (
        "2 点 (x1, y1), (x2, y2) のマンハッタン距離 |x1-x2| + |y1-y2| を出力せよ。\n\n"
        "## 制約\n\n- 座標の絶対値 <= 10^9\n\n"
        "## 入力\n\n```\nx1 y1 x2 y2\n```\n\n## 出力\n\nマンハッタン距離を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nx1,y1,x2,y2=map(int,sys.stdin.read().split())\nprint(abs(x1-x2)+abs(y1-y2))\n"
    ),
    gen=lambda d, rng: f"{rng.randint(-10**6,10**6)} {rng.randint(-10**6,10**6)} {rng.randint(-10**6,10**6)} {rng.randint(-10**6,10**6)}\n",
    edges=lambda d: ["0 0 0 0\n", "1 2 4 6\n"],
)

family(
    key="dist-sq", topic="geometry", tags=["distance"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "2 点間距離の 2 乗",
    statement=lambda d: (
        "2 点 (x1, y1), (x2, y2) のユークリッド距離の 2 乗 (整数) を出力せよ。\n\n"
        "## 制約\n\n- 座標の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nx1 y1 x2 y2\n```\n\n## 出力\n\n距離の 2 乗を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nx1,y1,x2,y2=map(int,sys.stdin.read().split())\nprint((x1-x2)**2+(y1-y2)**2)\n"
    ),
    gen=lambda d, rng: f"{rng.randint(-10**6,10**6)} {rng.randint(-10**6,10**6)} {rng.randint(-10**6,10**6)} {rng.randint(-10**6,10**6)}\n",
    edges=lambda d: ["0 0 3 4\n", "1 1 1 1\n"],
)

family(
    key="point-in-rect", topic="geometry", tags=["check"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "点が長方形の内部か",
    statement=lambda d: (
        "軸平行な長方形の左下 (x1, y1) と右上 (x2, y2)、および点 (px, py) が"
        "与えられる。点が長方形の内部または境界上にあれば `Yes`、なければ `No` を出力せよ。\n\n"
        "## 制約\n\n- 座標の絶対値 <= 10^9, x1<x2, y1<y2\n\n"
        "## 入力\n\n```\nx1 y1 x2 y2\npx py\n```\n\n## 出力\n\n`Yes` または `No` を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=list(map(int,sys.stdin.read().split()))\nx1,y1,x2,y2,px,py=d\n"
        "print('Yes' if x1<=px<=x2 and y1<=py<=y2 else 'No')\n"
    ),
    gen=lambda d, rng: _gen_point_rect(rng),
    edges=lambda d: ["0 0 10 10\n5 5\n", "0 0 10 10\n20 5\n"],
)


def _gen_point_rect(rng):
    x1 = rng.randint(-1000, 0)
    y1 = rng.randint(-1000, 0)
    x2 = rng.randint(1, 1000)
    y2 = rng.randint(1, 1000)
    px = rng.randint(-1500, 1500)
    py = rng.randint(-1500, 1500)
    return f"{x1} {y1} {x2} {y2}\n{px} {py}\n"


# ===========================================================================
# MATRIX
# ===========================================================================

family(
    key="matrix-diag", topic="matrix", tags=["matrix", "sum"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "正方行列の対角成分の和",
    statement=lambda d: (
        "N x N の整数行列が与えられる。主対角成分の和を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {10 if d==1 else 100}\n- 各要素の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nN\n行列 (N 行 N 列)\n```\n\n## 出力\n\n対角成分の和を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\ndata=sys.stdin.read().split()\nn=int(data[0])\n"
        "s=sum(int(data[1+i*n+i]) for i in range(n))\nprint(s)\n"
    ),
    gen=lambda d, rng: _gen_matrix(d, rng),
    edges=lambda d: ["2\n1 2\n3 4\n"],
)


def _gen_matrix(d, rng):
    n = rng.randint(1, 8 if d == 1 else 40)
    lines = [str(n)]
    for _ in range(n):
        lines.append(" ".join(str(rng.randint(-1000, 1000)) for _ in range(n)))
    return "\n".join(lines) + "\n"


family(
    key="matrix-transpose", topic="matrix", tags=["matrix"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "行列の転置",
    statement=lambda d: (
        "R 行 C 列の整数行列が与えられる。転置 (C 行 R 列) を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= R, C <= {6 if d==1 else 50}\n- 各要素の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nR C\n行列 (R 行 C 列)\n```\n\n## 出力\n\n転置行列を R 列 C 行で出力する。\n"
    ),
    solution=(
        "import sys\ndata=sys.stdin.read().split()\nr=int(data[0]);c=int(data[1])\n"
        "m=[[int(data[2+i*c+j]) for j in range(c)] for i in range(r)]\n"
        "out=[]\nfor j in range(c):\n out.append(' '.join(str(m[i][j]) for i in range(r)))\n"
        "print('\\n'.join(out))\n"
    ),
    gen=lambda d, rng: _gen_rc_matrix(d, rng),
    edges=lambda d: ["2 3\n1 2 3\n4 5 6\n"],
)


def _gen_rc_matrix(d, rng):
    r = rng.randint(1, 5 if d == 1 else 20)
    c = rng.randint(1, 5 if d == 1 else 20)
    lines = [f"{r} {c}"]
    for _ in range(r):
        lines.append(" ".join(str(rng.randint(-1000, 1000)) for _ in range(c)))
    return "\n".join(lines) + "\n"


family(
    key="dot-product", topic="matrix", tags=["vector"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "ベクトルの内積",
    statement=lambda d: (
        "長さ N の 2 つの整数ベクトル a, b が与えられる。内積を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= 10^6\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\nb_1 ... b_N\n```\n\n## 出力\n\n内積を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\n"
        "a=list(map(int,d[1:1+n]))\nb=list(map(int,d[1+n:1+2*n]))\n"
        "print(sum(x*y for x,y in zip(a,b)))\n"
    ),
    gen=lambda d, rng: _gen_dot(d, rng),
    edges=lambda d: ["2\n1 2\n3 4\n"],
)


def _gen_dot(d, rng):
    n = _n(rng, min(d, 3))
    a = " ".join(str(rng.randint(-1000, 1000)) for _ in range(n))
    b = " ".join(str(rng.randint(-1000, 1000)) for _ in range(n))
    return f"{n}\n{a}\n{b}\n"


# ===========================================================================
# SIMULATION / MISC
# ===========================================================================

family(
    key="fizzbuzz", topic="simulation", tags=["loop", "io"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "FizzBuzz",
    statement=lambda d: (
        "整数 N が与えられる。1 から N まで各行に出力する。ただし 3 の倍数は `Fizz`、"
        "5 の倍数は `Buzz`、両方の倍数は `FizzBuzz` と出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {30 if d==1 else 10000}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\nN 行に渡って出力する。\n"
    ),
    solution=(
        "import sys\nn=int(sys.stdin.read())\nout=[]\n"
        "for i in range(1,n+1):\n"
        " if i%15==0:out.append('FizzBuzz')\n elif i%3==0:out.append('Fizz')\n"
        " elif i%5==0:out.append('Buzz')\n else:out.append(str(i))\nprint('\\n'.join(out))\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1, 30 if d==1 else 5000)}\n",
    edges=lambda d: ["1\n", "15\n", "5\n"],
)

family(
    key="count-bits", topic="simulation", tags=["bit"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "立っているビットの数",
    statement=lambda d: (
        "非負整数 N の 2 進表現で 1 になっているビットの個数 (popcount) を出力せよ。\n\n"
        f"## 制約\n\n- 0 <= N <= {255 if d==1 else 10**18}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n1 のビット数を 1 行で出力する。\n"
    ),
    solution="import sys\nprint(bin(int(sys.stdin.read())).count('1'))\n",
    gen=lambda d, rng: f"{rng.randint(0, 255 if d==1 else 10**18)}\n",
    edges=lambda d: ["0\n", "7\n", "255\n"],
)

family(
    key="to-binary", topic="simulation", tags=["bit", "base"],
    difficulties=[1, 2], per_diff=3,
    title=lambda d: "10 進数を 2 進数に変換",
    statement=lambda d: (
        "非負整数 N を 2 進表現に変換して出力せよ (先頭 0 なし、N=0 は `0`)。\n\n"
        f"## 制約\n\n- 0 <= N <= {255 if d==1 else 10**18}\n\n"
        "## 入力\n\n```\nN\n```\n\n## 出力\n\n2 進表現を 1 行で出力する。\n"
    ),
    solution="import sys\nprint(bin(int(sys.stdin.read()))[2:])\n",
    gen=lambda d, rng: f"{rng.randint(0, 255 if d==1 else 10**18)}\n",
    edges=lambda d: ["0\n", "1\n", "10\n"],
)

family(
    key="grade", topic="simulation", tags=["branch"],
    difficulties=[1], per_diff=4,
    title=lambda d: "点数から評価",
    statement=lambda d: (
        "0 以上 100 以下の整数の点数 X が与えられる。90 以上なら `A`、70 以上なら"
        " `B`、50 以上なら `C`、それ未満なら `D` を出力せよ。\n\n"
        "## 制約\n\n- 0 <= X <= 100\n\n"
        "## 入力\n\n```\nX\n```\n\n## 出力\n\n評価を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nx=int(sys.stdin.read())\n"
        "print('A' if x>=90 else 'B' if x>=70 else 'C' if x>=50 else 'D')\n"
    ),
    gen=lambda d, rng: f"{rng.randint(0,100)}\n",
    edges=lambda d: ["90\n", "0\n", "100\n", "49\n"],
)

family(
    key="leap-year", topic="simulation", tags=["branch"],
    difficulties=[1], per_diff=4,
    title=lambda d: "うるう年判定",
    statement=lambda d: (
        "西暦 Y が与えられる。うるう年なら `Yes`、そうでなければ `No` を出力せよ。"
        " (4 で割り切れ、かつ 100 で割り切れない、または 400 で割り切れる年がうるう年)\n\n"
        "## 制約\n\n- 1 <= Y <= 10^9\n\n"
        "## 入力\n\n```\nY\n```\n\n## 出力\n\n`Yes` または `No` を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\ny=int(sys.stdin.read())\n"
        "print('Yes' if (y%4==0 and y%100!=0) or y%400==0 else 'No')\n"
    ),
    gen=lambda d, rng: f"{rng.randint(1,3000)}\n",
    edges=lambda d: ["2000\n", "1900\n", "2024\n", "2023\n"],
)

family(
    key="abs-diff", topic="math", tags=["arithmetic"],
    difficulties=[1], per_diff=4,
    title=lambda d: "差の絶対値",
    statement=lambda d: (
        "2 つの整数 A, B が与えられる。|A - B| を出力せよ。\n\n"
        "## 制約\n\n- |A|, |B| <= 10^9\n\n"
        "## 入力\n\n```\nA B\n```\n\n## 出力\n\n|A - B| を 1 行で出力する。\n"
    ),
    solution="import sys\na,b=map(int,sys.stdin.read().split())\nprint(abs(a-b))\n",
    gen=lambda d, rng: f"{rng.randint(-10**9,10**9)} {rng.randint(-10**9,10**9)}\n",
    edges=lambda d: ["0 0\n", "5 3\n", "3 5\n"],
)

family(
    key="min-max-range", topic="array", tags=["aggregate"],
    difficulties=[1, 2, 3], per_diff=3,
    title=lambda d: "最大値と最小値の差",
    statement=lambda d: (
        "N 個の整数の最大値と最小値の差を出力せよ。\n\n"
        f"## 制約\n\n- 1 <= N <= {N_BY_DIFF[d][1]}\n- 各要素の絶対値 <= {V_BY_DIFF[d][1]}\n\n"
        "## 入力\n\n```\nN\na_1 ... a_N\n```\n\n## 出力\n\n差を 1 行で出力する。\n"
    ),
    solution=(
        "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\na=list(map(int,d[1:1+n]))\n"
        "print(max(a)-min(a))\n"
    ),
    gen=lambda d, rng: (lambda n: f"{n}\n{' '.join(map(str,_rlist(rng,n,*V_BY_DIFF[d])))}\n")(_n(rng, min(d, 3))),
    edges=lambda d: ["1\n5\n", "3\n1 5 3\n"],
)
