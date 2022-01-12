# Git push confirmations for protected branches with a pre-push hook
<!-- date={2024-09-19} -->

Pre-push hooks can be used to do various checks on your local Git work before
pushing to ensure that you are not unintentionally pushing incomplete commits
to a shared or public repository. For example, Git includes a sample pre-push
hook that checks for commits containing `WIP` in the message. You can normally
find it in `.git/hooks/pre-push.sample` in your repository.

I recently accidentally pushed to a `master` branch in a work repository which
I had not intended to and decided to make a pre-push hook to confirm this for
the future:

```bash
#!/bin/bash

protected_branch='master'
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

if [ $protected_branch = $current_branch ]
then
    read -p "You're about to push ${protected_branch}, is that what you intended? [y|n] " -n 1 -r < /dev/tty
    echo
    echo $REPLY | grep -E '^[Yy]$' > /dev/null
    exit $?
else
    exit 0 # push will execute
fi
```

This Bash script needs to be placed in a file named `repo/.git/hooks/pre-push`.
The file must be executable (`chmod u+x pre-push`).  This script isn't perfect:
it will warn if you try to delete a remote branch, for example `git push -d
origin branch-to-delete`. Although this is a push that is not affecting the
current branch but if your current working branch is the protected branch then
you will get the confirmation anyway.

If your repository is in a submodule of another Git repository the location of
the pre-push hook is different.  Say your main repository is `repo` and the
name of the submodule the hook should work in is `sub` then the pre-push hook
should be at `repo/.git/modules/sub/hooks/pre-push`.
