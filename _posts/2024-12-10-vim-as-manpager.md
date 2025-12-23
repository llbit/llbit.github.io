# Vim as Manpager
<!-- date={2024-12-10} -->

Here is a tip for fellow Vim/Neovim users: it is possible to use Vim as a man page viewer by adding the following to your `.bashrc`/`.zshrc`/etc.

```bash
export MANPAGER="vim +MANPAGER --not-a-term -"
```

to use Neovim instead add this:

```bash
export MANPAGER="nvim +Man!"
```

I have been using this tip for a while now and it is awesome because links in the man pages can be followed using the usual Vim shortcut `Ctrl+]`.
