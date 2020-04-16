import requests
from collections import Counter

def show_stats(legal_words, matches):
    tally = Counter()
    for match_str, words in matches.items():
        tally[len(words)] += 1

    max_length = max(tally.keys())
    print(f'Frequency of number of words matching a given match string:')
    print(f"{'n_words':>10s}{'frequency':>10s}")
    for n_words in range(1,max_length+1):
        print(f'{n_words:10}{tally[n_words]:10}')
    print()
    print(f'Longest match(es):\n')

    long_matches = [match_str for match_str, words in matches.items() if len(words) == max_length]
    for match in long_matches:
        print(f"   match string = '{match}'")
        i = 1
        for word in sorted(matches[match]):
            print(f"       word {i:2} =  '{word}'")
            i += 1
        print()

    for ms in matches.keys():
        if len(matches[ms]) == 4 and ms[0] != '*' and ms[-1] != '*':
            break
    print(f"matches[{ms}] = {matches[ms]}")
    print()

    print(f"neighbors['maple'] = {neighbors['maple']}")
    print(f"neighbors['apple'] = {neighbors['maple']}")
    print()
    
    
def legal(word):
    result = True  # initial assumption
    if len(word) != 5:
        result = False
    elif word[-1] == 's':
        result = False
    elif word in ['chine', 'marge', 'merse', 'sedge', 'serge']:
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
    
    ladder, nexus = None, None  # default
    try:
        while True:
            start_list = [w for w, d in start_distance.items() if d == distance]
            end_list = [w for w, d in end_distance.items() if d == distance]
            if start_list == [] and end_list == []:
                break
            
            for word in start_list:
                for w in neighbors[word]:
                    if w not in start_distance:
                        start_distance[w] = distance + 1
                    if w in end_distance:
                        raise StopIteration

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

legal_words = []
def init():
    global legal_words, neighbors

    response = requests.get("https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt")
    assert response.status_code == 200
    words = response.text.split('\n')
    del words[-1]
    words.append('biden')

    matches = {}
    legal_words = list(filter(legal, words))
    for word in legal_words:
        for i in range(5):
            pattern = word[:i] + '*' + word[i+1:]
            if pattern in matches:
                matches[pattern].append(word)
            else:
                matches[pattern] = [word]

    non_trivial_matches = { match: words for match, words in matches.items() if len(words) > 1 }
    neighbors = {word:set() for word in legal_words}
    for pattern, words in non_trivial_matches.items():
        L = len(words)
        for i in range(L-1): 
            for j in range(i+1, L):
                word1, word2 = words[i], words[j]
                neighbors[word1].add(word2) 
                neighbors[word2].add(word1) 

    show_stats(legal_words, matches)


def main():
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
    ]

    for case in test_cases:
        start, end = case
        ladder, nexus = solve(start, end)
        
        print(f'From {start} to {end} ')
        if start not in legal_words:
            print(f'{start} is not in the legal word list')
        if end not in legal_words:
            print(f'{end} is not in the legal word list')
 
        if ladder:
            step = 1
            for word in ladder:
                print(f'{step:4}  {word}  {"(nexus)" if word == nexus else ""}')
                step += 1
        else:
            print('No ladder found.')

        print()

if __name__ == "__main__":
    main()

