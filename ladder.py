import requests
import pickle
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
import networkx as nx

# globals
words = {}
matches = defaultdict(set)
neighbors = defaultdict(set)

def main():
    init()

    test_cases = [
        ('loner', 'loner'),
        ('peace', 'plate'),
        ('large', 'small'),
        ('chick', 'hatch'),
        ('apple', 'maple'),
        ('homer', 'marge'),
        ('alone', 'humph'),
        ('trump', 'biden'),
        ('alpha', 'omega'),
        ('fruit', 'punch'),
        ('forte', 'piano'),
        ('salty', 'peppy'),
        ('crown', 'royal'),
        ('sleep', 'never'),
        ('bathe', 'amigo'),
    ]

    for case in test_cases:
        start, end = case
        print(f'From {start} to {end}:')
        if start not in words:
            print(f"'{start}' is not a legal word'")
        if end not in words:
            print(f"'{end} is not a legal word")
        ladder = solve(start, end)

        if not ladder:
            print(' --- no ladder found ---')
        else:
            step = 1
            for word in ladder:
                print(f'{step:4}  {word}')
                step += 1
        print()

def init():
    global words, matches, neighbors

    filename = 'common_words_5_letter.txt'
    try:
        with open(filename, 'rb') as in_file:
            word_list = pickle.load(in_file)
            print(f'Successfully read {len(word_list)} words from {filename}')
    except FileNotFoundError:
        response = requests.get("https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt")
        assert response.status_code == 200
        word_list = response.text.split('\n')
        del word_list[-1] # omit trailing empty line 

        with open(filename, 'wb') as out_file:
            pickle.dump(word_list, out_file)
            print(f'Successfully wrote {len(word_list)} words to {filename}')

    word_list.append('biden')
    words = set(filter(legal, word_list))
    
    for word in words:
        for pattern in [word[:i] + '*' + word[i+1:] for i in range(5)]:
            matches[pattern].add(word)

    for matching_words in matches.values():
        for this_word, that_word in combinations(matching_words, 2):
            neighbors[this_word].add(that_word) 
            neighbors[that_word].add(this_word) 

    # show_stats()

def solve(start, end):
    def search():
        nonlocal fwd, fwd_words, bwd_words, prev_word, next_word, nexus
        nexus = None
        next_wave = set()
        for word in fwd_words:
            for neighbor in neighbors[word]:
                if not prev_word[neighbor]:
                    prev_word[neighbor] = word
                    next_wave.add(neighbor)
                if next_word[neighbor]:
                    nexus = neighbor
                    return
        fwd_words = next_wave        

    def assemble_ladder():
        def suffix(word):
            def suf(word):
                while word != next_word[word]:
                    word = next_word[word]
                    yield word
            return [w for w in suf(word)]

        def prefix(word):
            def pre(word):
                while word != prev_word[word]:
                    word = prev_word[word]
                    yield word
            return [w for w in pre(word)][::-1]

        return prefix(nexus) + [nexus] + suffix(nexus) if nexus else []

    def reverse():
        nonlocal fwd, fwd_words, bwd_words, prev_word, next_word 
        fwd = not fwd 
        fwd_words, bwd_words = bwd_words, fwd_words
        prev_word, next_word = next_word, prev_word

    #
    # solve(start, end) 
    #
    fwd_words, bwd_words = {start}, {end}
    prev_word, next_word = defaultdict(str), defaultdict(str)
    prev_word[start] = start    # pointer to self marks end-of-list
    next_word[end]   = end      # ditto 

    fwd = True      # we arbitrarily choose forward as the initial direction 
    nexus = None    # if we can find a nexus, we can build the shortest ladder 
 
    # alternately search forward from start and backward from end
    while not nexus and fwd_words and bwd_words:
        search()
        reverse()

    # normalize direction
    if not fwd:
        reverse()

    # return results
    ladder = assemble_ladder()
    return ladder
            
def legal(word):
    result = True  # initial assumption
    if len(word) != 5:
        result = False
    elif word[-1] == 's':
        result = False
    elif word in ['chine', 'merse', 'sedge', 'serge']:
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

def nx_main():
    init()

    G = nx.Graph()
    G.add_nodes_from(words)
    for word in words:
        for other_word in neighbors[word]:
            G.add_edge(word, other_word)

    start, end = 'bathe', 'amigo'
    print(f'From {start} to {end}:')
    for i, word in enumerate(nx.shortest_path(G, start, end)):
        print(f'{i+1:5}   {word}')
    print()
    
if __name__ == "__main__":
    # nx_main()
    main()

