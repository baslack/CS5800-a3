import machine
import os
import sys
from typing import List

kDFA_flag = "--dfa"
kNFAL_flag = "--nfal"
kCONV_flag = '--conv'
kTAPE_flag = 'tape'
kDFA_ext = "dfa"
kNFAL_ext = "nfal"


class NoMachineException(Exception):
    pass


class NoInputException(Exception):
    pass


class FilePath_DNE_Exception(Exception):
    pass


class FilePath_NotSupplied_Exception(Exception):
    pass


class ConversionWithoutNFA_Exception(Exception):
    pass


def errmsg(*args, **flags):
    print(*args, file=sys.stderr, **flags)


def pathfix(_str: str) -> str:
    unix_style = "/" in _str
    win_style = "\\" in _str
    mac_style = ":" in _str
    if unix_style:
        _str = _str.split("/")
    elif win_style:
        _str = _str.split("\\")
    elif mac_style:
        _str = _str.split(":")
    _str = [os.path.expanduser(x) for x in _str]
    return os.path.join(*_str)


def parsecommands(argv: List[str]) -> dict:
    commands = dict()

    # check for machine settings
    if kNFAL_flag in argv:
        index = argv.index(kNFAL_flag)
        try:
            filepath = pathfix(argv[index + 1])
            if os.path.isfile(filepath):
                commands[kNFAL_flag] = filepath
            else:
                raise FilePath_DNE_Exception(kNFAL_flag, filepath)
        except IndexError:
            raise FilePath_NotSupplied_Exception(kNFAL_flag)
    elif kDFA_flag in argv:
        index = argv.index(kDFA_flag)
        try:
            filepath = pathfix(argv[index + 1])
            if os.path.isfile(filepath):
                commands[kDFA_flag] = filepath
            else:
                raise FilePath_DNE_Exception(kDFA_flag, filepath)
        except IndexError:
            raise FilePath_NotSupplied_Exception(kDFA_flag)
    else:
        # no machine tags
        raise NoMachineException

    # setup location for converted DFA
    if kCONV_flag in argv:
        if not kNFAL_flag in argv:
            raise ConversionWithoutNFA_Exception
        index = argv.index(kCONV_flag)
        try:
            filepath = pathfix(argv[index + 1])
            commands[kCONV_flag] = filepath
        except IndexError:
            # no filepath supplied for CONV
            # strip extension for DFA
            filename = commands[kNFAL_flag].rpartition(".")[0]
            commands[kCONV_flag] = "{0}.{1}".format(filename, kDFA_ext)

    # check for an input string
    if not argv[1] in [kCONV_flag, kDFA_flag, kNFAL_flag]:
        commands[kTAPE_flag] = argv[1]
    else:
        raise NoInputException

    return commands


if __name__ == "__main__":
    commands = dict()
    try:
        commands = parsecommands(sys.argv)
    except NoMachineException:
        errmsg("Usage: simulator <inputstring> [", kDFA_flag, kNFAL_flag, "] <filepath>")
        exit(-1)
    except FilePath_NotSupplied_Exception as e:
        errmsg("Filepath Not Supplied: ", *e.args)
        exit(-2)
    except FilePath_DNE_Exception as e:
        errmsg("Filepath does not exist: ", *e.args)
        exit(-3)
    except NoInputException as e:
        errmsg("No input provided: ", *e.args)
        exit(-4)
    except ConversionWithoutNFA_Exception as e:
        errmsg("Usage: simulator <inputstring>", kNFAL_flag, "<filepath>", kCONV_flag, "[<filepath>]")
    # print(commands)

    if kNFAL_flag in commands:
        M = machine.NFAlambda(commands[kNFAL_flag])
        print("T-Table:")
        print(M.dumps_ttable())
        if kCONV_flag in commands:
            Mprime = M.convert()
            Mprime.export(commands[kCONV_flag])
            print("DFA Configuration:")
            print(Mprime.dumps())
            Mprime.load(machine.Tape(commands[kTAPE_flag]))
            try:
                computation = Mprime.exec()
                print("Accepted: ", computation["accepted"])
                print("Tape: ", computation["tape"])
                print("Machine Execution:")
                print(computation["output"])
            except machine.InvalidCharacterInTapeException as e:
                print("Tape contains invalid character", *[str(x) for x in e.args])
                print("Allowed characters: ", Mprime.alpha)
    elif kDFA_flag in commands:
        M = machine.DFA(commands[kDFA_flag])
        M.load(machine.Tape(commands[kTAPE_flag]))
        try:
            computation = M.exec()
            print("Accepted: ", computation["accepted"])
            print("Tape: ", computation["tape"])
            print("Machine Execution:")
            print(computation["output"])
        except machine.InvalidCharacterInTapeException as e:
            print("Tape contains invalid character", *[str(x) for x in e.args])
            print("Allowed characters: ", M.alpha)

    print("Run Complete - Exiting")
    exit(0)
