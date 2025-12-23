# Reversing Conway's Game of Life
<!-- date={2024-10-03} -->
<!-- life-viewer -->

A few days ago the YouTube channel [Alpha Phoenix uploaded a
video about running Conway's Game of Life backwards.](https://youtu.be/g8pjrVbdafY?feature=shared) It's a great video,
but the solution Alpha Phoenix used was based on using a constraint solver and
it inspired me to try implementing my own solver for reverse Game of Life to see how a backtracking search would perform in comparison.
So I wrote a backtracking search solution in Julia. It runs pretty quickly on small inputs but gets exponentially slower for larger inputs.

Here is an example of one of my test cases:

<div class="viewer">
<textarea style="display:none">#C [[ GRID COLOR GRID 192 192 192 GRIDMAJOR 10 COLOR GRIDMAJOR 128 128 128 COLOR DEADRAMP 255 220 192 COLOR ALIVE 0 0 0 COLOR ALIVERAMP 0 0 0 COLOR DEAD 192 220 255 COLOR BACKGROUND 255 255 255 WIDTH 937 HEIGHT 600 AUTOSTART GPS 1 LOOP 6 ]]
x = 0, y = 0, rule = B3/S23
18b$bo3bo3bo8b$3bo4bo2bob2obob$2b2obobo2b3o5b$bobo4bo2bobobo2b$3b2ob3o4bobo2b$2b2o7bo2bo3b$2b3obo4bob2obob$5b2ob4o3bo2b$2b3o4bo2b2ob2ob$3b2o6bo3b2ob$2b4ob2o2bobobo2b$3bobob4o2bobo2b$3bo4bo9b$bo3bobo3bobobo2b$18b$!
</textarea><br/>
<canvas></canvas>
</div>

The largest test I did so far was a rasterization of the text `REVERSE`. My implementation only managed to run it 3 steps backwards and got stuck on the 4th step:

<div class="viewer">
<textarea style="display:none">#C [[ ZOOM 16 GRID COLOR GRID 192 192 192 GRIDMAJOR 10 COLOR GRIDMAJOR 128 128 128 COLOR DEADRAMP 255 220 192 COLOR ALIVE 0 0 0 COLOR ALIVERAMP 0 0 0 COLOR DEAD 192 220 255 COLOR BACKGROUND 255 255 255 WIDTH 937 HEIGHT 600 AUTOSTART GPS 1 LOOP 4 ]]
x = 0, y = 0, rule = B3/S23
56b$2bobobo8b2obobo3b3o6bo4bo3b2obo10b$2bobobo6b5o4b7ob2o3b2o9bob2ob2o3b$3bo4bobo2bobob2obo3bo3b2o3bo2b2obobob2obob3o2bo2b$bob2obobo2b3o2bobobo6b2obob2o7bob2o4bobo4b$3bo5b2o2bo11bobo2bob2o4bo5bo3b2ob3o2b$2b3o5bo3bo2bo4b3ob2obobob3ob2ob3o2b2o5bo3b$3bo3bobobob7o4b2o10b4ob2o3bobo4bo2b$4bo6b2o2bo2bob2o3bo5b3o9bo3bo2b4o2b$bo3bobo3b2o6bo5bo2bobob3ob2ob2obob2obo2bob3ob$bobo2b3o5bobob5ob2ob2o2b3o2b2ob2obob5o3b3ob$7b2o7bob2o9bobo8bo7b2o3bo2b$4b2o4b2o9bob2obo2bobo2bobobo2bob2o9bob$56b$!
</textarea><br/>
<canvas></canvas>
</div>

The problem with my solutions is that they grow in size, each predecessor state requires searching over more pixels which slows down the search a lot. For the `REVERSE` example the 3rd step took 15 seconds but the 4th step did not complete: I stopped it after more than 4 hours.

Update: I rewrote and optimized my search function and finally the 4th iteration of the `REVERSE` example finished without a solution after 15 hours.
If my code is correct the 3rd iteration shown above is [a so-called Garden of Eden](https://conwaylife.com/wiki/Garden_of_Eden), that is, a game state which has no predecessors.

## Julia Code
Anyway here is my Julia code if you want to try it for yourself:

```jl
b_north = 1<<0 + 1<<1 + 1<<2
b_south = 1<<6 + 1<<7 + 1<<8
b_ew = 1<<3 + 1<<4 + 1<<5  # line east-west
b_west = 1<<0 + 1<<3 + 1<<6
b_east = 1<<2 + 1<<5 + 1<<8
b_ns = 1<<1 + 1<<4 + 1<<7 # line north-south

neighbors(G, r, c) = G[r-1, c] + G[r-1, c-1] + G[r-1, c+1] + G[r+1, c] + G[r+1, c-1] + G[r+1, c+1] + G[r, c-1] + G[r, c+1]

function sim(G)
    H, W = size(G)
    F = fill(0, H, W)
    for r in 2:(H-1)
        for c in 2:(W-1)
            n = neighbors(G, r, c)
            F[r,c] = n == 3 || G[r,c] + n == 3
        end
    end
    return F
end

function disp(A::Matrix{Int}; border=true)
    H,W = size(A)
    if border
        println("."^W)
    end
    for r in 2:(H-1)
        if border
            print(".")
        end
        for c in 2:(W-1)
            print(" #"[A[r, c] + 1])
        end
        if border
            println(".")
        else
            println()
        end
    end
    if border
        println("."^W)
    end
end

function disp(A::Int)
    println("."^5)
    for r in 0:2
        print(".")
        for c in 0:2
            print(" #"[(A >> (r*3 + c))&1 + 1])
        end
        println(".")
    end
    println("."^5)
end

function load_input(filename::String, pad=0)
    f = open(filename, "r")
    lines = readlines(f)
    H = length(lines) + 2 + 2*pad
    W = max(map(x->length(x), lines)...) + 2 + 2*pad

    G = fill(0, H, W)
    for r in 1:length(lines)
        for c in 1:length(lines[r])
            if lines[r][c] == '#'
                G[r+1+pad,c+1+pad] = 1
            end
        end
    end
    return G
end

function find_ancestors()
    global live, dead
    G = fill(0, 5, 5)
    live = Set{Int}()
    dead = Set{Int}()
    for i in 0:(1<<9-1)
        for r in 0:2
            for c in 0:2
                G[r+2, c+2] = (i >> (r*3 + c)) & 1
            end
        end
        F = sim(G)
        if F[3,3] == 1
            push!(live, i)
        else
            push!(dead, i)
        end
        # disp(G)
    end
end

function search(P)
    H, W = size(P)
    L = []
    for c in 2:(W-1)
        for r in 2:(H-1)
            push!(L, (r,c))
        end
    end
    S = fill(1, length(L))
    Q = fill(0, length(L))
    i = 1
    while i <= length(L)
        r,c = L[i]
        mask = value = 0
        if r > 2
            value = Q[i-1] >> 3
            mask = b_north | b_ew
        end
        if c > 2
            value |= (Q[i-H+2] >> 1) & (b_west | b_ns)
            mask |= b_west | b_ns
        end
        value &= mask
        while S[i] <= length(P[r,c])
            p = P[r,c][S[i]]
            if (p & mask) == value
                Q[i] = p
                break
            end
            S[i] += 1
        end
        if S[i] <= length(P[r,c])
            i += 1
        else
            S[i] = 1
            i -= 1
            if i == 0
                return nothing
            end
            S[i] += 1
        end
    end
    F = fill(0, H, W)
    for i in 1:length(L)
        F[L[i]...] = (Q[i] >> 4) & 1
    end
    return F
end

function bitmask(u, v)
    c = 0
    for x in -1:1
        for y in -1:1
            if -1 <= y+u  <= 1 && -1 <= x+v <= 1
                c += 1 << ((y+u+1)*3 + x+v+1)
            end
        end
    end
    return c
end

function cull(G::Matrix{Int}, P, H, W)
    mask = fill(0, 3, 3)
    for x in -1:1
        for y in -1:1
            mask[y+2, x+2] = bitmask(y, x)
        end
    end
    culled = 0
    for r in 2:(H-1)
        for c in 2:(W-1)
            if G[r,c] == 1
                continue
            end
            diff = Set{Int}()
            for p in P[r,c]
                for (u,v) in [(1,0), (-1,0), (0,1), (0,-1)]
                    if 2 <= r+u <= H-1 && 2 <= c+v <= W-1
                        if G[r+u, c+v] == 1 && count_ones(mask[u+2, v+2] & p) > 4
                            push!(diff, p)
                        end
                    end
                end
            end
            culled += length(diff)
            setdiff!(P[r,c], diff)
        end
    end
end

function reverse(filename::String)
    find_ancestors()

    G = load_input(filename)
    H,W = size(G)
    possible = fill(Set{Int}(), H, W)
    global live, dead
    for r in 2:(H-1)
        for c in 2:(W-1)
            if G[r,c] == 1
                possible[r,c] = copy(live)
            else
                possible[r,c] = copy(dead)
            end
        end
    end

    for r in 2:(H-1)
        diff = Set{Int}()
        for p in possible[r,2]
            if (p & b_west) != 0 || count_ones(p & b_ns) == 3
                push!(diff, p)
            end
        end
        setdiff!(possible[r,2], diff)
        diff = Set{Int}()
        for p in possible[r,W-1]
            if (p & b_east) != 0 || count_ones(p & b_ns) == 3
                push!(diff, p)
            end
        end
        setdiff!(possible[r,W-1], diff)
    end
    for c in 2:(W-1)
        diff = Set{Int}()
        for p in possible[2,c]
            if (p & b_north) != 0 || count_ones(p & b_ew) == 3
                push!(diff, p)
            end
        end
        setdiff!(possible[2,c], diff)
        diff = Set{Int}()
        for p in possible[H-1,c]
            if (p & b_south) != 0 || count_ones(p & b_ew) == 3
                push!(diff, p)
            end
        end
        setdiff!(possible[H-1,c], diff)
    end

    cull(G, possible, H, W)

    P = possible
    possible = fill([], size(P))
    for r in 1:H
        for c in 1:W
            possible[r,c] = sort(collect(P[r,c]), by=count_ones)
        end
    end

    F = search(possible)
    if F isa Nothing
        println("No solution found!")
    else
        disp(F)
    end
end

filename = "big_reverse.txt"
@time reverse(filename)
```

This script expects a file named `big_reverse.txt` in the working directory containing a text representation of a Game of Life board where `#` denotes a living cell (all other non-newline characters are treated as dead). For example:

```
    ..................................................
    .#####  ###### #    # ###### #####   ####  ######.
    .#    # #      #    # #      #    # #      #     .
    .#    # #####  #    # #####  #    #  ####  ##### .
    .#####  #      #    # #      #####       # #     .
    .#   #  #       #  #  #      #   #  #    # #     .
    .#    # ######   ##   ###### #    #  ####  ######.
    ..................................................
```

## C Code

[Here is my C implementation:](https://gist.github.com/llbit/c3d9604383696aefcfdd84f7487e7783)

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <stdbool.h>
#include <stdint.h>

#define b_north ((1<<0) + (1<<1) + (1<<2))
#define b_south ((1<<6) + (1<<7) + (1<<8))
#define b_ew    ((1<<3) + (1<<4) + (1<<5))
#define b_west  ((1<<0) + (1<<3) + (1<<6))
#define b_east  ((1<<2) + (1<<5) + (1<<8))
#define b_ns    ((1<<1) + (1<<4) + (1<<7))
#define b_n (b_north | b_ew)
#define b_s (b_south | b_ew)
#define b_e (b_east | b_ns)
#define b_w (b_west | b_ns)

typedef struct Line Line;
struct Line {
  char* text;
  Line* next;
};

typedef struct {
  int n;
  uint64_t data[];
} BitSet;

typedef struct {
  int n;
  unsigned* data;
} Array;

static int count_ones(uint64_t x)
{
  int s = 0;
  while (x != 0) {
    s += x&1;
    x >>= 1;
  }
  return s;
}

static BitSet* bs(int n)
{
  int k = (n + 63) / 64;
  BitSet* bs = malloc(sizeof(BitSet) + 8 * k);
  bs->n = k;
  memset(bs->data, 0, 8 * k);
  return bs;
}

static int bs_size(BitSet* bs)
{
  int s = 0;
  for (int i = 0; i < bs->n; ++i) {
    s += count_ones(bs->data[i]);
  }
  return s;
}

static void set_bit(BitSet* bs, int b)
{
  bs->data[b>>6] |= (1ULL<<(b & 0x3F));
}

static void clear_bit(BitSet* bs, int b)
{
  bs->data[b>>6] &= ~(1ULL<<(b & 0x3F));
}

static int get_bit(BitSet* bs, int b)
{
  return (bs->data[b>>6] >> (b & 0x3F)) & 1;
}

void disp(unsigned* board, int H, int W)
{
  for (int r = 0; r < H; ++r) {
    for (int c = 0; c < W; ++c) {
      printf("%c", board[r * W + c] ? '#' : ' ');
    }
    printf("\n");
  }
}

int neighbors[][2] = {
  {-1, -1}, {-1, 0}, {-1, 1},
  {0, -1 },          {0, 1 },
  {1, -1 }, {1, 0 }, {1, 1 },
};
int nsew[][2] = {
                  {-2, 0},
                  {-1, 0},
 {0, -2}, {0, -1},         {0, 1}, {0, 2},
                  {1, 0 },
                  {2, 0 },
};

int count(unsigned* B, int H, int W, int r, int c)
{
  int n = 0;
  for (int i = 0; i < 8; ++i) {
    n += B[(r + neighbors[i][0])*W + c + neighbors[i][1]];
  }
  return n;
}

void sim(unsigned* start, unsigned* next, int H, int W)
{
  for (int r = 1; r < H-1; ++r) {
    for (int c = 1; c < W-1; ++c) {
      // count neighbors
      int n = count(start, H, W, r, c);
      if (start[r*W + c]) {
        // 2-3 neighbors stay alive
        next[r * W + c] = (n == 2 || n == 3) ? 1 : 0;
      } else {
        // 3 neighbors get born
        next[r * W + c] = n == 3 ? 1 : 0;
      }
    }
  }
}

static void enum_states(Array* live, Array* dead)
{
  int scratch[5*5];
  int out[5*5];
  memset(scratch, 0, sizeof(int) * 5 * 5);
  for (int p = 0; p < (1<<9); ++p) {
    for (int r = 0; r < 3; ++r) {
      for (int c = 0; c < 3; ++c) {
        scratch[(r+1)*5 + c + 1] = (p >> (r*3 + c)) & 1;
      }
    }
    sim(scratch, out, 5, 5);
    if (out[2*5 + 2]) {
      live->data[live->n++] = p;
    } else {
      dead->data[dead->n++] = p;
    }
  }
}

static void search(Array* A, int H, int W)
{
  int n = 0;
  int L[H*W][2];
  for (int c = 1; c < W-1; ++c) {
    for (int r = 1; r < H-1; ++r) {
      L[n][0] = r;
      L[n++][1] = c;
    }
  }
  int Q[n];
  int S[n];
  S[0] = 0;
  int i = 0;
  while (true) {
    int r = L[i][0];
    int c = L[i][1];
    int mask = 0;
    int value = 0;
    if (r > 1) {
      value = Q[i-1] >> 3;
      mask = b_north | b_ew;
    }
    if (c > 1) {
      value |= (Q[i-H+2] >> 1) & (b_west | b_ns);
      mask |= b_west | b_ns;
    }
    value &= mask;
    Array aa = A[r*W + c];
    while (S[i] < aa.n) {
      int p = aa.data[S[i]];
      if ((p & mask) == value) {
        Q[i] = p;
        break;
      }
      S[i] += 1;
    }
    if (S[i] < aa.n) {
      i += 1;
      if (i == n) {
        break;
      }
      S[i] = 0;
    } else {
      S[i] = 0;
      i -= 1;
      if (i < 0) {
        fprintf(stderr, "Input is a Garden of Eden.\n");
        return;
      }
      S[i] += 1;
    }
  }
  int board[H*W];
  memset(board, 0, sizeof(int)*H*W);
  for (i = 0; i < n; ++i) {
    int r = L[i][0];
    int c = L[i][1];
    board[r*W + c] = (Q[i] >> 4) & 1;
  }
  disp(board, H, W);
}

static void cull(Array* A, int H, int W)
{
  BitSet* d1 = bs(H*W);
  BitSet* d2 = bs(H*W);
  Array q1 = {
    .n = 0,
    .data = malloc(sizeof(int) * H*W * 2),
  };
  Array q2 = {
    .n = 0,
    .data = malloc(sizeof(int) * H*W * 2),
  };
  for (int r = 1; r < H-1; ++r) {
    for (int c = 1; c < W-1; ++c) {
      q1.data[q1.n++] = r;
      q1.data[q1.n++] = c;
    }
  }
  int pp[][5] = {
    { -1,  0, 0, 3, b_north | b_ew },
    { -2,  0, 0, 6, b_north },
    {  1,  0, 3, 0, b_south | b_ew },
    {  2,  0, 6, 0, b_south },
    {  0, -1, 0, 1, b_west | b_ns },
    {  0, -2, 0, 2, b_west },
    {  0,  1, 1, 0, b_east | b_ns },
    {  0,  2, 2, 0, b_east },
    { -1, -1, 0, 4, (1<<0) | (1<<1) | (1<<3) | (1<<4) },
    {  1,  1, 4, 0, (1<<4) | (1<<5) | (1<<7) | (1<<8) },
    { -1,  1, 0, 2, (1<<1) | (1<<2) | (1<<4) | (1<<5) },
    {  1, -1, 2, 0, (1<<3) | (1<<4) | (1<<6) | (1<<7) },
  };
  int N = sizeof(pp) / sizeof(pp[0]);
  int culled = 0;
  bool change = true;
  while (change) {
    change = false;
    for (int k = 0; k < q1.n; k += 2) {
      int r = q1.data[k];
      int c = q1.data[k + 1];
      Array* A0 = A + (r*W + c);
      for (int i = 0; i < A0->n; ++i) {
        int p = A0->data[i];
        int match = 0;
        for (int w = 0; w < N; ++w) {
          int r1 = r + pp[w][0];
          int c1 = c + pp[w][1];
          if (r1 >= 0 && r1 < H && c1 >= 0 && c1 < W) {
            Array A1 = A[r1*W + c1];
            int u = pp[w][2];
            int v = pp[w][3];
            int b = pp[w][4];
            for (int j = 0; j < A1.n; ++j) {
              if ((p & b) == ((u ? (A1.data[j] << u) : (A1.data[j] >> v)) & b)) {
                match |= 1<<w;
                break;
              }
            }
          } else {
            match |= 1<<w;
          }
        }
        if (match != (1<<N)-1) {
          A0->data[i] = A0->data[A0->n-1];
          A0->n -= 1;
          culled += 1;
          change = true;
          for (int w = 0; w < N; ++w) {
            int r1 = r + pp[w][0];
            int c1 = c + pp[w][1];
            if (r1 >= 0 && r1 < H && c1 >= 0 && c1 < W && !get_bit(d2, r1*W + c1)) {
              set_bit(d2, r1*W + c1);
              q2.data[q2.n++] = r1;
              q2.data[q2.n++] = c1;
            }
          }
          break;
        }
      }
    }
    BitSet* d = d1;
    d1 = d2;
    d2 = d;
    memset(d2->data, 0, 8*d1->n);
    Array q = q1;
    q1 = q2;
    q2 = q;
    q2.n = 0;
  }
  fprintf(stderr, "culled: %d\n", culled);
  free(d1);
  free(d2);
  free(q1.data);
  free(q2.data);
}

static int cmp_live(const void* pa, const void* pb)
{
  int a = count_ones(*(unsigned*) pa);
  int b = count_ones(*(unsigned*) pb);
  if ((a&(1<<4)) && !(b&(1<<4))) {
    return -1;
  }
  if (!(a&(1<<4)) && (b&(1<<4))) {
    return 1;
  }
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

static int cmp_dead(const void* pa, const void* pb)
{
  int a = count_ones(*(unsigned*) pa);
  int b = count_ones(*(unsigned*) pb);
  if ((a&(1<<4)) && !(b&(1<<4))) {
    return 1;
  }
  if (!(a&(1<<4)) && (b&(1<<4))) {
    return -1;
  }
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

static void reverse(unsigned* ref, int H, int W)
{
  Array live = {
    .n = 0,
    .data = alloca(sizeof(unsigned)<<9),
  };
  Array dead = {
    .n = 0,
    .data = alloca(sizeof(unsigned)<<9),
  };
  enum_states(&live, &dead);
  qsort(live.data, live.n, sizeof(int), cmp_live);
  qsort(dead.data, dead.n, sizeof(int), cmp_dead);
  Array A[H*W];
  for (int i = 0; i < H*W; ++i) {
    Array* set;
    if (ref[i]) {
      set = &live;
    } else {
      set = &dead;
    }
    A[i].n = set->n;
    A[i].data = malloc(sizeof(unsigned) * set->n);
    memcpy(A[i].data, set->data, sizeof(unsigned) * set->n);
  }
  for (int r = 0; r < H; ++r) {
    Array* pA = A + (r*W);
    int i = 0;
    while (i < pA->n) {
      if (pA->data[i] & b_w) {
        pA->n -= 1;
        pA->data[i] = pA->data[pA->n];
      } else {
        i += 1;
      }
    }
    pA = A + (r*W + W-1);
    i = 0;
    while (i < pA->n) {
      if (pA->data[i] & b_e) {
        pA->n -= 1;
        pA->data[i] = pA->data[pA->n];
      } else {
        i += 1;
      }
    }
  }
  for (int c = 0; c < W; ++c) {
    Array* pA = A + c;
    int i = 0;
    while (i < pA->n) {
      if (pA->data[i] & b_n) {
        pA->n -= 1;
        pA->data[i] = pA->data[pA->n];
      } else {
        i += 1;
      }
    }
    pA = A + ((H-1)*W + c);
    i = 0;
    while (i < pA->n) {
      if (pA->data[i] & b_s) {
        pA->n -= 1;
        pA->data[i] = pA->data[pA->n];
      } else {
        i += 1;
      }
    }
  }

  cull(A, H, W);

#if 1
  for (int r = 0; r < H; ++r) {
    for (int c = 0; c < W; ++c) {
      char buf[30];
      snprintf(buf, sizeof(buf), "%d", A[r*W+c].n);
      fprintf(stderr, "%3s ", buf);
    }
    fprintf(stderr, "\n");
  }
#endif

  search(A, H, W);

  for (int i = 0; i < H*W; ++i) {
    free(A[i].data);
  }
}

int main(int argc, char** argv)
{
  int H = 0;
  int W = 0;
  char temp[1<<10];
  size_t bufsize = sizeof(temp);
  Line* head = NULL;
  Line* tail = NULL;
  while (1) {
    char* buf = NULL;
    size_t t;
    ssize_t r = getline(&buf, &t, stdin);
    if (r < 0) {
      free(buf);
      break;
    }
    Line* line = malloc(sizeof(Line));
    *line = (Line) {
      .text = buf,
      .next = NULL,
    };
    if (!head) {
      head = tail = line;
    } else {
      tail->next = line;
      tail = line;
    }
    H += 1;
  }

  tail = head;
  while (tail) {
    char* p = tail->text;
    tail = tail->next;
    int linew = 0;
    while (*p) {
      if (*p != '\n' && *p != '\r') {
        linew += 1;
      }
      p++;
    }
    if (linew > W) W = linew;
  }

  H += 2;
  W += 2;
  size_t boardsz = H * W * sizeof(unsigned);
  unsigned* start = calloc(H * W, sizeof(unsigned));
  tail = head;
  int r = 0;
  int pop = 0;
  while (tail) {
    char* p = tail->text;
    tail = tail->next;
    int c = 0;
    while (*p) {
      if (*p == '#' || *p == 'O') {
        start[(r + 1)*W + c + 1] = 1;
        pop += 1;
        c += 1;
      } else if (*p != '\n' && *p != '\r') {
        c += 1;
      }
      p++;
    }
    r += 1;
  }

  if (argc > 1 && !strcmp(argv[1], "sim")) {
    struct timespec ts = {
      .tv_sec = 0,
      .tv_nsec = 300000000,
    };
    unsigned* next = malloc(boardsz);
    memcpy(next, start, boardsz);
    int step = 0;
    printf("\033[2J"); // Clear screen.
    while (1) {
      printf("\033[Hstep %d\n", step++);
      disp(start, H, W);
      fflush(stdout);
      nanosleep(&ts, NULL);

      sim(start, next, H, W);
      unsigned* t = start;
      start = next;
      next = t;
    }
  } else {
    fprintf(stderr, "Population: %d\n", pop);
    reverse(start, H, W);
  }

  free(start);
  while (head) {
    tail = head;
    tail = head->next;
    free(head->text);
    free(head);
    head = tail;
  }
  return 0;
}
```
