# --- Example usage for calculating word frequency within comments --- #
from PushshiftWrapper import *
from Utilities import pretty_print


def get_word_frequency(body_list):
    frequency = {}
    for body in body_list:
        for word in body.split(' '):
            if word in frequency:
                frequency[word] += 1
            else:
                frequency[word] = 1
    
    return frequency


if __name__ == '__main__':
    a = datetime(2020, 2, 10)
    b = a + timedelta(days=1)
    results = search_comments(
        count=2000,
        time_range=(a, b),
        subreddits=['the_donald', 'politics'],
        fields=['body'],
        printing=True
    )
    print(f'{len(results)} results found')
    pretty_print(results)
    freq = get_word_frequency(comment['body'] for comment in results)
    for k, v in sorted(freq.items(), key=lambda item: item[1], reverse=True)[:100]:
        print(f'{k} => {v}')
