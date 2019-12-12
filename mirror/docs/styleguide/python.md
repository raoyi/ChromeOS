# Python Style Guidelines

[TOC]

## Introduction

You should follow this guide for all Python source code that is created as part
of the Chromium OS project i.e. src/platform/\*.  You may not like some bits of
it, but you still need to follow it.  In doing so, you ensure that others can
work with your code.

This guide may be ignored if you are working on code that is part of an open
source project that already conforms to a different style i.e. generally Python
code in src/third\_party.  Autotest is a great example of this - see the [other
notable Python style guides](#Other-notable-Python-style-guides) below.

See also the overall [Chromium coding style].

## Official Style Guide

The [Google Python Style guide] is the official Python style guide for
Chromium OS original code.

New projects should use that unmodified public Python Google style guide
(4 space indent with methods\_with\_underscores). Historically, we adopted a
style that was congruent with Google internal Python style guide (2 spaces with
MethodsAsCamelCase). Individual older projects are in the process of migrating
to the public style as time allows; there is no mandate to migrate.

That is, for new projects, use:

*   [Indentation]: 4 spaces
*   [Naming]: Functions and Method names use lower\_with\_under()

If that guide is silent on an issue, then you should fall back to [PEP-8].

[PEP-257] is referenced by PEP-8.  If it isn't covered in the
[Comments section], you can also fall back to PEP-257.

## Other notable Python style guides

There are a number of other Python style guidelines out there.

*   [The CODING STYLE file for autotest] - When working on autotest code (or
    any autotest tests), you should ignore the Chromium OS style guidelines
    (AKA this page) and use the autotest ones.

## Describing arguments in docstrings

[PEP-257] says that "The docstring for a function or method should summarize
its behavior and document its arguments, return value(s), side effects,
exceptions raised, and restrictions. However, it doesn't specify any details of
what this should look like.

Fortunately, the Google Python style guide provides a [reasonable syntax for
arguments and return values].  We will use that as our standard (adjusted to
two-space indentation):

```python
def FetchBigtableRows(big_table, keys, other_silly_variable=None):
  """Fetches rows from a Bigtable.

  Retrieves rows pertaining to the given keys from the Table instance
  represented by big_table.  Silly things may happen if
  other_silly_variable is not None.

  Args:
    big_table: An open Bigtable Table instance.
    keys: A sequence of strings representing the key of each table row
        to fetch.
    other_silly_variable: Another optional variable, that has a much
        longer name than the other args, and which does nothing.

  Returns:
    A dict mapping keys to the corresponding table row data
    fetched. Each row is represented as a tuple of strings. For
    example:

    {'Serak': ('Rigel VII', 'Preparer'),
     'Zim': ('Irk', 'Invader'),
     'Lrrr': ('Omicron Persei 8', 'Emperor')}

    If a key from the keys argument is missing from the dictionary,
    then that row was not found in the table.

  Raises:
    IOError: An error occurred accessing the bigtable.Table object.
  """
  pass
```

Specifically:

*   **Required**  of all **public methods** to follow this convention.
*   **Encouraged** for all **private methods** to follow this convention. May
    use a one-line sentence describing the function and return value if it's
    simple.
*   All arguments should be described in the `Args:` section, using the format
    above.
    *   Ordering of descriptions should match order of parameters in function.
    *   For two-line descriptions, indent the 2nd line 4 spaces.
*   If present, `Args:`, `Returns:`, and `Raises:` should be the last three
    things in the docstring, separated by a blank line each.

## Imports

The following rules apply to imports (in addition to rules already talked about
in [PEP-8]):

*   It is OK to import packages, modules, and things within a module. This is
    mentioned solely because it contradicts the [section on imports in the
    Google Style Guide] (which, remember, is not an authority for Chromium OS).
    *   Said another way, this is completely OK:
        `from subprocess import Popen, PIPE`
    *   **NOTE**: Although not required, we still may want to encourage people
        to only import packages and modules.
*   Relative imports are forbidden ([PEP-8] only "highly discourages" them).
    Where absolutely needed, the `from __future__ import absolute_import`
    syntax should be used (see [PEP-328]).
*   Do not use `import *`. Always be explicit about what you are importing.
    Using `import *` is useful for interactive Python but shouldn't be used in
    checked-in code.

## The shebang line

All files that are meant to be executed should start with the line:

```python
#!/usr/bin/env python2
```

If your system doesn't support that, it is sufficiently unusual for us to not
worry about compatibility with it.  Most likely it will break in other fun ways.

Files that are not meant to be executed should not contain a shebang line.

## String formatting

The [Google style guide] says that the `'{}'.format()` style is permitted.
That is true, but in CrOS we much more often/always use % instead. You should
stick to using % in CrOS code to match existing codebases.

```python
x = 'name: %s; score: %d' % (name, n)
x = 'name: %(name)s; score: %(score)d' % {'name': name, 'score': n}
```

Also keep in mind that for logging type functions, we don't format in place.
Instead, we pass them as args to the function.

```python
logging.info('name: %s; score: %d', name, n)
```

## Variables in Comprehensions & Generator Expressions

When using comprehensions & generators, it's best if you stick to "throw away"
variable names.  "x" tends to be the most common iterator.

```python
some_var = [x for x in some_list if x]
```

While helping with readability (since these expressions are supposed to be kept
"simple"), it also helps avoid the problem of variable scopes not being as tight
as people expect.

```python
# This throws an exception because the variable is undefined.
print(x)

some_var = [x for x in (1, 2)]
# This displays "1" because |x| is now defined.
print(x)

string = 'some string'
some_var = [string for string in ('a', 'b', 'c')]
# This displays "c" because the earlier |string| value has been clobbered.
print(string)
```

## TODOs

It is OK to leave TODOs in code.  **Why?**  Encouraging people to at least
document parts of code that need to be thought out more (or that are confusing)
is better than leaving this code undocumented.

See also the [Google style guide] here.

All TODOs should be formatted like:

```python
TODO(username): Revisit this code when the frob feature is done.
```

...where `username` is your chromium.org username. If you don't have a
chromium.org username, please use an email address.

Please **do not** use other forms of TODO (like `TBD`, `FIXME`, `XXX`, etc).
This makes TODOs much harder for someone to find in the code.

## pylint

Python code written for Chromium OS should be "pylint clean".

[Pylint] is a utility that analyzes Python code to look for bugs and for style
violations.  We run it in Chromium OS because:

*   It can catch bugs at "compile time" that otherwise wouldn't show up until
    runtime.  This can include typos and also places where you forgot to import
    the required module.
*   It helps to ensure that everyone is following the style guidelines.

Pylint is notoriously picky and sometimes warns about things that are really OK.
Because of this, we:

*   Disable certain warnings in the Chromium OS pylintrc.
*   Don't consider it a problem to locally disable warnings parts of code.
    **NOTE**: There should be a high bar for disabling warnings.
    Specifically, you should first think about whether there's a way to rewrite
    the code to avoid the warning before disabling it.

You can use `cros lint` so that we can be sure everyone is on the same version.
This should work outside and inside the chroot.

## Other Considerations

### Unit tests

All Python modules should have a corresponding unit test module called
`<original name>_unittest.py` in the same directory.  We use a few related
modules (they're available in the chroot as well):

*   [mock] (`import mock`) for testing mocks
    *   It has become the official Python mock library starting in 3.3
    *   [pymox] (`import mox`) is the old mock framework

*   You'll still see code using this as not all have been migrated to mock yet

*   [unittest] (`import unittest`) for unit test suites and methods for testing

### Main Modules {#main}

*   All main modules require a `main` method.  Use this boilerplate at the end:
    ```python
    if __name__ == '__main__':
      sys.exit(main(sys.argv[1:]))
    ```
    *   Having `main` accept the arguments instead of going through the implicit
        global `sys.argv` state allows for better reuse & unittesting: other
        modules are able to import your module and then invoke it with
        `main(['foo', 'bar'])`.
    *   The `sys.exit` allows `main` to return values which makes it easy to
        unittest, and easier to reason about behavior in general: you can always
        use `return` and not worry if you're in a func that expects a `sys.exit`
        call.  If your func doesn't explicitly return, then you still get the
        default behavior of `sys.exit(0)`.
    *   If you want a stable string for prefixing output, you shouldn't rely on
        `sys.argv[0]` at all as the caller can set that to whatever it wants (it
        is never guaranteed to be the basename of your script).  You should set
        a constant in your module, or you should base it off the filename.
        ```python
        # A constant string that is guaranteed to never change.
        _NAME = 'foo'
        # The filename which should be stable (respects symlink names).
        _NAME = os.path.basename(__file__)
        # The filename which derefs symlinks.
        _NAME = os.path.basename(os.path.realpath(__file__))
        ```
    *   If your main func wants `argv[0]`, you should use `sys.argv[0]`
        directly. If you're trying to print an error message, then usually you
        want to use `argparse` (see below) and the `parser.error()` helper
        instead.

*   Main modules should have a symlink without an extension that point to the
    .py file.  All actual code should be in .py files.

### Other

*   There should be one blank line between conditional blocks.
*   Do not use `GFlags` or `optparse` anymore -- stick to `argparse` everywhere.

[Chromium coding style]: https://chromium.googlesource.com/chromium/src/+/master/styleguide/styleguide.md
[Google Python Style guide]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md
[Indentation]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#s3.4-indentation
[Naming]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#316-naming
[PEP-8]: https://www.python.org/dev/peps/pep-0008/
[Comments section]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
[The CODING STYLE file for autotest]: https://chromium.googlesource.com/chromiumos/third_party/autotest/+/master/docs/coding-style.md
[reasonable syntax for arguments and return values]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
[section on imports in the Google Style Guide]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#313-imports-formatting
[PEP-8]: https://www.python.org/dev/peps/pep-0008/
[PEP-257]: https://www.python.org/dev/peps/pep-0257/
[PEP-328]: https://www.python.org/dev/peps/pep-0328/
[Google style guide]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#310-strings
[Google style guide]: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#312-todo-comments
[mock]: https://docs.python.org/3/library/unittest.mock.html
[pymox]: https://code.google.com/p/pymox/wiki/MoxDocumentation
[unittest]: https://docs.python.org/library/unittest.html
[Pylint]: https://github.com/PyCQA/pylint
