---
layout: post
title: "Vim as Manpager"
date: 2024-12-10 08:00:00 +0100
categories: linux
---
Here is a tip for fellow Vim/Neovim users: it is possible to use Vim as a man page viewer by adding the following to your `.bashrc`/`.zshrc`/etc.

{% highlight bash %}
export MANPAGER="vim +MANPAGER --not-a-term -"
{% endhighlight %}

to use Neovim instead add this:

{% highlight bash %}
export MANPAGER="nvim +Man!"
{% endhighlight %}

I have been using this tip for a while now and it is awesome because links in the man pages can be followed using the usual Vim shortcut `Ctrl+]`.
