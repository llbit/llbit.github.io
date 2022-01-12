# Git Metrics Tool
<!-- date={2018-12-19} -->

I wrote a small Python program to extract Git commit metrics for a table in my thesis. There
were some alternative tools available, but none of them gave exactly the output I was looking for.
Instead of converting the output from another tool it seemed easy enough to roll my own solution,
so here it is: [git-commit-metrics](https://github.com/llbit/git-commit-metrics).

My program generates TeX tables like the following one:

![Number of commits and lines changed per author for a git repository.](/assets/extendj-statistics.png)

The above table was generated for the [ExtendJ compiler repository](https://bitbucket.org/extendj/extendj/src).

