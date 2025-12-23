# Julia is not LR(1)
<!-- date={2022-01-27} -->

The [Julia programming language][julia] has a very minimalistic grammar, avoiding
many keywords or syntax elements that are common in other languages such as
braces and semicolons.  For example, here is a small piece of Julia code:

```jl
function hello(x)
  if x
    print(x)
  end
end
```

At a glance, Julia code looks similar to [Python][python]. The most notable differences
are that that Julia requires `end` after each block of code and does not have
colons after the function header or if-statement condition. Although properly indented
code will look very similar to Python code, the Julia parser does not care about indentation.

Semicolons and braces are used in many programming languages to resolve
otherwise ambiguous syntax.  For example, if semicolons are optional after
statements, an expression like `x = f(a) + 1`
could be parsed as either one statement `x = (f(a) + 1)` or two statements
`x = f; (a) + 1`. To make expressions like these unambiguous, the Julia language is
whitespace-sensitive and has some disambiguation rules that depend on the whitespace.
For example, a function call cannot have whitespace between the function name
and the parameter list.

I recently attempted to write an LR(1) grammar for the Julia language, to see
if it would be possible.  It turned out to not be possible due to the
whitespace sensitivity in Julia. Here is a small essential subset of my Julia
grammar which is unambiguous and context-free but not LR(1):

```
program = es
es = e | es w e
e  = n | n w EQ e
n = ID
w = WHITESPACE
```

The `es` production represents an expression list, which is separated by
whitespace(s).  An expression `e` can either be a name `n` or an
assignment `n w EQ e`.  There can be whitespace `w` preceding
the assignment operator `EQ`.  There can also be whitespace after `EQ`
but I omit it here for simplicity's sake.  This grammar is
not LR(1) because when the parser encounters an `ID` token with a `WHITESPACE` token
in the lookahead it can either reduce the `ID` to an expression or shift it
to build an assignment later. Since an LR(1) parser must decide which action to take
based only on the `WHITESPACE` in the lookahead, it cannot unambiguously choose the
correct action as always choosing to shift or reduce will make some Julia expressions
parse incorrectly.

The LR(1) ambiguities in Julia prevent the use of an LR(1) or LALR(1) parser generator.
However, I have used a [GLR parser generator][GLR] with my Julia
grammar and this seems to work so far. Unfortunately it is very
hard to know if the grammar is ambiguous when using GLR, you pretty much just
have to parse a bunch of programs and test for multiple valid parse trees. I
have successively refined my grammar after finding such ambiguities to arrive
at a grammar that appears unambiguous with my current test set.  Another way
of determining if the grammar is unambiguous is to carefully look at all the
LR(1) conflicts in the grammar and convincing yourself that they will be
resolved by a GLR parse. This seems infeasible for my grammar as there are
currently 51 shift/reduce conflicts and 34 reduce/reduce conflicts.

[julia]: https://julialang.org/
[GLR]: https://en.wikipedia.org/wiki/GLR_parser
[python]: https://www.python.org/
