---
layout: post
title: "Julia is not LR(1)"
date: 2022-01-27 17:00:00 +0100
categories: programming
---
The [Julia programm language][julia] has a very minimalistic grammar, avoiding
many keywords or syntax elements that are common in other languages such as
braces and semicolons.  For example, here is a small piece of Julia code:

{% highlight julia %}
function hello(x)
  if x
    (x) = x
    print(x)
  end
end
{% endhighlight %}

At a glance, Julia code looks similar to Python. The most notable differences
are that that Julia requires `end` after each block of code and does not require
colons after the function header or if-statement condition. Although properly indented
code will look very similar to Python code, the Julia parser does not care about indentation.

Semicolons and braces are used in many programming languages to resolve
otherwise ambiguous syntax.  For example, an expression like `x = f(a) + 1`
could be parsed as either one statement `x = (f(a) + 1)` or two statements
`x = f; (a) + 1`. To make statements like this unambiguous, the Julia language is
whitespace-sensitive and has some disambiguation rules that depend on the whitespace.
For example, a function call cannot have whitespace between the function name
and the parameter list.

I recently attempted to write an LR(1) grammar for the Julia language, to see
if it would be possible.  It turned out to not be possible due to the
whitespace sensitivity in Julia. Here is a small subset of my attempted Julia
grammar which I believe is not LR(1):

```
program = es
es = e | es w e
e  = n | n w EQ e
n = ID
w = WHITESPACE
```

The `es` production represents an expression list, which is separated by
whitespace(s).  An expression `e` can either be a name `n` or an
assignment `n w EQ e`.  There can be whitespace between the left-hand-side of
the assignment and the equals operator.  There can also be whitespace after the
equals operator `EQ` but I omit it here for simplicity's sake.  This grammar is
not LR(1) because when the parser encounters an `ID` token with a `WHITESPACE` token
in the lookahead it can either reduce the `ID` to an expression or shift it
to build an assignment later. Since an LR(1) parser must decide which action to take
based only on the `WHITESPACE` in the lookahead, it cannot unambiguously choose the
correct action as always choosing to shift or reduce will make some Julia expressions
parse incorrectly.

[julia]: https://julialang.org/
