from __future__ import print_function

import os
import sys
import glob
import shutil
import subprocess
import tempfile

from nose.tools import assert_true, assert_equal
from tools import integration, cleanfs, check_cmd, clean_import

from xdress.astparsers import PARSERS_AVAILABLE

if sys.version_info[0] >= 3:
    basestring = str

PROJNAME = "cppproj"
PROJDIR = os.path.abspath(PROJNAME)
INSTDIR = os.path.join(PROJDIR, 'install')
ROOTDIR = os.path.splitdrive(INSTDIR)[0] or '/'

GENERATED_PATHS = [
    [PROJDIR, 'build'],
    [PROJDIR, PROJNAME, 'basics.pxd'],
    [PROJDIR, PROJNAME, 'basics.pyx'],
    [PROJDIR, PROJNAME, 'cpp_basics.pxd'],
    [PROJDIR, PROJNAME, 'cpp_discovery.pxd'],
    [PROJDIR, PROJNAME, 'cpp_pybasics.pxd'],
    [PROJDIR, PROJNAME, 'cppproj_extra_types.pxd'],
    [PROJDIR, PROJNAME, 'cppproj_extra_types.pyx'],
    [PROJDIR, PROJNAME, 'discovery.pxd'],
    [PROJDIR, PROJNAME, 'discovery.pyx'],
    [PROJDIR, PROJNAME, 'pybasics.pxd'],
    [PROJDIR, PROJNAME, 'pybasics.pyx'],
    [PROJDIR, PROJNAME, 'stlc.pxd'],
    [PROJDIR, PROJNAME, 'stlc.pyx'],
    [PROJDIR, PROJNAME, 'tests'],
    [PROJDIR, 'src', 'cppproj_extra_types.h'],
    [INSTDIR],
    ]

# Because we want to guarentee build and test order, we can only have one 
# master test function which generates the individual tests.
@integration
def test_all():
    parsers = ['gccxml', 'clang']
    cases = [{'parser': p} for p in parsers]

    cwd = os.getcwd()
    base = os.path.dirname(cwd)
    pyexec = sys.executable
    xdexec = os.path.join(base, 'scripts', 'xdress')
    defaults = {'cwd': cwd, 'base': base, 'pyexec': pyexec, 'xdexec': xdexec, 
                'instdir': INSTDIR, 'rootdir': ROOTDIR}

    commands = (
        'PYTHONPATH="{base}" {pyexec} {xdexec} --debug -p={parser}\n'
        '{pyexec} setup.py install --prefix="{instdir}" --root="{rootdir}" -- --\n'
        )

    for case in cases:
        parser = case['parser']
        if not PARSERS_AVAILABLE[parser]:
            continue
        cleanfs(GENERATED_PATHS)
        rtn = 1
        holdsrtn = [rtn]  # needed because nose does not send() to test generator
        fill = dict(defaults)
        fill.update(case)
        cmds = commands.format(**fill).strip().splitlines()
        for cmd in cmds:
            yield check_cmd, cmd, PROJDIR, holdsrtn
            rtn = holdsrtn[0]
            if rtn != 0:
                break  # don't execute further commands
        if rtn != 0:
            break  # don't try further cases

        # we have now run xdress and build the project
        # What follow are project unit tests, no need to break on these
        instsite = os.path.join(INSTDIR, 'lib', 'python*', 'site-packages')
        instsite = glob.glob(instsite)[0]
        instproj = os.path.join(instsite, PROJNAME)

        with clean_import('basics', [instproj, instsite]) as basics:
            yield basics.func0
    else:
        cleanfs(GENERATED_PATHS)