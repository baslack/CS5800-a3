import machine
import os
import sys
import json
from typing import List

kDFA_flag = "--dfa"
kNFAL_flag = "--nfal"
kCONV_flag = '--conv'
kTAPE_flag = 'tape'


class NoMachineException(Exception):
    pass


class NoInputException(Exception):
    pass


class FilePath_DNE_Exception(Exception):
    pass


class FilePath_NotSupplied_Exception(Exception):
    pass


def errmsg(*args, **flags):
    print(*args, file=sys.stderr, **flags)


def parsecommands(argv: List[str]) -> dict:
    commands = dict()

    # check for machine settings
    if kNFAL_flag in argv:
        index = argv.index(kNFAL_flag)
        try:
            if os.path.isfile(argv[index + 1]):
                commands[kNFAL_flag] = argv[index + 1]
            else:
                raise FilePath_DNE_Exception(kNFAL_flag, argv[index + 1])
        except IndexError:
            raise FilePath_NotSupplied_Exception(kNFAL_flag)
    elif kDFA_flag in argv:
        index = argv.index(kDFA_flag)
        if os.path.isfile(argv[index + 1]):
            commands[kDFA_flag] = argv[index + 1]
        else:
            raise FilePath_DNE_Exception(kDFA_flag, argv[index + 1])
    else:
        # no machine tags
        raise NoMachineException

    # setup locationi for converted DFA
    if kCONV_flag in argv:
        index = argv.index(kCONV_flag)
        if os.path.isfile(argv[index + 1]):
            commands[kCONV_flag] = argv[index + 1]
        else:
            raise FilePath_DNE_Exception(kCONV_flag, argv[index + 1])

    # check for an input string
    if not argv[1] in [kCONV_flag, kDFA_flag, kNFAL_flag]:
        commands[kTAPE_flag] = argv[1]
    else:
        raise NoInputException

    return commands


if __name__ == "__main__":
    try:
        commands = parsecommands(sys.argv)
    except NoMachineException:
        errmsg("Usage: simulator [", kDFA_flag, kNFAL_flag, "] <filepath>")
    except FilePath_NotSupplied_Exception as e:
        errmsg("Filepath Not Supplied: ", *e.args)
    pass
