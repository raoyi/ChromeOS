#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Print syscall table as markdown."""

from __future__ import print_function

import argparse
import collections
import os
import re
import subprocess
import sys

import constants


# The C library header to find symbols.
HEADER = 'syscall.h'

# The markdown file where we store this table.
MARKDOWN = 'syscalls.md'

# The string we use to start the table header.
START_OF_TABLE = '## Tables'

# We order things based on expected usage.
ORDER = collections.OrderedDict((
    ('x86_64', 'x86_64 (64-bit)'),
    ('arm', 'arm (32-bit/EABI)'),
    ('aarch64', 'arm64 (64-bit)'),
    ('i686', 'x86 (32-bit)'),
))

# Which register is used for the syscall NR.
REGS = {
    'arm': {'nr': 'r7', 'args': ['r0', 'r1', 'r2', 'r3', 'r4', 'r5']},
    'aarch64': {'nr': 'x8', 'args': ['x0', 'x1', 'x2', 'x3', 'x4', 'x5']},
    'i686': {'nr': 'eax', 'args': ['ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp']},
    'x86_64': {'nr': 'rax', 'args': ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']},
}


def manpage_link(name):
    """Get a link to the man page for this symbol."""
    # There are man pages for almost every syscall, so blindly link them.
    return '[man/](http://man7.org/linux/man-pages/man2/%s.2.html)' % (name,)


def cs_link(name):
    """Get a link to code search for this symbol."""
    return ('[cs/](https://cs.corp.google.com/search/?'
            'q=SYSCALL_DEFINE.*%s+package:^chromeos_public$)') % (name,)


def kernel_version(target):
    """Figure out what version of the kernel we're looking at."""
    cc = '%s-clang' % (target,)
    source = '#include <linux/version.h>\nLINUX_VERSION_CODE\n'
    ret = subprocess.run([cc, '-E', '-P', '-'],
                         input=source,
                         stdout=subprocess.PIPE,
                         encoding='utf-8')
    line = ret.stdout.splitlines()[-1]
    ver = int(line)
    return (ver >> 16 & 0xff, ver >> 8 & 0xff, ver & 0xff)


def find_symbols(target):
    """Find all the symbols using |target|."""
    cc = '%s-clang' % (target,)
    source = '#include <%s>\n' % (HEADER,)
    ret = subprocess.run([cc, '-E', '-dD', '-P', '-'],
                         input=source,
                         stdout=subprocess.PIPE,
                         encoding='utf-8')

    table = {}

    # Find all the symbols that are known.  We have to do two passes as the
    # headers like to #undef & redefine names.
    matcher = re.compile(r'^#define\s+(SYS_[^\s]+)\s+__NR_')
    symbols = set()
    for line in ret.stdout.splitlines():
        m = matcher.match(line)
        if m:
            sym = m.group(1)
            symbols.add(sym)

    # Because they can ...
    matcher = re.compile(r'^#define\s+(__ARM_NR_[^\s]+)\s+')
    for line in ret.stdout.splitlines():
        m = matcher.match(line)
        if m:
            sym = m.group(1)
            symbols.add(sym)

    source += '\n'.join('__%s %s' % (x, x) for x in symbols)

    # Parse our custom code and extract the symbols.
    ret = subprocess.run([cc, '-E', '-P', '-'],
                         input=source,
                         stdout=subprocess.PIPE,
                         encoding='utf-8')

    for line in ret.stdout.splitlines():
        if line.startswith('__'):
            sym, val = line.strip().split(' ', 1)
            if sym.startswith('____ARM'):
                sym = 'ARM_' + sym[11:]
                if sym == 'ARM_BASE':
                    continue
            else:
                sym = sym[6:]
            if val.startswith('('):
                val = constants.math_eval(val)
            val = int(val)
            assert sym not in table, 'sym %s already found' % (sym,)
            table[sym] = val

    return table


def load_table():
    """Return a table of all the symbol values (and aliases)."""
    all_tables = {}
    for target in constants.TARGETS:
        all_tables[target] = find_symbols(target)
    return all_tables


def sort_table(table):
    """Return a sorted table."""
    def sorter(element):
        try:
            num = int(element[1])
        except ValueError:
            num = 0
        return (num, element[0])
    return sorted(table.items(), key=sorter)


def get_md_table(table, prototypes):
    """Return the table in markdown format."""
    ret = []
    last_num = 0
    for sym, num in sort_table(table):
        # Fill in holes in the table so it's obvious to the user when searching.
        # Unless it's an obviously large gap for ABI reasons.  We pick 100 as an
        # arbitrary constant that seems to work.
        if num - last_num < 100:
            for stub in range(last_num + 1, num):
                ret.append('| %i | *not implemented* | | 0x%02x ||' %
                           (stub, stub))
        last_num = num

        line = ('| %i | %s | %s %s | 0x%02x | ' %
                (num, sym, manpage_link(sym), cs_link(sym), num))
        prototype = prototypes.get(sym, ['?'] * 6)
        prototype = (prototype + ['-'] * 6)[0:6]
        line += ' | '.join(x.replace('*', r'\*').replace('_', r'\_')
                           for x in prototype)
        line += ' |'

        ret.append(line)
    return ret


def get_md_common(tables):
    all_syscalls = set()
    for table in tables.values():
        all_syscalls.update(table.keys())

    desc = [x.split(' ')[0] for x in ORDER.values()]
    targets = [
        [x for x in constants.TARGETS if x.startswith(frag)][0]
        for frag in ORDER.keys()
    ]

    ret = [
        '',
        '### Cross-arch Numbers',
        '',
        ('This shows the syscall numbers for (hopefully) the same syscall name '
         'across architectures.'),
        'Consult the [Random Names](#naming) section for common gotchas.',
        '',
        '| syscall name | %s |' % (' | '.join(desc),),
        '|---|' + (':---:|' * len(desc)),
    ]
    for syscall in sorted(all_syscalls):
        ret.append(
            '| %s | %s |' %
            (syscall, ' | '.join(str(tables[x].get(syscall, '-'))
                                 for x in targets))
        )
    return ret


def load_prototypes():
    """Parse out prototypes from the kernel headers."""
    # Find the path to the kernel trees in the checkout.
    kernels = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', '..', 'src', 'third_party', 'kernel')
    # Load all the kernel versions that have the header file we need.
    versions = [x for x in os.listdir(kernels)
                if (re.match('^v[0-9.]+$', x) and
                    os.path.exists(os.path.join(kernels, x, 'include', 'linux',
                                                'syscalls.h')))]
    # Sort the versions to find the latest (which should be best?).
    versort = sorted([int(x) for x in v[1:].split('.')]
                     for v in versions)
    latest = versort[-1]

    syscalls = os.path.join(kernels, 'v%s' % '.'.join(str(x) for x in latest),
                            'include', 'linux', 'syscalls.h')
    ret = {}
    with open(syscalls) as fp:
        entries = re.findall(r'^asmlinkage long sys_([^(]*)\s*\(([^)]+)\)',
                             fp.read(), flags=re.M)
        for name, prototype in entries:
            # Clean up the prototype a bit.
            params = [x.strip() for x in prototype.split(',')]
            if params == ['void']:
                params = []
            for i, param in enumerate(params):
                keywords = [x for x in param.split() if x not in ('__user',)]
                params[i] = ' '.join(keywords)
            ret[name] = params
    return ret


def get_parser():
    """Return a command line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--inplace', action='store_true',
                        help='Update the markdown file directly.')
    return parser


def main(argv):
    """The main func!"""
    parser = get_parser()
    opts = parser.parse_args(argv)

    tables = load_table()
    prototypes = load_prototypes()

    md_data = []

    for (frag, desc) in ORDER.items():
        target = [x for x in constants.TARGETS if x.startswith(frag)][0]

        ver = kernel_version(target)
        sver = '.'.join(str(x) for x in ver)

        table = tables[target]
        reg_nr = REGS[frag]['nr']
        reg_args = REGS[frag]['args']
        md_data += [
            '',
            '### %s' % (desc,),
            '',
            'Compiled from [Linux %s headers][linux-headers].' % (sver,),
            '',
            ('| NR | syscall name | references | %%%s | arg0\u00a0(%%%s) | '
             'arg1\u00a0(%%%s) | arg2\u00a0(%%%s) | arg3\u00a0(%%%s) | '
             'arg4\u00a0(%%%s) | arg5\u00a0(%%%s) |') % (reg_nr, *reg_args),
            '|:---:|---|:---:|:---:|---|---|---|---|---|---|',
        ]
        md_data += get_md_table(table, prototypes)

    md_data += get_md_common(tables)

    if opts.inplace:
        md_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               MARKDOWN)
        with open(md_file) as fp:
            old_data = fp.readlines()

        i = None
        for i, line in enumerate(old_data):
            if line.startswith(START_OF_TABLE):
                break
        else:
            print('ERROR: could not find table in %s' % (md_file,),
                  file=sys.stderr)
            sys.exit(1)

        old_data = old_data[0:i + 1]
        with open(md_file, 'w') as fp:
            fp.writelines(old_data)
            fp.write('\n'.join(md_data) + '\n')
    else:
        print('\n'.join(md_data))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
