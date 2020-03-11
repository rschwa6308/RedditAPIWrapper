# --- Utility functions for the PushshiftWrapper and assosciated scripts --- #
import requests
from time import sleep
import urllib
import json
import os
from datetime import date, datetime, timedelta


# Wrapper for requests.get; handles 'Too Many Requests' errors; returns response.json()
ATTEMPT_LIMIT = 5
BASE_SLEEP_DURATION_SECONDS = 0.35  # seems to be lower limit
def fetch_data(url, params={}, printing=True, attempt=0):
    if attempt > ATTEMPT_LIMIT:
        print('\nAttempt limit exceeded.')
        return None

    # encode url params while still allowing commas; this is unconventional but that's pushshift for ya :/
    encoded_params = [f'{k}={urllib.parse.quote(str(v), safe=",")}' for k, v in params.items()]
    combined_url = url + '&'.join(encoded_params)
    if printing: print(f'\nFetching data from \'{combined_url}\' ...')

    try:
        response = requests.get(combined_url)
    except Exception as e:
        print(f'Request failed critically; Error: {e}')
        return None
    
    if printing: print(f'Done. Status code: {response.status_code} ({response.reason}). Elapsed time: {round(response.elapsed.total_seconds(), 2)} seconds.')

    if response.ok:
        contents = response.json()
        return contents
    else:
        if response.status_code == 429:
            sleep_duration = BASE_SLEEP_DURATION_SECONDS * 2**attempt   # exponentially increase wait time with successive attempts
            if printing: print(f'Request failed; waiting {sleep_duration} seconds before trying again...')
            sleep(sleep_duration)
            return fetch_data(url, printing=printing, attempt=attempt+1)
        else:
            print('Request failed critically.')
            return None


# Given a set of arguments to the '/reddit/search/comment' endpoint, return a dictionary of url parameters
# For API documentation, see https://github.com/pushshift/api
def build_url_params(query=None, title_query=None, selftext_query=None, ids=None, count=None, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], num_comments_range=[None, None]):
    params = {}
    
    if query: params['q'] = query
    if title_query: params['title'] = title_query
    if selftext_query: params['selftext'] = selftext_query
    if ids: params['ids'] = ','.join(ids)
    if count: params['size'] = count
    if fields: params['fields'] = ','.join(fields)
    if sort_attribute: params['sort_type'] = sort_attribute
    if sort_rev: params['sort'] = 'desc'
    if authors: params['author'] = ','.join(authors)
    if subreddits: params['subreddit'] = ','.join(subreddits)

    if time_range[0]: params['after'] = int(time_range[0].timestamp())
    if time_range[1]: params['before'] = int(time_range[1].timestamp())

    score_params = []
    if score_range[0]: score_params.append(f'>{score_range[0] - 1}')
    if score_range[1]: score_params.append(f'<{score_range[1] + 1}')
    params['score'] = ','.join(score_params)

    num_comments_params = []
    if num_comments_range[0]: num_comments_params.append(f'>{num_comments_range[0] - 1}')
    if num_comments_range[1]: num_comments_params.append(f'<{num_comments_range[1] + 1}')
    params['num_comments'] = ','.join(num_comments_params)

    return {k: v for k, v in params.items() if v}


# Print a json object in an easily readable abbreviated form
def pretty_print(json_obj, indent=1, head_line_limit=20, tail_line_limit=5):
    lines = json.dumps(json_obj, indent=indent).split('\n')
    print()
    print('\n'.join(lines[:head_line_limit]))
    if head_line_limit + tail_line_limit < len(lines):
        print(' ' * (len(lines[head_line_limit + 1]) // 2) + '...')
        print('\n'.join(lines[-tail_line_limit:]))


# Return a generator of datetime.date objects
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


# Takes a filename (including the path) and a list of data
# Writes the data (seperated by newlines) to the specified location
def write_list_to_file(filename, data):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write('\n'.join(data))


# Takes a filename (including the path)
# Reads the data (seperated by newlines) and returns the contents as a list
def read_list_from_file(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()
