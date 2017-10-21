import json
import copy
import sys
import os
import collections

kSTATES_PREFIX = "States"
kALPHA_PREFIX = "Alphabet"
kDTABLE_PREFIX = "D-Table"
kSTART_PREFIX = "Start"
kACCEPT_PREFIX = "Accept"


def generateConfig():
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


def testDFA():
    test = DFA(filepath=os.path.join(os.path.expanduser("~"), "Desktop", "test_config.dfa"))
    tape = Tape("aaabbabaabc")
    test.load(tape)
    test.exec()
    # print(test.states, test.alpha, test.d_table, test.start, test.accept)


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
            missing_blocks = list()

            # does config contain:
            # states block
            states_present = (kSTATES_PREFIX in configuration.keys())
            config_valid &= states_present
            if not states_present:
                missing_blocks.append(kSTATES_PREFIX)

            # alphabet block
            alpha_present = (kALPHA_PREFIX in configuration.keys())
            config_valid &= alpha_present
            if not alpha_present:
                missing_blocks.append(kALPHA_PREFIX)
            pass

            # d-table block
            d_table_present = (kDTABLE_PREFIX in configuration.keys())
            config_valid &= d_table_present
            if not d_table_present:
                missing_blocks.append(kDTABLE_PREFIX)
            pass

            # starting state block
            start_present = (kSTART_PREFIX in configuration.keys())
            config_valid &= start_present
            if not start_present:
                missing_blocks.append(kSTART_PREFIX)
            pass

            # accepting states block
            accepting_present = (kACCEPT_PREFIX in configuration.keys())
            config_valid &= accepting_present
            if not alpha_present:
                missing_blocks.append(kACCEPT_PREFIX)
            pass

            if not config_valid:
                raise MissingConfigBlock(*missing_blocks)
            pass

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
    testDFA()
