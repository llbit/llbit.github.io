# Comparing Collections
<!-- date={2014-03-14} -->

In a project I'm currently working on I had to compare two [Java
Collections][1] to see if they contained the same elements, ignoring element
order. The usual place for such general Collection-related library functions is
[java.util.Collections][2] however a fitting method was not found there.

## Apache Commons Algorithm

[An answer on Stack Overflow][3] pointed me to a method in an Apache Commons
library which did exactly what I wanted. The method is called
`isEqualCollection` and the implementation I looked at can be found in Apache
Commons Collections 4.0. The Apache library uses this algorithm to compare two
collections A and B:

1. Test that both A and B have equal size. If the sizes differ then A is not
   equal to B and we are done.
2. Build a frequency table for collection A.
3. Build a frequency table for collection B.
4. Test that both frequency tables have the same number of rows, if not then A
   is not equal to B and we are done.
5. For each element in the frequency table of A, check that the element has the
   same frequency as in B (by lookup in the frequency table of B).

## Improved Algorithm

I saw some improvements that could be made on the Apache Commons algorithm above.

The frequency tables give the number of times an element x occurs in each
collection. We can improve the memory usage of the algorithm by using a single
frequency table rather than two. Let `fA(x)` be the number of occurrences of x
in A, and let `fB(x)` be the number of occurrences of x in B. We only need to
compute the difference `d(x) = fA(x)-fB(x)`. If there is any x for which `d(x)`
is not zero, then x occurs more times in A (`d(x) > 0`) or B (`d(x) < 0`). The
modified algorithm stores `d(x)` in a frequency table which is initialized by
counting occurrences of elements in A, as in step 2 above, then for each
element in B we subtract one from the frequency count of the element.

Using a single frequency table still requires iteration over both collections
in order to populate the frequency table correctly, but we now have an easy way
to add a fail-fast condition while iterating over elements in B. If we notice
that the frequency of any element drops below zero then we know that the
element occurs more often in B. This new condition may improve the average
running time, but it does not affect the asymptotic worst-case running time.

An improvement in the worst-case running time is gained by completely removing
the final loop. It is not immediately obvious that it is possible to remove the
final loop, but I wrote a [sketch of a correctness proof in the README for my
code on GitHub][4].  The idea is that the extra check during iteration over B
while updating the frequency table together with the first check testing that
both collections have the same size is sufficient to ensure that A is equal to
B.

Let's review the improved algorithm:

1. Test that both A and B have equal size, if the sizes differ then A is not
   equal to B and we are done.
2. Build a frequency table for collection A.
3. For each element x in B:
    * Subtract one from row x in the frequency table.
    * If the frequency of x is now negative then A is not equal to B.
4. If the algorithm did not already terminate, then A and B are equal.

## Implementation

Below is my implementation of the improved algorithm. Note that I use a
`HashMap` to implement the frequency table, it may be replaced by an
[`IdentityHashMap`][5] if you wish to use [reference equality rather than
object equality][6] as the element equality condition.

```java
boolean isEqualCollection(Collection<?> a, Collection<?> b) {
    if (a.size() != b.size()) {
        return false;
    }
    Map<Object, Integer> map = new HashMap<>();
    for (Object o : a) {
        Integer val = map.get(o);
        int count;
        if (val != null) {
            count = val.intValue();
        } else {
            count = 0;
        }
        map.put(o, Integer.valueOf(count + 1));
    }
    for (Object o : b) {
        Integer val = map.get(o);
        int count;
        if (val != null) {
            count = val.intValue();
            if (count == 0) {
                return false;
            }
        } else {
            return false;
        }
        map.put(o, Integer.valueOf(count - 1));
    }
    return true;
}
```

In conclusion, the above implementation is more efficient than the Apache
Commons implementation because it uses less memory (by using only one
`HashMap`, rather than two), and avoids the final loop of the Apache algorithm.
My algorithm can also return `false` faster than the Apache algorithm.

## Revisions

* Update (2016): I published a Git repository with my algorithm and tests [on GitHub][7].
* Update (2016, #2): I revised my original algorithm: I found that it was
possible to remove the check of the frequency table after iterating over the B
collection. The algorithm description here has been updated. See the
correctness proof sketch in the README of the Git repository for details.
* Update (2022): Removed redundant type arguments to `HashMap`.

[1]: http://docs.oracle.com/javase/7/docs/api/java/util/Collection.html
[2]: http://docs.oracle.com/javase/7/docs/api/java/util/Collections.html
[3]: http://stackoverflow.com/a/1167234/1250278
[4]: https://github.com/llbit/collection-comparison#correctness-proof-sketch
[5]: http://en.wikibooks.org/wiki/Java_Programming/Comparing_Objects
[6]: http://en.wikibooks.org/wiki/Java_Programming/Comparing_Objects
[7]: https://github.com/llbit/collection-comparison
