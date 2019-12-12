# Chromium OS docs

This directory contains public [Chromium OS] project documentation that is
automatically [rendered by Gitiles]. The docs are written in [Gitiles-flavored
Markdown].

## General guidelines

See the [Chromium documentation guidelines] and [Chromium documentation best
practices].

## Style guide

Markdown documents must follow the [style guide].

## Making changes

This repository is managed by the [repo] tool, so you can make changes to it
using the same techniques that you'd use for any other repositories in the
project.

See the [Contributing] guide for more details.

## Making changes without repo

You can also make changes to this repository without using the [repo] tool. This
comes in handy when you don't have a Chromium OS checkout:

```
git clone https://chromium.googlesource.com/chromiumos/docs
cd docs
curl -Lo .git/hooks/commit-msg https://gerrit-review.googlesource.com/tools/hooks/commit-msg
chmod +x .git/hooks/commit-msg
git checkout -b changes
(make some changes)
git commit -a
git push origin HEAD:refs/for/master
```

The above steps will upload a patch to [chromium-review.googlesource.com] where
you can get your patch reviewed, and submit.

## Previewing changes

You can preview your local changes using `scripts/preview_docs` which utilizes
[Gerrit sandbox branches]:

```bash
scripts/preview_docs README.md
```

You can also use [md_browser], which is entirely local and does not require
refs/sandbox/ push permission, but has somewhat inaccurate rendering:

```bash
# at top of Chromium OS checkout
./src/chromium/src/tools/md_browser/md_browser.py -d docs
```

Then browse to e.g.
[http://localhost:8080/README.md](http://localhost:8080/README.md).

To review someone else's changes, apply them locally first, or just click the
`gitiles` link near the top of a Gerrit file diff page.

[Chromium OS]: https://www.chromium.org/chromium-os
[Contributing]: contributing.md
[rendered by Gitiles]: https://chromium.googlesource.com/chromiumos/docs/+/master/
[Gerrit sandbox branches]: contributing.md#sandbox
[Gitiles-flavored Markdown]: https://gerrit.googlesource.com/gitiles/+/master/Documentation/markdown.md
[Chromium documentation guidelines]: https://chromium.googlesource.com/chromium/src/+/master/docs/documentation_guidelines.md
[Chromium documentation best practices]: https://chromium.googlesource.com/chromium/src/+/master/docs/documentation_best_practices.md
[style guide]: https://github.com/google/styleguide/tree/gh-pages/docguide
[repo]: https://source.android.com/source/using-repo
[chromium-review.googlesource.com]: https://chromium-review.googlesource.com/
[md_browser]: https://chromium.googlesource.com/chromium/src/tools/md_browser/+/master/
