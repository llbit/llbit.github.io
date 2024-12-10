---
layout: post
title: "Reversing Conway's Game of Life"
date: 2024-10-03 19:00:00 +0100
categories: programming, julia
life_viewer: true
---
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

{% highlight julia %}
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
{% endhighlight %}

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

Update: [here is my C implementation.](https://gist.github.com/llbit/c3d9604383696aefcfdd84f7487e7783)
