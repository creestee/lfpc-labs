# Defining &epsilon
epsilon = 'empty'

# Non-terminal symbols
vn = ['S', 'A', 'B', 'C', 'D']

# Terminal symbols
vt = ['a', 'b']

# Production rules
p = [
    "S -> aB",
    "S -> DA",
    "A -> a",
    "A -> BD",
    "A -> bDAB",
    "B -> b",
    "B -> BA",
    "D -> #{epsilon}",
    "D -> BA",
    "C -> BA"
]

class Grammar
    def initialize(vn, vt, p)
        @vn = vn
        @vt = vt
        @p = p
        @p_hash = {}
    end

    def productions_to_hash
        for key in @vn do
            @p_hash[key[0]] = []
        end
        for rule in @p do
            if @p_hash.key?(rule[0])
                @p_hash[rule[0]].append(rule.partition('-> ').last)
            end
        end
        @p_hash
    end

    def get_hash
        productions_to_hash()
        @p_hash
    end

    def convert_to_cnf
        productions_to_hash()
        
        # If the start symbol S occurs on some right side, create a new start symbol S0 and a new production S0 -> S
        for key, value in @p_hash do
            if value == 'S'
                @p_hash['S0'] = ['S']
                break
            end
        end

        # Removal of null productions

        # Finding out nullable non-terminal variables which derive epsilon
        nullable_variables = []
        
        for key, value in @p_hash do
            if value.include?('empty')
                nullable_variables.append(key)
            end
        end

        for key, value in @p_hash do
            for derivation in value do
                for null_var in nullable_variables
                    aux_string = derivation
                    if derivation.include?(null_var) and derivation == derivation.upcase()
                        aux_string = aux_string.sub(null_var, '')
                    end
                    if aux_string == ''
                        nullable_variables.append(key)
                    end
                end
            end
        end

        for key, value in @p_hash do
            for null_var in nullable_variables do
                puts "#{key} : #{value}"
            end
        end

        nullable_variables
    end
end

grammar = Grammar.new(vn, vt, p)
grammar.convert_to_cnf()
grammar.get_hash()