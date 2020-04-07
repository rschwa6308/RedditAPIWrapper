from Main import *
from Utilities import pretty_print, daterange

from datetime import date, datetime, timedelta
from random import shuffle


MIN_SAMPLES = 10    # minimum number of unique days sampled

# Sample submissions uniformly over the given time range
def sample_submissions(query=None, title_query=None, selftext_query=None, ids=None, count=1000, fields=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], num_comments_range=[None, None], printing=True):
    base_url = 'https://api.pushshift.io/reddit/search/submission/?'
    params = build_url_params(query=query, title_query=title_query, selftext_query=selftext_query, ids=ids, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range, num_comments_range=num_comments_range)
    params['aggs'], params['frequency'] = 'created_utc', 'day'
    agg_results = fetch_data(base_url, params=params, printing=printing)['aggs']['created_utc']

    start_date = date.fromtimestamp(agg_results[0]['key'])
    end_date = date.fromtimestamp(agg_results[-1]['key'])

    days = list(daterange(start_date, end_date))
    shuffle(days)
    pos = 0

    max_res_per_sample = count // MIN_SAMPLES
    results = []
    while len(results) < count:
        day = days[pos]
        print(f'\nSampling submissions from {day.isoformat()}')
        start_time = datetime.combine(day, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        results += search_submissions(
            query=query, title_query=title_query, selftext_query=selftext_query, ids=ids, count=max_res_per_sample, fields=fields, authors=authors, subreddits=subreddits, time_range=[start_time, end_time], score_range=score_range, num_comments_range=num_comments_range, printing=printing
        )
        pos += 1

    return results[:count]

# Sample comments uniformly from the given time range
def sample_comments(query=None, ids=None, count=1000, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], printing=True):
    base_url = 'https://api.pushshift.io/reddit/search/comment/?'
    params = build_url_params(query=query, ids=ids, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range)
    params['aggs'], params['frequency'] = 'created_utc', 'day'
    agg_results = fetch_data(base_url, params=params, printing=printing)['aggs']['created_utc']

    start_date = date.fromtimestamp(agg_results[0]['key'])
    end_date = date.fromtimestamp(agg_results[-1]['key'])

    days = list(daterange(start_date, end_date))
    shuffle(days)
    pos = 0

    max_res_per_sample = count // MIN_SAMPLES
    results = []
    while len(results) < count:
        day = days[pos]
        print(f'\nSampling comments from {day.isoformat()}')
        start_time = datetime.combine(day, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        results += search_comments(
            query=query, ids=ids, count=max_res_per_sample, fields=fields, authors=authors, subreddits=subreddits, time_range=[start_time, end_time], score_range=score_range, printing=printing
        )
        pos += 1

    return results[:count]


if __name__ == '__main__':
    res = sample_comments(
        subreddits=['askscience'],
        count=15000,
        printing=True
    )
    print(len(res))
    pretty_print(res, head_line_limit=50)
