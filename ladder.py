import requests
from collections import Counter
from collections import defaultdict
from itertools import combinations

#import sys
#import numpy
#import scipy
#import pandas
#import matplotlib
#import pygraphviz  -- failed to install.  Says MSVC++ 14.0 is required;  I have 19.0 
#import pydot       #-- no runtime error, but intellisense says: "Unable to import 'pydot' "
#import pyyaml      -- seems to have installed, but runtime error "No module named 'pyyaml' " occurs 
#import gdal        -- failed to install.  Says MSVC++ 14.0 is required;  I have 19.0 
#import networkx as nx

words = {}
matches = defaultdict(list)
neighbors = defaultdict(set)

def main():
#    print(f'Testing NetworkX...')
#    nx.test()

    init()

    test_cases = [
        ('peace', 'plate'),
        ('large', 'small'),
        ('chick', 'hatch'),
        ('apple', 'maple'),
        ('homer', 'marge'),
        ('alone', 'adobe'),
        ('alone', 'humph'),
        ('trump', 'biden'),
        ('alpha', 'omega'),
        ('fruit', 'punch'),
        ('forte', 'piano'),
        ('salty', 'peppy'),
        ('sleep', 'never'),
        ('bathe', 'amigo'),
    ]

    for case in test_cases:
        start, end = case
        ladder, nexus = solve(start, end)
        
        print(f'From {start} to {end}:')
        if not ladder:
            print(' <no ladder found>')
        else:
            for i, word in enumerate(ladder):
                print(f'{i+1:4}  {word}  {"(nexus)" if word == nexus else ""}')
        print()

def init():
    global words, matches, neighbors

    response = requests.get("https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt")
    assert response.status_code == 200
    word_list = response.text.split('\n')
    del word_list[-1]
    word_list.append('biden')
    words = set(filter(legal, word_list))
    
    for word in words:
        for pattern in [word[:i] + '*' + word[i+1:] for i in range(5)]:
            matches[pattern].append(word)

    for matching_words in matches.values():
        for this_word, that_word in combinations(matching_words, 2):
            neighbors[this_word].add(that_word) 
            neighbors[that_word].add(this_word) 

    show_stats()

def solve(start, end):
    
    def grow(in_words, this_word, that_word):
        out_words = set()

        for word in in_words:
            for neighbor in neighbors[word]:
                if not this_word[neighbor]:
                    this_word[neighbor] = word
                    out_words.add(neighbor)
                if that_word[neighbor]:
                    return neighbor, out_words  # nexus found
        return None, out_words  # nexus not found

    def pre(word):
        while word:
            word = prev_word[word]
            if word:
                yield word

    def suf(word):
        while word:
            word = next_word[word]
            if word:
                yield word

    def prefix(word):
        l = [w for w in pre(word)]
        l.reverse()
        return l

    def suffix(word):
        return [w for w in suf(word)]
    
    def assemble_ladder():
        return prefix(nexus) + [nexus] + suffix(nexus) if nexus else None

    # solve() starts here
    fwd_words, bwd_words = {start}, {end}
    next_word, prev_word = defaultdict(str), defaultdict(str)

    fwd = True      # arbitrary initial direction forward
    while fwd_words and bwd_words:
        if fwd:
            nexus, fwd_words = grow(fwd_words, prev_word, next_word)
        else:
            nexus, bwd_words = grow(bwd_words, next_word, prev_word)
        if nexus:
            break
        fwd = not fwd  # go the other way

    prev_word[start], next_word[end] = None, None
    return assemble_ladder(), nexus
            
def legal(word):
    result = True  # initial assumption
    if len(word) != 5:
        result = False
    elif word[-1] == 's':
        result = False
    elif word in ['chine', 'merse', 'sedge', 'serge', 'marge']:
        result = False
    return result

def show_stats():
    print()
    print(f'number of legal words    = {len(words)    :6}')
    print(f'number of match groups   = {len(matches)  :6}')
    print()
    
    tally = Counter(map(len, matches.values()))
    max_length = max(tally.keys())
  
    match_count = 0
    for n_words in sorted(tally):
        print(f'{tally[n_words]:10} match groups contain {n_words:3} word{"s" if n_words != 1 else ""}')
        match_count += tally[n_words]
    print(f'{match_count:10} match groups in total\n')

    print(f'Longest match(es):\n')
    long_matches = [match_str for match_str, words in matches.items() if len(words) == max_length]
    for match in long_matches:
        print(f"   match string = '{match}'")
        i = 1
        for word in sorted(matches[match]):
            print(f"       word {i:2} =  '{word}'")
            i += 1
        print()

    tally = Counter(map(len, neighbors.values()))
    tally[0] = sum(map(lambda word:len(neighbors[word]) == 0, words))
    max_neighbors = max(tally.keys())

    neighbor_count = 0
    for n_neighbors in range(max_neighbors+1):
        print(f'{tally[n_neighbors]:10} words have {n_neighbors:3} neighbor{"s" if n_neighbors != 1 else ""}')
        neighbor_count += tally[n_neighbors]
    print(f'{neighbor_count:10} words in total\n')

    print(f'Largest group(s) of neighbors:\n')
    large_circles = [word for word, neighbors in neighbors.items() if len(neighbors) == max_neighbors]
    for word in large_circles:
        print(f"   word = '{word}'")
        i = 1
        for neighbor in sorted(neighbors[word]):
            print(f"       neighbor {i:2} =  '{neighbor}'")
            i += 1
        print()

    
    for ms in matches.keys():
        if len(matches[ms]) == 4 and ms[0] != '*' and ms[-1] != '*':
            break
    print(f"matches[{ms}] = {matches[ms]}")
    print()

    for word in ['maple', 'apple', 'alpha', 'omega', 'forte', 'piano', 'marge', 'merse', 'chine']:
        print(f'neighbors["{word}"] = {neighbors[word]}')
    print()

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
def longest_ladder():
    word_list = list(words)
    longest_ladder = []
    for i, start in enumerate(word_list[0:-1]):
        for end in word_list[i+1:]:
            nexus, ladder = solve(start, end)
            if len(ladder) > len(longest_ladder):
                longest_ladder = ladder
    return longest_ladder, nexus

if __name__ == "__main__":
    main()

