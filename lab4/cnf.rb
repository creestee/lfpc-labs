require "set"

# Defining &epsilon
epsilon = "empty"

# Non-terminal symbols
vn = ["S", "A", "B", "C", "D"]

# Terminal symbols
vt = ["a", "b"]

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
]

class Grammar
  def initialize(vn, vt, p)
    @vn = vn
    @vt = vt
    @p = p
    @p_hash = {}
    @elimi_terms = []
    @elimi_unterms = {}
    @unterms_pool = ["E", "F", "G", "H", "I", "J", "K"]
    @unterms_used = 0
  end

  def productions_to_hash
    for key in @vn
      @p_hash[key[0]] = []
    end
    for rule in @p
      if @p_hash.key?(rule[0])
        @p_hash[rule[0]].append(rule.partition("-> ").last)
      end
    end
    @p_hash
  end

  def eliminate_epsilon()
    # If the start symbol S occurs on some right side, create a new start symbol S0 and a new production S0 -> S
    for key, value in @p_hash
      if value == "S"
        @p_hash["S0"] = ["S"]
        break
      end
    end

    # Removal of null productions

    # Finding out nullable non-terminal variables which derive epsilon
    nullable_variables = []

    for key, value in @p_hash
      if value.include?("empty")
        nullable_variables.append(key)
      end
    end

    for key, value in @p_hash
      for derivation in value
        upd_string = derivation
        for null_var in nullable_variables
          if upd_string.include?(null_var) and upd_string == upd_string.upcase()
            upd_string = upd_string.sub(null_var, "")
          end
          if upd_string == "" and !nullable_variables.include?(key)
            nullable_variables.append(key)
          end
        end
      end
    end

    for key, value in @p_hash
      for symbol in nullable_variables
        temp = value
        while temp.include?(symbol)
          temp = temp.tr(symbol, "")
          @p_hash[key] = temp
        end
      end
    end

    flag = false
    for key, value in @p_hash
      if value.length == 0
        @p_hash[key] = "empty"
        flag = true
      end
    end

    if flag
      eliminate_epsilon()
    end
  end

  def eliminate_terminals
    elimi_terms = []
    @p_hash.each do |k, p|
      p.each do |item|
        if item != "empty"
          if item.length > 1
            item.length.times do |ind|
              if @vt.include?(item[ind]) && !elimi_terms.include?(item[ind])
                elimi_terms.append(item[ind])
              end
            end
          end
        end
      end
    end
    @elimi_terms = elimi_terms
    elimi_terms
  end

  def eliminate_unterminals_split(v, len)
    half = len / 2
    pre_half = v[0...half]
    post_half = v[half..-1]
    [pre_half, post_half]
  end

  def eliminate_unterminals_internal(base_hash, tmp_hash)
    tmp_tmp_hash = tmp_hash.dup
    tmp_hash.each do |k, v|
      if v[0].length > 2
        unless base_hash.has_key?(v[0])
          base_hash[v[0]] = eliminate_unterminals_split(v[0], v[0].length)
          tmp_tmp_hash[v[0]] = base_hash[v[0]]
          eliminate_unterminals_internal(base_hash, tmp_tmp_hash)
        end
      end
      if v[1].length > 2
        unless hash.has_key?(v[1])
          base_hash[v[1]] = eliminate_unterminals_split(v[1], v[1].length)
          tmp_tmp_hash[v[1]] = base_hash[v[1]]
          eliminate_unterminals_internal(base_hash, tmp_tmp_hash)
        end
      end
    end
  end

  def eliminate_unterminals
    elimi_unterms = {}
    @p_hash.each do |k, p|
      p.each do |item|
        if item != "empty"
          if item.length > 2
            elimi_unterms[item] = eliminate_unterminals_split(item, item.length)
          end
        end
      end
    end
    eliminate_unterminals_internal(elimi_unterms, elimi_unterms.dup)
    @elimi_unterms = elimi_unterms
  end

  def use_unterm_sym
    @unterms_used += 1
    @unterms_pool[@unterms_used - 1]
  end

  def convert_productions
    elimi_term_map = {}
    terms_used = @elimi_terms.length
    terms_used.times do |ind|
      elimi_term_map[@elimi_terms[ind]] = use_unterm_sym
    end
    elimi_unterm_map = {}
    convert_p = []
    @p_hash.each do |k, p|
      p.each do |item|
        unless @elimi_unterms.has_key?(item)
          convert_p.append([k, item])
        end
      end
    end
    unterm_sym_map = {}
    @elimi_unterms.each do |k, v|
      item = @p_hash.find { |l, r| r.include?(k) }
      if item.nil
        unless unterm_sym_map.has_key?(k)
          unterm_sym_map[k] = k.length > 1 ? use_unterm_sym : k
        end
        unless unterm_sym_map.has_key?(v[0])
          unterm_sym_map[v[0]] = v[0].length > 1 ? use_unterm_sym : v[0]
        end
        unless unterm_sym_map.has_key?(v[1])
          unterm_sym_map[v[1]] = v[1].length > 1 ? use_unterm_sym : v[1]
        end
        convert_p.append([unterm_sym_map[k], unterm_sym_map[v[0]] + unterm_sym_map[v[1]]])
      else
        unless unterm_sym_map.has_key?(v[0])
          unterm_sym_map[v[0]] = v[0].length > 1 ? use_unterm_sym : v[0]
        end
        unless unterm_sym_map.has_key?(v[1])
          unterm_sym_map[v[1]] = v[1].length > 1 ? use_unterm_sym : v[1]
        end
        convert_p.append([item[0], unterm_sym_map[v[0]] + unterm_sym_map[v[1]]])
      end
    end
    convert_p
  end
end

grammar = Grammar.new(vn, vt, p)
grammar.productions_to_hash()
grammar.eliminate_epsilon()
grammar.eliminate_unterminals()
grammar.eliminate_terminals()
grammar.convert_productions
