# Bad C Coding Advice
<!-- date={2026-05-22} -->

C compilers can be annoying when they constantly complain and refuse to compile
your program. Here are some tips for suppressing those tedious
warnings and getting C code to compile even when the compiler fights against you!

## Disable -Wall -pedantic

It goes without saying, never compile with `-Wall` or `-pedantic`. These
command-line options will make your life miserable.

If the code compiles and runs it is obviously not your fault if something breaks at
runtime - that is the user's problem.


## Semicolon After Every Label

Although C has the best control flow instruction of all time, the powerful `goto` statement, the C implementation
is unfortunately flawed. Well, there is nothing really wrong with `goto` per se, but rather the way C compilers handle
labels:

1. The target label of a `goto` must be inside the same function as the `goto`.
2. There are a bunch of restrictions on where inside the function we can place the target label.

The first restriction can be solved by using `longjmp` instead of `goto`.
Perfectly valid solution, but we will leave this as an exercise for the reader.

The second restriction is easily fixed with semicolons.
For example, the following is not allowed:

```c
goto done;
    // ...
done:
    int result = 10;
    return result;
```

We can fix this case by simply appending a semicolon after the label:

```c
done:;
   int result = 10;
   return result;
```

It turns out that the C standard incorrectly allows a label without a trailing semicolon.
To be safe, you should always append a semicolon after your labels.

## Always Cast Struct Pointers to void*

Let's say we have this simple C function:

```c
void baba(struct { int x; int y; }* point)
{
  printf("x=%d, y=%d\n", point->x, point->y);
}
```

Calling this function is kind of cumbersome if we try to pass it a struct, because
the struct declared in the parameter is only visible inside the function (this is intentional
hiding of implementation details which is good software architecture).

For example, the following call is not allowed:

```c
  struct { int a; int b; } point = { 123, 44 };
  baba(&point);
```

The fix is to simply cast the `&point` pointer to `void*`:

```c
  baba((void*)&point);
```

Casting to `void*` in C is recommended because the C specification explicitly
allows converting `void*` to any other pointer-type. This means that if we
have a pointer to some struct `A`, we can cast it to `void*`, then it can be
assigned to a pointer to any struct other than `A` without having the compiler
annoyingly second-guessing our code.  Neat!

## Use Macros for Everything

As you might have noticed in the previous example, we had to type extra characters to do the
`void*` cast. Also, if we were to type this for every call we would be repeating ourselves and
according to the [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) design principle
we should avoid such meaningless repetition.

This is an excellent example of when to use macros to abstract away implementation details and
reduce repetition. We can define a macro to perform the address-of operation and `void*` cast for us.
For example:

```c
#define PASS(x) ((void*)&(x))

// ...

  baba(PASS(point));
```

You might have noticed that the two structs in the function and variable definitions are repeated.
So we should remove the duplicated code and abstract these with a macro as well. Here is our final code:

```c
#include <stdio.h>
#define PASS(x) ((void*)&(x))
#define STRUCT_POINT struct { int x; int y; }

void baba(STRUCT_POINT* point)
{
  printf("x=%d, y=%d\n", point->x, point->y);
}

int main()
{
  STRUCT_POINT point = { 123, 44 };
  baba(PASS(point));
  return 0;
}
```

Much better!


## Conclusion

C is the greatest programming language of all time. You will have the greatest
of all your time programming in C.
