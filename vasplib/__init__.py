NAME = 'vasplib'

def info():
    """
        Show basic information about """+NAME+""", its location and version.
    """

    print('Vasplib\n------------')
    print('')
    print('Dependency')
    print('------------')
    for modui in ['numpy', 'scipy']:
        try:
            mm = __import__(modui)
            print('%10s %10s   %s' % (modui, mm.__version__, mm.__path__[0]))
        except ImportError:
            print('%10s %10s Not Found' % (modui, ''))
    print()