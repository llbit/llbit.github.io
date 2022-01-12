# Useful C Macros
<!-- date={2025-12-18} -->

I generally try to avoid reaching for macros when I program in C because using them inappropriately
can lead to unreadable code which does seemingly unpredictable things and is painful to debug
(e.g., stepping through macros in a debugger).
That being said, there are some macros that
can really help make it much nicer to work in C by minimizing a lot of
tedious boiler-plate style code.
Here I will show some of my favorite C macros for various tasks
like iterating over data structures and printing error messages.

## Circular List Iteration
Say that we have a circular linked list structure defined like this:

```c
typedef struct List List;
struct List {
  List* next;
  void* data;
};
```

Here is a macro to iterate over the elements of such a list:

```c
#define FOR_EACH(p, list) for (        \
    List* p = NULL, *next__##p = list; \
    p != list && (p = next__##p);      \
    p = next__##p = p->next)
```

The macro is used like this, for example:

```c
FOR_EACH(p, my_list) {
  process_data(p->data);
}
```

## Locking/Unlocking Mutexes
This macro helps creating critical sections by taking and holding a lock while the statements inside the block following the macro call are executed:

```c
#define WITH_LOCK(lock) for(int xk=1; xk && !pthread_mutex_lock(&lock); \
    (pthread_mutex_unlock(&lock)), xk=0)
```

For example:

```c
pthread_mutex_t sched_lock = PTHREAD_MUTEX_INITIALIZER;

// ...

  WITH_LOCK(sched_lock) {
    vm_Task* task = task_from_ref(taskref);
    if (task && task->state != TASK_STATE_FINISHED) {
      state.ffi_result = TASK_BLOCKED;
      task_wait_on(vm_current_task(), task);
    }
  }
```

Note that the macro relies on normal control flow exiting the block, so that the for-loop increment
statement can unlock the mutex.
In other words, you cannot use `return`, `break`, or `continue` inside the block.

```c
  WITH_LOCK(sched_lock) {
    break; // DANGER! mutex is left locked
  }
```

## Error Reporting
Since C99 it is possible to use variable argument macros. This can be combined with a helper function to
include extra information in error messages. Below is a simplified example of how this might be used,
adding the function name in the error message.

```c
#include <stdarg.h>

#define FFI_ERROR(...) ffi_error(__func__, __VA_ARGS__)

__attribute__((format(printf,2,3)))
static void ffi_error(const char* func, const char* format, ...)
{
  va_list argp;
  va_start(argp, format);
  printf("%s: ", func);
  vprintf(format, argp);
  va_end(argp);
}
```

The macro is used like this:

```c
void copy_to_buffer(int len, void* data)
{
  if ((size_t) len + 1 > sizeof(strbuf)) {
    FFI_ERROR("length %d is too large for temporary buffer\n", len);
  }
}
```

The `__func__` macro expands to the function name where the macro is used, so the error message
looks like this:

```
copy_to_buffer: length 123 is too large for temporary buffer
```

The `__attribute__` above the function declaration is optional and just helps in checking
for `printf` argument errors.

## Hash Table Iteration
In one project I am working on I wrote the following macro for iterating over a hash table:

```c
/** An iterator for a hash table. */
typedef struct {
  uint32_t i;       // Current bucket index.
  const char* key;  // Current bucket key.
  void* value;      // Current bucket value.
} tbl_Iter;

#define TBL_ITERATE(it, tbl) for (                  \
    tbl_Iter it = { .i = 0 };                       \
    it.i < (tbl)->capacity && (it = (tbl_Iter) {    \
      .i = it.i,                                    \
      .key = (tbl)->buckets[it.i].key,              \
      .value = (tbl)->buckets[it.i].value }, true); \
    it.i += 1) if (!(tbl)->buckets[it.i].flag)
```

This is very specific to one hash table implementation so it might not be easy to adapt to other
hash tables, but here is how I would use it in the project where it lives:

```c
  HashTable* tbl = new_hashtable();
  tbl_insert(tbl, "name", ast_call(...));
  TBL_ITERATE(it, tbl) {
    const char* name = (const char*) it.key;
    AstNode* node = (AstNode*) it.value;
  }
```

## Addendum: clang-format
If you use the for-each style macros like the ones above (`FOR_EACH` or `TBL_ITERATE`), you can add the `ForEachMacros` option to your `.clang-format` so that you get formatting to look better for these macros:

```
ForEachMacros: ['FOR_EACH', 'TBL_ITERATE']
```
