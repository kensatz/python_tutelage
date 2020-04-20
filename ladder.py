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

def show_stats():
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
    
def legal(word):
    result = True  # initial assumption
    if len(word) != 5:
        result = False
    elif word[-1] == 's':
        result = False
    elif word in ['chine', 'merse', 'sedge', 'serge', 'marge']:
        result = False
    return result

def assemble_ladder(start, nexus, end, start_dist, end_dist):
    ladder = [nexus]
    word = nexus
    dist = start_dist[nexus]
    while (dist):
        for neighbor in neighbors[word]:
            if neighbor in start_dist:
                sd = start_dist[neighbor]
                if sd == dist - 1:
                    ladder = [neighbor] + ladder
                    word, dist = neighbor, sd
                    break
        assert dist == sd

    word = nexus
    dist = end_dist[nexus]
    while (dist):
        for neighbor in neighbors[word]:
            if neighbor in end_dist:
                ed = end_dist[neighbor]
                if ed == dist - 1:
                    ladder = ladder + [neighbor]  # ladder += [neighbor]
                    word, dist = neighbor, ed
                    break
        assert dist == ed

    return ladder

def solve(start, end):
    distance = 0
    start_distance = {start: distance}
    end_distance = {end: distance}
    
    ladder, nexus = [], None  # default
    try:
        while True:
            start_list = [w for w, d in start_distance.items() if d == distance]
            if start_list == []:
                break

            for word in start_list:
                for w in neighbors[word]:
                    if w not in start_distance:
                        start_distance[w] = distance + 1
                    if w in end_distance:
                        raise StopIteration

            end_list = [w for w, d in end_distance.items() if d == distance]
            if end_list == []:
                break
            
            for word in end_list:
                for w in neighbors[word]:
                    if w not in end_distance:
                        end_distance[w] = distance + 1
                    if w in start_distance:
                        raise StopIteration
            
            distance += 1

    except StopIteration:
        nexus = w
        ladder = assemble_ladder(start, nexus, end, start_distance, end_distance)

    finally:
        return ladder, nexus

words = {}
neighbors = defaultdict(set)
matches = defaultdict(list)
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

    print()
    print(f'number of original words = {len(word_list):6}')
    print(f'number of legal words    = {len(words)    :6}')
    print(f'number of match groups   = {len(matches)  :6}')
    print()
    
    # show_stats()

def main():

#    print(f'Testing NetworkX...')
#    nx.test()

    init()

    test_cases = [
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
        
        print(f'From {start} to {end} ')
        if start not in words:
            print(f' <{start} is not in the legal word list>')
        if end not in words:
            print(f' <{end} is not in the legal word list>')
 
        if ladder:
            step = 1
            for word in ladder:
                print(f'{step:4}  {word}  {"(nexus)" if word == nexus else ""}')
                step += 1
        else:
            print(' <no ladder found>')

        print()


if __name__ == "__main__":
    main()

def longest_ladder():
    word_list = list(words)
    longest_ladder = []
    for i, start in enumerate(word_list[0:-1]):
        for end in word_list[i+1:]:
            ladder, nexus = solve(start, end)
            if len(ladder) > len(longest_ladder):
                longest_ladder = ladder
    return longest_ladder, nexus