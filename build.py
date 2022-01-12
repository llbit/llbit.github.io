#!/usr/bin/env python3

# Rebuild the code highlight css:
# pygmentize -S github-dark -f html -a .codehilite > assets/highlight.css

from glob import glob
import sys
from markdown import markdown
import codecs
import re
import os

def main():
    posts = []
    for fn in reversed(sorted(glob("_posts/*.md"))):
        print(fn)
        filename_relative = os.path.relpath(fn, '_posts').replace('\\', '/')
        filename_no_ext = os.path.splitext(filename_relative)[0]
        with codecs.open(fn, mode='r', encoding='utf-8') as fin:
            text = fin.read()
            title = text.split('\n', 1)[0]
            title = re.match('#*\\s*(.+)', title).group(1)
            date = re.search('<!-- date=\\{(.*)\\} -->', text)
            lifeview = re.search('<!-- life-viewer -->', text)
            if date:
                date = date.group(1)
            markup = markdown(text, extensions=['extra', 'fenced_code', 'codehilite'])
            posts += [ (filename_no_ext, title, date, markup, lifeview) ]
    with open("index.html", "w") as f:
        links = []
        for fn, title, date, markup, lifeview in posts:
            links += [ f'<li><span class="post-meta">{date}</span><h3><a href="posts/{fn}.html">{title}</a></h3></li>' ]
        markup = "\n".join(links)
        f.write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Low-Level Bits</title>
<link rel="icon" href="/favicon.ico" sizes="16x16" type="image/vnd.microsoft.icon">
<link href="/assets/style.css" rel="stylesheet" type="text/css">
<link href="/assets/highlight.css" rel="stylesheet" type="text/css">
</head>
<a name="top"></a>
<body>
    <header id="header">
        <div class="column">
        <a href="/" id="site-title">Low-Level Bits</a>
        </div>
    </header>
    <div class="column">
        <main>
          <list class="post-list">
          {markup}
          </list>
        </main>
        <footer>Copyright &copy; Jesper Öqvist</footer>
    </div>
  </table>
</body>
</html>""")
    for fn, title, date, markup, lifeview in posts:
        print(fn, date)
        extra = ""
        if lifeview:
            extra = """<meta name="LifeViewer" content="viewer textarea">
    <script src='/assets/js/lv-plugin.js'></script>"""
        with open(f"posts/{fn}.html", "w") as f:
            f.write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="icon" href="/favicon.ico" sizes="16x16" type="image/vnd.microsoft.icon">
<link href="/assets/style.css" rel="stylesheet" type="text/css">
<link href="/assets/highlight.css" rel="stylesheet" type="text/css">
{extra}
</head>
<a name="top"></a>
<body>
    <header id="header">
        <div class="column">
        <a href="/" id="site-title">Low-Level Bits</a>
        </div>
    </header>
    <div class="column">
        <main>
          {markup}
        </main>
        <footer>Posted on {date}<br/>Copyright &copy; Jesper Öqvist</footer>
    </div>
  </table>
</body>
</html>""")

if __name__ == '__main__':
    main()
