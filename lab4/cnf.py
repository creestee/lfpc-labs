from itertools import product
from lib2to3.pgen2 import grammar
import pprint

grammar_dict = {
    'S': ['AC', 'bA', 'B', 'aA'],
    'A': ['$', 'aS', 'ABAb'],
    'B': ['a', 'AbSA'],
    'C': ['abC'],
    'D': ['AB'],
}

print('')
print("Initial grammar : ")
print("^"*70)
pprint.pprint(grammar_dict, sort_dicts=False)

term_syms = ['a', 'b']
unterm_syms = ['S', 'A', 'B', 'C', 'D']
empty_sym = '$'
start_sym = 'S'

null_syms = set()
flag = False

while not flag:
    flag = True
    for k, v in grammar_dict.items():
        if k in null_syms:
            continue
        for string in v:
            if string == empty_sym or all([nonterminal in null_syms for nonterminal in string]):
                null_syms.add(k)
                flag = False

print('')
print("Nullable Symbols : ")
print("^"*70)
pprint.pprint(null_syms, sort_dicts=False)

def filter(word, to_replace, replacement):
    options = [(c,) if c != to_replace else (to_replace, replacement) for c in word]
    return ("".join(o) for o in product(*options))

keys = []

for i in grammar_dict.keys():
    keys.append(i)

def remove_epsilon(grammar, k = '', p = '', n = 0, i = 0, trigger = False, iteration = 0):
    if trigger == True:
        aux = iteration
        if i == n:
            trigger = False
            return
        cur_p = p[i]
        for null_var in null_syms:
            empty_p = filter(cur_p, null_var, '')
        grammar[k] += empty_p
        return remove_epsilon(grammar, keys[iteration], grammar[keys[iteration]], n, i + 1, True, aux)
    grammar[keys[iteration]] = list(set(grammar[keys[iteration]]))
    if empty_sym in grammar[keys[iteration]]:
        grammar[keys[iteration]].remove(empty_sym)
    remove_epsilon(grammar, keys[iteration], grammar[keys[iteration]], len(grammar[keys[iteration]]), 0, True, iteration + 1)

    return grammar

remove_epsilon(grammar_dict)

print('')
print("Remove epsilon productions : ")
print("^"*70)
pprint.pprint(grammar_dict, sort_dicts=False)

unit_hash = {}
for k,p in grammar_dict.items():
    unit_hash[k] = []
    for cur_p in p:
        if cur_p in unterm_syms:
            unit_hash[k].append(cur_p)

unit_hash = dict( [(k,v) for k,v in unit_hash.items() if len(v)>0]) # remove empty keys

for k, v in grammar_dict.items():
    if k in unit_hash.keys():
        for renaming in unit_hash[k]:
            grammar_dict[k].remove(renaming)
            if renaming in grammar_dict:
                grammar_dict[k].extend(grammar_dict[renaming])

for k, v in grammar_dict.items():
    grammar_dict[k] = list(set(grammar_dict[k]))

print("")
print("Remove unit productions : ")
print("^"*70)
pprint.pprint(grammar_dict, sort_dicts=False)

non_generating = []
for key, value in grammar_dict.items():
    generating = False
    for rule in value:
        if (all(r not in non_generating for r in rule)):
            generating = True

    if generating is False:
        non_generating.append(key)

for a in non_generating:
    if a in grammar_dict.keys():
        grammar_dict.pop(a, None)
    for k, v in grammar_dict:
        for rule in v:
            if a in rule:
                grammar_dict[k].remove(rule)

print('')
print("Remove nonproductive symbols : ")
print("^"*70)
pprint.pprint(grammar_dict, sort_dicts=False)

reachables = [start_sym]
for r in reachables:
    rules = []
    if r in unterm_syms:
        rules = grammar_dict[r]
    for rule in rules:
        for symbol in rule:
            if symbol not in reachables: 
                reachables.append(symbol)

all_symbols = set().union(unterm_syms, term_syms)

unreachable = all_symbols - set(reachables)

for a in unreachable:
    if a in grammar_dict.keys():
        grammar_dict.pop(a, None)

print('')
print("Remove nonreachable symbols : ")
print("^"*70)
pprint.pprint(grammar_dict, sort_dicts=False)

split_dict = {}

for k, v in grammar_dict.items():
    if k not in split_dict.keys():
        split_dict[k] = []
    for rule in v:
        split_dict[k].append(list(rule))

counter = 1
new_rules = {}
for t in term_syms:
    new_unterm = 'X' + str(counter)
    # split_dict[new_unterm] = list([t])
    new_rules[new_unterm] = list([t])
    counter += 1

for k, v in split_dict.items():
    for rule in v:
        if len(rule) > 1:
            for i, char in enumerate(rule):
                if char.islower():
                    myKey = [key for key, value in new_rules.items() if value == [char]]
                    rule[i] = myKey.pop()

counter = 1

while True:
    flag = True
    for key, value in split_dict.items():
        for a in value:
            if len(a) > 2:
                new_rule = [a[0], a[1]]
                if new_rule not in new_rules.values():
                    flag = False
                    new_rules['Y' + str(counter)] = new_rule
                    counter += 1

    for k, v in split_dict.items():
        for i, a in enumerate(split_dict[k]):
            # print(split_dict[k][i])
            if len(a) > 2:
                toFind = [split_dict[k][i][0], split_dict[k][i][1]]
                for k_, v_ in new_rules.items():
                    if toFind == v_:
                        split_dict[k][i] = split_dict[k][i][1:]
                        split_dict[k][i][0] = k_
                    
    if flag: break

for k, v in new_rules.items():
    new_rules[k] = [''.join(new_rules[k])]

for k, v in split_dict.items():
    for i, a in enumerate(split_dict[k]):
        split_dict[k][i] = ''.join(split_dict[k][i])

split_dict.update(new_rules)

print('')
print("CNF : ")
print("^"*70)
pprint.pprint(split_dict, sort_dicts=False)