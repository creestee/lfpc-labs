# Graphic library for generating graphs
import graphviz

# Grammar input
Vn = ['S', 'B', 'D']
Vt = ["a", "b", "c"]
P = ["S=aB", "B=aD", "B=bB", "D=aD", "D=bS", "B=cS", "D=c"]

for i in range(len(P)):
    if P[i][-1].islower():

        # Add final state (node)
        P[i] = P[i] + 'Q' 

# Create Adjacency List of Finite Automaton
adjacency_list = {} 

for rr in P:
    if rr[0] not in adjacency_list.keys():

        # Create key (node) in adjacency list if it doesn't exist already
        adjacency_list[rr[0]] = []
    
    # Add edges for every node (weight, target) in an array form
    adjacency_list[rr[0]].append([rr[-2], rr[-1]])

print(adjacency_list)

# Generate graph of FA using graphviz library
fa = graphviz.Digraph('finite_automata', filename='fa')
fa.attr('node', shape='doublecircle')
fa.node('Q')

fa.attr('node', shape='circle')
for key in adjacency_list:
    for transition in adjacency_list[key]:
        fa.edge(key, transition[1], label=transition[0])

# fa.view() # Export in PDF format

# Function to check if an inserted string is accepted by FA or not 
def checkString(input_string, adj_list):
    
    # Start on initial node (starting symbol)
    node = 'S'
    
    # Iterate over every symbol in string
    for symbol in input_string:

        # Check if the first node is empty 
        if node == 'Q':
            return False

        # Iterate through weights and targets from adjacency list
        for weight, target in adj_list[node]:
            if symbol == weight:
                node = target
                break
            else:
                return False

    # Returns true or false if the last node is empty
    return node == 'Q'

string = input("Input a string : ")

print(checkString(string, adjacency_list))