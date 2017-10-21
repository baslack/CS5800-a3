import json
import copy
import sys
import os
import collections

kSTATES_PREFIX = "States"
kALPHA_PREFIX = "Alphabet"
kDTABLE_PREFIX = "D-Table"
kTTABLE_PREFIX = "T-Table"
kSTART_PREFIX = "Start"
kACCEPT_PREFIX = "Accept"
kLAMBA = ""
kEMPTYSET = "0"


def generateConfigDFA():
    config = dict()
    config[kSTATES_PREFIX] = list(set("AB"))
    config[kALPHA_PREFIX] = list(set("ab"))
    config[kDTABLE_PREFIX] = collections.defaultdict(dict)
    for this_state in config[kSTATES_PREFIX]:
        for this_alpha in config[kALPHA_PREFIX]:
            config[kDTABLE_PREFIX][this_state][this_alpha] = this_state
    config[kSTART_PREFIX] = "A"
    config[kACCEPT_PREFIX] = list(set("A"))
    filepath = os.path.join(os.path.expanduser("~"), "Desktop", "test_config.dfa")
    with open(filepath, "w+") as f:
        json.dump(config, f)


def generateConfigNFAlamba():
    config = dict()
    config[kSTATES_PREFIX] = list(set("AB"))
    config[kALPHA_PREFIX] = [kLAMBA, 'a', 'b']
    config[kDTABLE_PREFIX] = collections.defaultdict(dict)
    for this_state in config[kSTATES_PREFIX]:
        for this_alpha in config[kALPHA_PREFIX]:
            config[kDTABLE_PREFIX][this_state][this_alpha] = this_state
    config[kSTART_PREFIX] = "A"
    config[kACCEPT_PREFIX] = list(set("A"))
    filepath = os.path.join(os.path.expanduser("~"), "Desktop", "test_config.nfal")
    with open(filepath, "w+") as f:
        json.dump(config, f)


def testDFA():
    test = DFA(filepath=os.path.join(os.path.expanduser("~"), "Desktop", "test_config.dfa"))
    tape = Tape("aaabbabaabc")
    test.load(tape)
    test.exec()
    # print(test.states, test.alpha, test.d_table, test.start, test.accept)

def testNFAlamba():
    return NFAlambda(filepath=os.path.join(os.path.expanduser("~"), "Desktop", "test_config.nfal"))


class Machine:
    def __init__(self, filepath=None):
        self.current_state = None
        self.current_position = 0
        self.loaded_tape = None
        try:
            if filepath:
                self.config(filepath)
        except (InvalidConfigBlock, MissingConfigBlock, FileNotFoundError) as e:
            print(type(e), e, sys.stderr)

    def config(self, filepath):
        """
        uses a given file to configure the
        machine

        :param filepath:
        :return:
        """
        pass

    def exec(self):
        """
        performs a execution of the machine
        with the currently loaded tape

        :return:
        """
        pass

    def load(self, tape):
        """
        loads a tape in the machine

        :param Tape tape: tape to load into machine
        """
        self.loaded_tape = tape;


