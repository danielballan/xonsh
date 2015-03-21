import os
import builtins
from argparse import ArgumentParser

DIRSTACK = []

def pushd(args, stdin=None):
    global DIRSTACK

    try:
        args = pushd_parser.parse_args(args)
    except SystemExit:
        return None, None

    pwd = builtins.__xonsh_env__['PWD']

    if args.dir is None:
        new_pwd = DIRSTACK.pop(0)
    elif os.path.isdir(args.dir):
        new_pwd = args.dir
    else:
        try:
            num = int(args.dir[1:])
            assert num >=0
        except:
            return None, 'Invalid argument to pushd: {0}\n'.format(args.dir)
        if num > len(DIRSTACK):
            return None, 'Too few elements in dirstack ({0} elements)\n'.format(len(DIRSTACK))
        elif args.dir.startswith('+'):
            if num == len(DIRSTACK):
                new_pwd = None
            else:
                new_pwd = DIRSTACK.pop(len(DIRSTACK)-1-num)
        elif args.dir.startswith('-'):
            if num == 0:
                new_pwd = None
            else:
                new_pwd = DIRSTACK.pop(num-1)
        else:
            return None, 'Invalid argument to pushd: {0}\n'.format(args.dir)
    if new_pwd is not None:
        DIRSTACK.insert(0, os.path.expanduser(pwd))

        o = None
        e = None
        if args.cd:
            o, e = builtins.default_aliases['cd']([new_pwd], None)

        if e is not None:
            return None, e

    if not builtins.__xonsh_env__.get('QUIET_PUSHD', False):
        return dirs([], None)

    return None, None

popd_parser = ArgumentParser(description="popd: pop from the directory stack")
def popd(args, stdin=None):
    dirstack = get_dirstack()
    return None, None

def dirs(args, stdin=None):
    global DIRSTACK
    dirstack = [os.path.expanduser(builtins.__xonsh_env__['PWD'])] + DIRSTACK

    try:
        args = dirs_parser.parse_args(args)
    except SystemExit:
        return None, None

    if args.clear:
        dirstack = []
        return None, None

    if args.long:
        o = dirstack
    else:
        d = os.path.expanduser('~')
        o = [i.replace(d, '~') for i in dirstack]

    if args.verbose:
        out = ''
        pad = len(str(len(o)-1))
        for (ix, e) in enumerate(o):
            blanks = ' ' * (pad - len(str(ix)))
            out += '\n{0}{1} {2}'.format(blanks, ix, e)
        out = out[1:]
    elif args.print_long:
        out = '\n'.join(o)
    else:
        out = ' '.join(o)

    N = args.N
    if N is not None:
        try:
            num = int(N[1:])
            assert num >=0
        except:
            return None, 'Invalid argument to dirs: {0}\n'.format(N)
        if num >= len(o):
            return None, 'Too few elements in dirstack ({0} elements)\n'.format(len(o))
        if N.startswith('-'):
            idx = num
        elif N.startswith('+'):
            idx  = len(o)-1-num
        else:
            return None, 'Invalid argument to dirs: {0}\n'.format(N)

        out = o[idx]

    return out+'\n', None

pushd_parser = ArgumentParser(description="pushd: push onto the directory stack")
pushd_parser.add_argument('-n',
        dest='cd',
        help='Suppresses the normal change of directory when adding directories to the stack, so that only the stack is manipulated.',
        action='store_false')
pushd_parser.add_argument('dir', nargs='?')

dirs_parser = ArgumentParser(description="dirs: view and manipulate the directory stack", add_help=False)
dirs_parser.add_argument('-c',
        dest='clear',
        help='Clears the directory stack by deleting all of the entries',
        action='store_true')
dirs_parser.add_argument('-p',
        dest='print_long',
        help='Print the directory stack with one entry per line.',
        action='store_true')
dirs_parser.add_argument('-v',
        dest='verbose',
        help='Print the directory stack with one entry per line, prefixing each entry with its index in the stack.',
        action='store_true')
dirs_parser.add_argument('-l',
        dest='long',
        help='Produces a longer listing; the default listing format uses a tilde to denote the home directory.',
        action='store_true')
dirs_parser.add_argument('N', nargs='?')
