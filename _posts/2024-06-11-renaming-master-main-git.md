# Renaming Master/Main in Git
<!-- date={2024-06-11} -->

TL;DR: Add an alias for the current branch with this Bash one-liner:

```bash
git symbolic-ref refs/heads/m refs/heads/$(git rev-parse --abbrev-ref HEAD)
```

Git, and many source code hosting websites like GitHub and GitLab, decided
to change the default branch name from `master` to `main` a few years ago. So
new repositories have `main` as the mainline branch name and older repositories
instead use `master` for the most part.

Although I slightly prefer `main` for the simple reason that it's marginally
simpler to type than `master`, I find this revisionist trend of constantly
renaming stuff in software highly annoying. This is a common occurrence in
programming APIs and tools where the developers suddenly decide that `destDir`
is not descriptive and must be changed to `destinationDirectory`, forcing all
users of the software to adapt if they want to use the new version.

The Gradle build system is an example of this. Gradle has done several pedantic
and overly descriptive renaming changes which have forced me to do trivial and
from my perspective entirely pointless changes in my build scripts.

I wonder how many years of developer productivity have been wasted on the sum
of all those moments of inconvenience and confusion caused by pointless renames
in software that we all use.

Anyway back to Git, I recently found a very nice solution to my annoyance with
having different names for the main branch in different repositories.
Apparently [Git allows us to make symbolic
references](https://git-scm.com/docs/git-symbolic-ref) from one branch name to
another, so my solution is to just make a symbolic reference `m` pointing to
either `main` or `master` depending on the repository. This is done with the
following command:

```bash
git symbolic-ref refs/heads/m refs/heads/main
```

Replace `main` by whatever branch you want to make an alias for.  Alternatively, the
following command adds an alias for the _current branch_

```bash
git symbolic-ref refs/heads/m refs/heads/$(git rev-parse --abbrev-ref HEAD)
```

I can do
this once for every repository I am working on and thereafter I can always use
my own standardized main branch name `m` which is shorter and easier to type
than both `main` and `master`.

For example

```bash
git checkout feature-branch
git diff m
git merge m
git checkout m
```

The one caveat to this is that the default merge commit message will mention
the branch name `m` although you might want to use the actual branch name.

As a side note I highly recommend creating aliases for your most used git
commands. For example

```bash
git config --global alias.co checkout
git config --global alias.d diff
```

I even have a Bash alias `g` for `git` so that I can type `g co m` instead
of `git checkout master`.
