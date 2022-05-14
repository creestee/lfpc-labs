import copy

gramar = {
    'S': ['AC', 'bA', 'B', 'aA'],
    'A': ['X', 'aS', 'ABAb'],
    'B': ['a', 'AbSA'],
    'C': ['abC'],
    'D': ['AB']
}
term_syms = ['a', 'b']
unterm_syms = ['S', 'A', 'B', 'C', 'D']
empty_sym = 'X'
start_sym = 'S'

pool = {
    'ind': 0,
    'pool': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
}

def gen_unterm(pool, used_unterm_syms):
    pool_array = pool['pool']
    cur_ind = pool['ind']
    cur_unterm_syms = pool_array[cur_ind]
    while(cur_unterm_syms in used_unterm_syms) and cur_ind < 26:
        cur_ind += 1
        cur_unterm_syms = pool_array[cur_ind]
    pool['ind'] = cur_ind
    if cur_ind >= 26:
        return None
    else:
        return cur_unterm_syms

convert_term_syms_dict = {}
for k,p in gramar.items():
    for p_ind in range(0, len(p)):
        cur_p = p[p_ind]
        for ind in range(0, len(cur_p)):
            if cur_p[ind] in term_syms:
                if cur_p[ind] in convert_term_syms_dict:
                    p[p_ind] = cur_p[0:ind] + convert_term_syms_dict[cur_p[ind]] + cur_p[(ind+1):]
                    cur_p = p[p_ind]
                else:
                    convert_term_syms_dict[cur_p[ind]] = gen_unterm(pool, unterm_syms)
                    p[p_ind] = cur_p[0:ind] + convert_term_syms_dict[cur_p[ind]] + cur_p[(ind+1):]
                    unterm_syms.append(p[p_ind][ind])
                    cur_p = p[p_ind]

for p,k in convert_term_syms_dict.items():
    gramar[k] = [p]
print("TERM Result: "+str(gramar))

def shink_grammar(gramar, unterm_syms, pool):
    new_p_dict = {}
    shink_count = 0
    for k,p in gramar.items():
        for ind in range(0, len(p)):
            if len(p[ind]) > 2:
                new_unterm = gen_unterm(pool, unterm_syms)
                unterm_syms.append(new_unterm)
                new_p_dict[new_unterm] = p[ind][1:]
                p[ind] = p[ind][0]+new_unterm
    for k,p in new_p_dict.items():
        gramar[k] = [p]
        shink_count += 1
    return shink_count

while(shink_grammar(gramar, unterm_syms, pool) > 0):
    pass

print("Shrink out: "+str(gramar))

null_syms = [empty_sym]
null_sym_count = 0xff
while(null_sym_count > 0):
    null_sym_count = 0
    for k,p in gramar.items():
        for cur_p in p:
            is_null_p = True
            for sym in cur_p:
                is_null_p = is_null_p and (sym in null_syms)
            if is_null_p and (k not in null_syms):
                null_syms.append(k)
                null_sym_count += 1
print("Nullable symbols: "+str(null_syms))

def gen_mask_set(null_syms, p, empty_sym):
    empty = [p]
    item_count = 0xff
    while(item_count > 0):
        item_count = 0
        for ind in range(0, len(empty)):
            cur_item = empty[ind]
            for cur_ind in range(0, len(cur_item)):
                if cur_item[cur_ind] in null_syms:
                    new_p = cur_item[0:cur_ind]+cur_item[(cur_ind+1):]
                    if len(new_p)==0:
                        new_p = empty_sym
                    if new_p not in empty:
                        empty.append(new_p)
                        item_count += 1
    return empty

new_grammar_dict = {}
for k,p in gramar.items():
    new_grammar_dict[k] = copy.copy(p)
    for ind in range(0, len(p)):
        cur_p = p[ind]
        empty_p = gen_mask_set(null_syms, cur_p, empty_sym)
        new_grammar_dict[k] += empty_p
    new_grammar_dict[k] = list(set(new_grammar_dict[k]))
    if empty_sym in new_grammar_dict[k]:
        new_grammar_dict[k].remove(empty_sym)

print("No nullable: "+str(new_grammar_dict))

unit_hash = {}
unit_revert_hash = {}
for k,p in new_grammar_dict.items():
    unit_hash[k] = []
    for cur_p in p:
        if cur_p in unterm_syms:
            unit_hash[k].append(cur_p)
            if cur_p in unit_revert_hash:
                unit_revert_hash[cur_p].append(k)
            else:
                unit_revert_hash[cur_p] = [k]

not_run_items = []
del_items = []
replace_hash = {}
for k,same_list in unit_hash.items():
    if k in not_run_items:
        continue
    for same in same_list:
        if k in unit_revert_hash[same]: # avoid A->B B->A case
            not_run_items.append(same)
        new_grammar_dict[k] += new_grammar_dict[same]
        if same != start_sym:
            del_items.append(same)
        replace_hash[same] = k
    new_grammar_dict[k] = list(set(new_grammar_dict[k]))

unit_grammar_dict = {}
for k,p in new_grammar_dict.items():
    if k not in del_items:
        unit_grammar_dict[k] = []
        for ind in range(0, len(p)):
            cur_p = p[ind]
            for cur_ind in range(0, len(p[ind])):
                if cur_p[cur_ind] in replace_hash:
                    p[ind] = cur_p[0:cur_ind]+replace_hash[cur_p[cur_ind]]+cur_p[(cur_ind+1):]
                    cur_p = p[ind]
        for item in p:
            if item not in unterm_syms:
                unit_grammar_dict[k].append(item)

print("CNF: "+str(unit_grammar_dict))