class DFA(Machine):
    def __init__(self, filepath=None):
        self.states = None
        self.alpha = None
        self.d_table = None
        self.start = None
        self.accept = None
        super().__init__(filepath)

    def config(self, filepath):

        file_exists = False

        # open filepath
        with open(filepath) as f:
            file_exists = True
            configuration = json.load(f)

            # validate config
            config_valid = True

            # check blocks
            needed_configs = {kSTATES_PREFIX, kALPHA_PREFIX, \
                              kDTABLE_PREFIX, kSTART_PREFIX, \
                              kACCEPT_PREFIX}
            all_blocks_present = needed_configs == set(configuration.keys())
            if not all_blocks_present:
                raise MissingConfigBlock(set(configuration.keys()).difference(needed_configs))

            # checking configs
            invalid_config_blocks = list()

            # is states a set
            states_are_set = (len(configuration[kSTATES_PREFIX]) == len(set(configuration[kSTATES_PREFIX])))
            config_valid &= states_are_set
            if not states_are_set:
                invalid_config_blocks.append(kSTATES_PREFIX)
            pass

            # is alpha a set
            alpha_is_set = (len(configuration[kALPHA_PREFIX]) == len(set(configuration[kALPHA_PREFIX])))
            config_valid &= alpha_is_set
            if not alpha_is_set:
                invalid_config_blocks.append(kALPHA_PREFIX)
            pass

            # is d-table defined for all states/symbols
            # for every state
            # for evert alpha
            # state is defined
            states = set(configuration[kSTATES_PREFIX])
            alpha = set(configuration[kALPHA_PREFIX])
            d_table = configuration[kDTABLE_PREFIX]
            missing_dtable_elements = list()
            d_table_valid = True
            try:
                for this_state in states:
                    for this_alpha in alpha:
                        if not (d_table[this_state][this_alpha] in states):
                            missing_dtable_elements.append((this_state, this_alpha, d_table[this_state][this_alpha]))
                            d_table_valid = False
            except KeyError as e:
                d_table_valid = False
                missing_dtable_elements.append(e)
            if not d_table_valid:
                invalid_config_blocks.append((kDTABLE_PREFIX, missing_dtable_elements))
            config_valid &= d_table_valid
            pass

            # is accepting subset of states
            accept = set(configuration[kACCEPT_PREFIX])
            accept_is_subset = accept.issubset(states)
            config_valid &= accept_is_subset
            if not accept_is_subset:
                invalid_config_blocks.append(kACCEPT_PREFIX)
            pass

            # is starting state element of states
            start = configuration[kSTART_PREFIX]
            start_in_states = start in states
            config_valid &= start_in_states
            if not start_in_states:
                invalid_config_blocks.append(kSTART_PREFIX)
            pass

            if not config_valid:
                raise InvalidConfigBlock(invalid_config_blocks)
            pass

            # configure DFA

            # set states
            self.states = copy.deepcopy(states)

            # set alpha
            self.alpha = copy.deepcopy(alpha)

            # set d-table
            self.d_table = copy.deepcopy(d_table)

            # set starting-state
            self.start = copy.deepcopy(start)

            # set accepting-states
            self.accept = copy.deepcopy(accept)
        if not file_exists:
            raise FileNotFoundError

    def exec(self):
        self.current_state = self.start
        self.current_position = 0
        try:
            while True:
                print("state: ", self.current_state)
                print("character: ", self.loaded_tape.read(self.current_position))
                print("new state: ", self.d_table[self.current_state][self.loaded_tape.read(self.current_position)])
                self.current_state = self.d_table[self.current_state][self.loaded_tape.read(self.current_position)]
                self.current_position += 1
        except IndexError as e:
            if self.current_state in self.accept:
                print("accepted {1}, state: {0}".format(self.current_state, str(self.loaded_tape)))
                return True
            else:
                print("rejected {1}, state: {0}".format(self.current_state, str(self.loaded_tape)))
                return False
        except KeyError as e:
            print("rejected {0}, invalid character on tape: {1}".format(str(self.loaded_tape), e))


class NFAlambda(Machine):
    def __init__(self, filepath=None):
        self.states = None
        self.alpha = None
        self.t_table = None
        self.start = None
        self.accept = None
        super().__init__(filepath)

    def config(self, filepath):
        with open(filepath) as f:
            configuration = json.load(f)

            # check needed blocks
            needed_configs = {kSTATES_PREFIX, kALPHA_PREFIX, \
                              kTTABLE_PREFIX, kSTART_PREFIX, \
                              kACCEPT_PREFIX}
            all_blocks_present = needed_configs == set(configuration.keys())
            if not all_blocks_present:
                raise MissingConfigBlock(set(configuration.keys()).difference(needed_configs))

            # validate blocks
            self.states = set([x.upper() for x in configuration[kSTATES_PREFIX]])
            if self.states == set():
                raise InvalidConfigBlock(kSTATES_PREFIX, self.states)
            self.alpha = set([x.lower() for x in configuration[kALPHA_PREFIX]])
            if self.alpha == set():
                raise InvalidConfigBlock(kALPHA_PREFIX, self.alpha)
            self.t_table = configuration[kTTABLE_PREFIX]
            for this_state in self.t_table.keys():
                for this_char in self.t_table[this_state].keys():
                    if self.t_table[this_state][this_char] == kEMPTYSET:
                        self.t_table[this_state][this_char] = set()
                    else:
                        self.t_table[this_state][this_char] = set(self.t_table[this_state][this_char])
                        if not self.t_table[this_state][this_char].issubset(self.states):
                            raise InvalidConfigBlock(kTTABLE_PREFIX, self.t_table[this_state][this_char])
            self.start = configuration[kSTART_PREFIX]
            if not self.start in self.states:
                raise InvalidConfigBlock(kSTART_PREFIX, self.start)
            self.accept = set([x.upper() for x in configuration[kACCEPT_PREFIX]])
            if not self.accept.issubset(self.states):
                raise InvalidConfigBlock(kACCEPT_PREFIX, self.accept)

    def exec(self):
        raise AttributeError("exec disabled for NFAlambda")


def convertMachine(nfa_l: NFAlambda) -> DFA:
    nfa_l.exec()
    return DFA()


class MissingConfigBlock(Exception):
    pass


class InvalidConfigBlock(Exception):
    pass


class Tape:
    def __init__(self, in_string):
        self.characters = list(in_string)

    def __str__(self):
        contents = ""
        for a in self.characters:
            contents += a
        return contents

    def read(self, position):
        return self.characters[position]

    def write(self, character, position):
        self.characters[position] = character


if __name__ == "__main__":
    print(testNFAlamba().__dict__)
