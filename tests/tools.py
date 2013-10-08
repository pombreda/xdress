from __future__ import print_function

import os
import sys
import imp
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

from nose.tools import assert_true, assert_equal
from nose.plugins.attrib import attr

if sys.version_info[0] >= 3:
    basestring = str

unit = attr('unit')
integration = attr('integration')

def cleanfs(paths):
    """Removes the paths from the file system."""
    for p in paths:
        p = os.path.join(*p)
        if os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            shutil.rmtree(p)

def check_cmd(args, cwd, holdsrtn):
    """Runs a command in a subprocess and verifies that it executed properly.
    """
    if not isinstance(args, basestring):
        args = " ".join(args)
    print("TESTING: running command in {0}:\n\n{1}\n".format(cwd, args))
    f = tempfile.NamedTemporaryFile()
    rtn = subprocess.call(args, shell=True, cwd=cwd, stdout=f, stderr=f)
    if rtn != 0:
        f.seek(0)
        print("STDOUT + STDERR:\n\n" + f.read())
    f.close()
    holdsrtn[0] = rtn
    assert_equal(rtn, 0)

@contextmanager 
def clean_import(name, paths=None):
    """Imports and returns a module context manager and then removes
    all modules which didn't originally exist when exiting the block.
    Be sure to delete any references to the returned module prior to 
    exiting the context.
    """
    sys.path = paths + sys.path
    origmods = set(sys.modules.keys())
    mod = imp.load_module(name, *imp.find_module(name, paths))
    yield mod
    sys.path = sys.path[len(paths):]
    del mod
    newmods = set(sys.modules.keys()) - origmods
    for newmod in newmods:
        del sys.modules[newmod]