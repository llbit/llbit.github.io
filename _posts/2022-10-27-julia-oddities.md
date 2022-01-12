# Julia Oddities
<!-- date={2022-10-27} -->

[The Julia language][julia] is in general very well-designed. However, no
programming language is perfect and there are some rough edges or unexpected
behaviors even in Julia.

In this post I document some of the interesting, quirky, or unexpected
behaviors I have noticed in Julia.  Some of these are well-known and others are
obscure. I will occasionally update this post as I find more interesting
things to mention.

## String Concatenation

Probably the most common Julia oddity is that `+` does not concatenate strings
as is common in many other languages that have a string concatenation operator.

In Julia the standard string concatenation operator is `*`. The Julia
developers are aware that this is an unintuitive choice so they even note this
and [explain their reasoning in the Julia documentation][julia-strcat].
Essentially the argument for not using `+` like most other programming
languages is that `+` in mathematics usually denotes a commutative
operation but string concatenation does not commute.

There are more than one way to concatenate a string, however. One can also
use the standard `string()` function like so: `string("a", "b", "c")`.

If you still want to use `+` to concatenate strings you can overload the
`+` operator:

```jl
+(s1::AbstractString, ss::AbstractString...) = string(s1, ss...)
"much" + " better"
```

## Default Arguments

Julia allows an argument to have a default value, but the type of the default
value is not statically checked. Therefore it is possible to declare a default
argument value that does not match the type of the argument, for example:

```jl
foo(::Int = "3.1415") = println("foo(::Int)")
foo()
```

Here, the call to `foo()` results in the default argument expression `"3.1415"`
being evaluated and passed to `foo(::Int)` but that does not work as the
expression does not match the argument type. Instead, we get the error
`MethodError: no method matching foo(::String)`.

Even more confusingly, if we add another function with the same name that accepts a `String`
argument then that other function is called instead of our original function.

```jl
foo(::String)         = println("foo(::String)")
foo(::Int = "3.1415") = println("foo(::Int)")

foo()
foo(101)
```

This code outputs:

```
foo(::String)
foo(::Int)
```

This has been a
[known problem in Julia for a while](https://github.com/JuliaLang/julia/issues/7357).

## Where-clause Parsing

If you are familiar with polymorphic functions in Julia, you might expect the following
functions to be equivalent:

```jl
f(x::T)::Int64 where T = 1

function f(x::T)::Int64 where T
  return 1
end
```

The first version of `f()` is written in assignment form, which is usually equivalent to
the longer non-assignment form function-declaration style.
In this case however, the Julia compiler gives the following error for the assignment form:

```
julia> f(x::T)::Int64 where T = 1
ERROR: UndefVarError: T not defined
```

The problem here is that the function is parsed as if it was written `f(x::T)::(Int where T) = 1`
and therefore `T` is not actually part of the function's `where`-clause.
This is a [known issue in the Julia parser](https://github.com/JuliaLang/julia/issues/21847)
with no clear solution.

## Negative Bit Shifts

The `<<` and `>>` operators are sometimes misunderstood. I think the original intention of these operators in C was just to shift the
bits around in integer numbers, but the behavior is not fully specified for all possible combinations of signed/unsigned operands (so-called undefined behavior).

Without going into great detail it can be noted that the right-hand operand is usually not allowed to be
negative. For example modern C compilers warn against negative shifts and Python disallows it completely.
However, Julia **does** allow negative right-hand operands. An expression `X << -10` is equivalent to `X >> 10` and `Y >> -4` is equivalent to `Y << 4` in Julia.
This seems pretty logical to me and it is a nice little consistency fix when using the `<<` or `>>` operators to multiply or divide by powers of two.

## UnitRange Normalization

The first time I typed `10:1` in the Julia REPL I was surprised at the output:

```
julia> 10:1
10:9
```

The `10:1` syntax creates a `UnitRange` object and in the constructor it will
normalize the range so that an empty range has `stop - start + 1 == 0`. This
leads to the above range being constructed with `stop == 9` instead of `1`.
This makes sense but it was also a little bit confusing when I first noticed
this behaviour and didn't understand why it was happening.

## Relative Module Paths

An import/using statement can use a relative module path which normally
would look like `using ..Thing`. However, this is also perfectly fine:

```
using .................Base.Base.Base.Base
```

The [Julia documentation](https://docs.julialang.org/en/v1/manual/modules/#Submodules-and-relative-paths) states:

> A relative module qualifier starts with a period (.), which corresponds to the current module, and each successive . leads to the parent of the current module.

A relative module path does not go past the topmost module, so additional
periods are just ignored. Additionally, the name `Base` inside the `Base`
module refers to itself so the `Base.Base.Base.Base` part is equivalent to just
`Base`.

Here is another strange example that works in Julia 1.9.2:

```
Main.Main=(..)=Main.Main
import ...Main....Main...
```


[julia-strcat]: https://docs.julialang.org/en/v1/manual/strings/#man-concatenation
[julia]: https://julialang.org/
