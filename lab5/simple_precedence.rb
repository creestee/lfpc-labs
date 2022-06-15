require "pp"

input_grammar = {
  :N => ["S", "A", "B", "C"],
  :T => ["a", "b", "c", "d", "e", "f"],
  :P => [["S", "Bc"],
         ["S", "BcdC"],
         ["C", "Ae"],
         ["A", "f"],
         ["A", "Abf"],
         ["B", "a"],
         ["B", "Bba"]],
}
input_language = "abacdfbfe"
input_start_sym = "S"

grammar = input_grammar

fr = {}
first = {}
lt = {}
last = {}

loop do
  grammar[:N].each do |item|
    fr[item] ||= []
    lt[item] ||= []
    first[item] = fr[item].dup
    last[item] = lt[item].dup
  end

  grammar[:P].each do |item|
    x = item[0]
    fr_item = item[1][0]
    lt_item = item[1][-1]
    fr[x].push(fr_item)
    lt[x].push(lt_item)
    fr_res = fr[fr_item]
    fr[x].push(*fr_res) unless fr_res.nil?
    lt_res = lt[lt_item]
    lt[x].push(*lt_res) unless lt_res.nil?
    fr[x] = fr[x].uniq # set
    lt[x] = lt[x].uniq
  end

  break if fr == first && lt == last
end

puts "FIRST:"
pp(first)
puts ""

puts "LAST:"
pp(last)
puts ""

relations = []
grammar[:P].each do |item|
  p = item[1]
  len = p.length
  if len >= 2
    (len - 1).times do |ind|
      x1 = p[ind]
      x2 = p[ind + 1]
      relations.push([x1, x2, "="])
      if grammar[:N].include?(x2)
        first[x2].each do |x2_|
          relations.push([x1, x2_, "<"])
        end
      end
      if grammar[:N].include?(x1)
        if grammar[:T].include?(x2)
          last[x1].each do |x1_|
            relations.push([x1_, x2, ">"])
          end
        elsif grammar[:N].include?(x2)
          last[x1].each do |x1_|
            first[x2].each do |x2_|
              relations.push([x1_, x2_, ">"]) if grammar[:T].include?(x2_)
            end
          end
        end
      end
    end
  end
end

relation_hash = {}

relations.each do |item|
  x1 = item[0]
  x2 = item[1]
  relation = item[2]
  relation_hash[x1] ||= {}
  if relation_hash[x1][x2].nil?
    relation_hash[x1][x2] = relation
  else
    if relation == "="
      relation_hash[x1][x2] = relation if relation_hash[x1][x2] != "="
    elsif relation_hash[x1][x2] == "="
      relation_hash[x1][x2] = relation + relation_hash[x1][x2]
    elsif relation_hash[x1][x2].include?(relation)
    elsif relation_hash[x1][x2] == relation
    else
      puts "FATAL ERROR!"
    end
  end
end

puts "RELATIONS:"
relation_hash.each do |item|
  item[1].each_pair { |key, value| puts "#{item[0]} #{value} #{key}" }
end

def dump_relation(relations, grammar)
  token = (grammar[:N] + grammar[:T])
  puts " " * 5 + token.join(" " * 3)
  token.each do |item|
    r = relations[item]
    row = token.collect do |k| # each element, dup array
      v = r.nil? ? nil : r[k]
      if v.nil?
        "  "
      elsif v.length == 1
        " #{v}"
      else
        v
      end
    end
    puts [" #{item}", *row].join("  ")
  end
end

def finished?(stack, start_sym)
  stack.join("").gsub("<", "") == "$#{start_sym}"
end

def get_relation(relation_hash, x1, x2)
  if x1 == "$"
    "<"
  elsif x2 == "$"
    ">"
  else
    # puts "x1=#{x1}, x2=#{x2}"
    relation_hash[x1][x2]
  end
end

# 2. Parsing

def parse(grammar, relation_hash, input, start_sym)
  result = true
  history = []

  stack = ["$"]
  input = input + "$"
  cursor = input.length - 2
  while !(input[cursor] == "$" && finished?(stack, start_sym))
    top = stack[0]
    next_token = input[cursor]
    obj = {
      :stack => stack.dup,
      :input => input[0..cursor],
    }
    rel = get_relation(relation_hash, next_token, top)
    obj[:precedence] = rel
    history.push(obj)
    if rel == ">" || rel == "=" || rel == "=>" || rel.nil?
      # Shift
      obj[:action] = "SHIFT"
      stack.insert(0, rel[0])
      stack.insert(0, input[cursor])
      cursor -= 1
    elsif rel == "<"
      #     # Reduce
      start = 0
      while (stack[start + 1] != ">")
        start += 1
      end
      exp = stack[0..start].join("").gsub("=", "")
      f = grammar[:P].find do |item|
        item[1] == exp
      end
      if f.nil?
        result = false
        obj[:action] = "REJECT"
        break
      end
      obj[:action] = "REDUCE (#{f[0]} -> #{f[1]})"
      red_rel = get_relation(relation_hash, f[0], stack[2])
      stack = [f[0], red_rel, *stack[2..-1]]
      pp(stack)
    end
  end
  if result
    history.push({
                   :stack => stack.dup,
                   :input => input[0..cursor],
                   :precedence => get_relation(relation_hash, stack[-1], input[cursor]),
                   :action => "ACCEPT",
                 })
  end
  [result, history]
end

def dump_parse_result(result, history)
  # determine column length
  title = ["STACK", "PRECEDENCE", "INPUT", "ACTION"]
  width = title.collect { |item| item.length }
  paddings = []
  history.each do |item|
    stack_len = item[:stack].join("").length
    width[0] = stack_len if stack_len > width[0]
    prece_len = item[:precedence].length
    width[1] = prece_len if prece_len > width[1]
    input_len = item[:input].length
    width[2] = input_len if input_len > width[2]
    action_len = item[:action].length
    width[3] = action_len if action_len > width[3]
  end

  title_row = []
  title.length.times do |ind|
    title_row.push(title[ind] + (" " * (width[ind] - title[ind].length)))
  end

  prece_row = []
  history.length.times do |ind|
    prece_row.push(
      [history[ind][:stack].join("") + (" " * (width[0] - history[ind][:stack].join("").length)),
       history[ind][:precedence] + (" " * (width[1] - history[ind][:precedence].length)),
       history[ind][:input] + (" " * (width[2] - history[ind][:input].length)),
       history[ind][:action] + (" " * (width[3] - history[ind][:action].length))]
    )
  end

  puts title_row.join(" ")
  prece_row.collect do |row|
    puts row.join(" ")
  end
end

puts ""
puts "Matrix of precedence relations:"
dump_relation(relation_hash, grammar)
puts ""

puts "Analysis table:"
result, hist = parse(grammar, relation_hash, input_language, input_start_sym)
dump_parse_result(result, hist)
