from os.path import join
from subprocess import check_call

'''A file object to `/dev/null`.'''
import os as _os
DEV_NULL = open(_os.devnull, "r+")

_ensure_str_encoding = []
def ensure_str(string):
    '''Ensure that the argument is in fact a Unicode string.  If it isn't,
    then:

      - on Python 2, it will be decoded using the preferred encoding;
      - on Python 3, it will trigger a `TypeError`.
    '''
    # Python 2
    if getattr(str, "decode", None) and getattr(str, "encode", None):
        if isinstance(string, unicode):
            return string
        if not _ensure_str_encoding:
            import locale
            _ensure_str_encoding.append(locale.getpreferredencoding(False))
        return string.decode(_ensure_str_encoding[0])
    # Python 3
    if isinstance(string, str):
        return string
    raise TypeError("not an instance of 'str': " + repr(string))

def rename(src_filename, dest_filename):
    '''Rename a file (allows overwrites on Windows).'''
    import os
    if os.name == "nt":
        import ctypes
        success = ctypes.windll.kernel32.MoveFileExW(
            ensure_str(src_filename),
            ensure_str(dest_filename),
            ctypes.c_ulong(0x1),
        )
        if not success:
            raise ctypes.WinError()
        return
    os.rename(src_filename, dest_filename)

def mkdirs(path):
    import os
    try:
        os.makedirs(path)
    except OSError:
        pass

def read_file(filename, binary=False):
    '''Read the contents of a file.'''
    with open(filename, "rb" if binary else "rt") as file:
        contents = file.read()
    if not binary:
        contents = ensure_str(contents)
    return contents

def write_file(filename, contents, binary=False, safe=True):
    '''Write the contents to a file.  Unless `safe` is false, it is performed
    as atomically as possible.  A temporary directory is used to store the
    file while it is being written.'''
    if safe and filename == "/dev/stdout":
        safe = False
    if not safe:
        if not binary:
            contents = ensure_str(contents)
        with open(filename, "wb" if binary else "wt") as file:
            file.write(contents)
        return
    import os, shutil, tempfile
    try:
        tmp_dir = tempfile.mkdtemp(
            suffix=".tmp",
            prefix="." + os.path.basename(filename) + ".",
            dir=os.path.dirname(filename),
        )
        tmp_filename = os.path.join(tmp_dir, "file.tmp")
        write_file(tmp_filename, contents, binary, safe=False)
        rename(tmp_filename, filename)
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass

class WorkDir(object):
    '''A context for changing to a different working directory.  The original
    working directory is restored upon exiting the context.'''

    def __init__(self, path):
        '''Initialize a context for changing the working directory.'''
        self.path = path

    def __enter__(self):
        '''Change the working directory and return the path to the previous
        working directory.'''
        import os
        self.prevdir = os.getcwd()
        os.chdir(self.path)
        return self.prevdir

    def __exit__(self, type, value, traceback):
        '''Restore the the temporary directory.'''
        import os
        os.chdir(self.prevdir)

class FileLock(object):
    '''A context for holding an exclusive file lock, which is released upon
    exiting the context.  (Unix only.)'''

    def __init__(self, path, block=True):
        '''Initialize a context for holding an exclusive file lock.'''
        self.path  = path
        self.block = block

    def __enter__(self):
        '''Acquire the lock.  Returns nothing.  If `block` was set to true,
        then an `IOError` is raised if the file is already locked.'''
        import fcntl
        flags = fcntl.LOCK_EX
        if not self.block:
            flags |= fnctl.LOCK_NB
        self.lockfile = open(self.path, "w")
        try:
            fcntl.lockf(self.lockfile, flags)
        except:
            self.lockfile.close()
            raise

    def __exit__(self, type, value, traceback):
        '''Release the lock.'''
        self.lockfile.close()

def format_pairs(kvs):
    return " ".join("{0}={1}".format(*kv) for kv in sorted(dict(kvs).items()))

def run_with_argv(funcs):
    import sys
    func_map = dict((f.__name__, f) for f in funcs)
    func_map[sys.argv[1]](*sys.argv[2:])

def parse_table(s):
    from io     import StringIO
    from pandas import read_table
    return read_table(StringIO(s), sep=" *", engine="python")

def write_table(fn, t):
    from pandas import DataFrame
    write_file(fn, DataFrame(t).to_csv(sep=" ", na_rep="nan", index=False))

def execfile(fn):
    globals = {}
    exec(compile(open(fn, "rt").read(), fn, "exec"), globals, {})
    return globals

def replace_ext(fn, ext):
    import os
    return os.path.splitext(fn)[0] + ext

def record_to_dict(x):
    return dict(zip(x.dtype.names, x))