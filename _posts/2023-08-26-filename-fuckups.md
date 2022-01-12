# Filename Fuck-ups
<!-- date={2023-08-26} -->

I recently made a git branch with the slightly creative branch name
`((x.y).z).w` and pushed it to my team's GitLab server.  Normally the branches
on the server are named with only underscore or dash to separate parts of the
branch name, e.g., `refactor-compiler`.  I was testing how creative I could be
with branch names and found out that `>` was allowed.  So I also made a branch
named `globals->initfunctions` and pushed that one too.  This soon lead to all
our GitLab continuous integration builds failing on Windows for all branches.

The failing Windows builds had the following in their logs:

```
Fetching changes...
Initialized empty Git repository in C:/GitLab-Runner/builds/SZUExwvh/0/nextgen/language/.git/
Created fresh repository.
error: cannot lock ref 'refs/remotes/origin/global->initfunctions': Unable to create 'C:/GitLab-Runner/builds/SZUExwvh/0/nextgen/language/.git/refs/remotes/origin/global->initfunctions.lock': Invalid argument
```

Even if a build job was not trying to check out the `global->initfunctions`
branch, it still apparently needed to create a `.lock` file for the branch in the git
checkout, but this failed because `>` cannot be part of a filename on Windows.

This git problem reminded me of one time when a student in a course I was TA in
had a problem building a lab project on his laptop.  The lab project was built
using Gradle and it had worked seamlessly for hundreds of students before then,
but this student got seemingly unexplainable Java compilation errors in his
unmodified base version of the lab project.

It turned out that the problem was that his project resided in a
directory that contained a colon in its name.  The `:` character is used for
separating entries on the Java classpath so when Gradle tried to build his
project it had some extra `:` in the classpath that referenced Jar files inside his
project folder and the build then failed because the paths got split up
incorrectly.
