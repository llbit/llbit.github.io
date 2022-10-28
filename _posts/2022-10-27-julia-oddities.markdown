---
layout: post
title: "Julia Oddities"
date: 2022-10-27 17:00:00 +0100
categories: programming, julia
---
[The Julia language][julia] is overall well-designed, but
I have found some rough edges where the language did not work as I had expected.
Here I will describe the two most interesting unexpected behaviors I've seen thus far in Julia.

## Default Arguments

Julia allows an argument to have a default value, but the type of the default
value is not statically checked. Therefore it is possible to declare a default
argument value that does not match the type of the argument, for example:

{% highlight julia %}
foo(::Int = "3.1415") = println("foo(::Int)")
foo()
{% endhighlight %}

Here, the call to `foo()` results in the default argument expression `"3.1415"`
being evaluated and passed to `foo(::Int)` but that does not work as the
expression does not match the argument type. Instead, we get the error
`MethodError: no method matching foo(::String)`.

Even more confusingly, if we add another function with the same name that accepts a `String` as
type then that other function is called instead of our original function.

{% highlight julia %}
foo(::String)         = println("foo(::String)")
foo(::Int = "3.1415") = println("foo(::Int)")

foo()
foo(101)
{% endhighlight %}

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

{% highlight julia %}
f(x::T)::Int64 where T = 1

function f(x::T)::Int64 where T
  return 1
end
{% endhighlight %}

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


[julia]: https://julialang.org/
