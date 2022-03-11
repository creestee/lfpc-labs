class NFA:

    def __init__(self, states, F, input_alphabet, transitions):
        self.states = states
        self.F = F
        self.input_alphabet = input_alphabet
        self.transitions = transitions
        self.NFA_transitions_dict = {}

    def convert_to_dict(self):
        for a in self.transitions:
            self.NFA_transitions_dict[a[0]] = []

        for a in self.transitions:
            self.NFA_transitions_dict[a[0]].append(a[1])


class DFA():
    def __init__(self, NFA):
        self.NFA = NFA
        self.states = NFA.states
        self.F = NFA.F
        self.input_alphabet = NFA.input_alphabet
        self.DFA_transitions_dict = {}
    
    def nfa_to_dfa(self, nfa, counter = 0):
        
        updating_states = NFA.states

        for a in nfa:
        
            # print(a)

            if a not in self.DFA_transitions_dict.keys():
                self.DFA_transitions_dict[a] = []

                discover_new_state = False

                if len(nfa[a]) > 1:
                    
                    new_state = []

                    for b in nfa[a]:
                        new_state.append(b)

                    self.DFA_transitions_dict[a] = ''.join(new_state)

                    for input_a in self.input_alphabet:
                        new_transition = tuple([''.join(new_state), input_a])
                        adj_state = [nfa[tuple([x, input_a])] for x in new_state]
                        new_set = []

                        for split_array in adj_state:
                            new_set = split_array + new_set

                        new_set = list(set(new_set))
                        self.DFA_transitions_dict[new_transition] = new_set[0] if len(new_set) == 1 else ''.join(sorted(new_set))

                        updating_states.append(self.DFA_transitions_dict[new_transition])

# ------------------------------------

                # if nfa[a] not in updating_states:

                #     for input_a in self.input_alphabet:
                #         new_transition = tuple(list([nfa[a], input_a]))
                #         adj_state = [nfa[tuple([x, input_a])] for x in nfa[a]]
                #         new_set = []

                #         for split_array in adj_state:
                #             new_set = split_array + new_set

                #         new_set = list(set(new_set))
                #         self.DFA_transitions_dict[new_transition] = new_set[0] if len(new_set) == 1 else ''.join(sorted(list(new_set)))

                #         updating_states.append(self.DFA_transitions_dict[new_transition])

# ------------------------------------

                else: 
                    self.DFA_transitions_dict[a] = nfa[a][0]

        if counter < 3:
            return self.nfa_to_dfa(self.DFA_transitions_dict, counter + 1)

        print("NEW STATES -----", sorted(set(updating_states)))  
        for a in self.DFA_transitions_dict:
            print(a, f"{self.DFA_transitions_dict[a] : ^10}")

NFA = NFA(
    # States
    ['q0', 'q1', 'q2', 'q3'],
    
    # F
    'q3', 
    
    # Input Alphabet
    ['a', 'b'],
    
    # Transitions
    [
        [('q0', 'a'), 'q0'],
        [('q0', 'b'), 'q1'],
        [('q1', 'a'), 'q1'],
        [('q1', 'a'), 'q2'],
        [('q1', 'b'), 'q3'],
        [('q2', 'a'), 'q2'],
        [('q2', 'b'), 'q3']
    ]

)

NFA.convert_to_dict()

DFA = DFA(NFA)

DFA.nfa_to_dfa(NFA.NFA_transitions_dict)