# --- Wrapper functions for accessing the pushshift.io Reddit API --- #
from datetime import datetime, timedelta
import concurrent.futures

from RedditAPIWrapper.Utilities import fetch_data, build_url_params


# API-related Constants
NUM_RESULTS_PER_CALL = 1000     # limit set by API on max number of results returned per call
NUM_RESULTS_LIMIT = 10**5       # sanity limit to help avoid never-ending recursions


# Access the '/reddit/search/submissions' endpoint once to fetch submission data
# num_results <= min(count, NUM_RESULTS_PER_CALL)
def search_submissions_base(query=None, title_query=None, selftext_query=None, ids=None, count=None, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], num_comments_range=[None, None], printing=True):
    base_url = 'https://api.pushshift.io/reddit/search/submission/?'
    params = build_url_params(query=query, title_query=title_query, selftext_query=selftext_query, ids=ids, count=count, fields=fields, sort_attribute=sort_attribute, sort_rev=sort_rev, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range, num_comments_range=num_comments_range)
    results = fetch_data(base_url, params=params, printing=printing)['data']
    return results


# Access the '/reddit/search/comment' endpoint once to fetch comment data
# num_results <= min(count, NUM_RESULTS_PER_CALL)
def search_comments_base(query=None, ids=None, count=None, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], printing=True):
    base_url = 'https://api.pushshift.io/reddit/search/comment/?'
    params = build_url_params(query=query, ids=ids, count=count, fields=fields, sort_attribute=sort_attribute, sort_rev=sort_rev, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range)
    results = fetch_data(base_url, params=params, printing=printing)['data']
    return results


# Access the '/reddit/search/submission' endpoint repeatedly to fetch submission data (num_results <= count < +inf)
# Bisects time range and recursively searches the left half (and then the right half if necessary)
# Concatenates the results (respects sorting)
#   use None as count for unlimited results
#   use None as endpoints of ranged attributes for unbounded
def search_submissions(query=None, title_query=None, selftext_query=None, ids=None, count=None, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], num_comments_range=[None, None], printing=True):
    if count is None: count = NUM_RESULTS_LIMIT
    else: count = min(count, NUM_RESULTS_LIMIT)

    time_range, score_range, num_comments_range = list(time_range), list(score_range), list(num_comments_range)
    if time_range[0] is None: time_range[0] = datetime(2005, 12, 1)     # approximate start date of data set
    if time_range[1] is None: time_range[1] = datetime.today()

    kwargs = {'query': query, 'title_query': title_query, 'selftext_query': selftext_query, 'ids': ids, 'count': count, 'fields': fields, 'sort_attribute': sort_attribute, 'sort_rev': sort_rev, 'authors': authors, 'subreddits': subreddits, 'time_range': time_range, 'score_range': score_range, 'num_comments_range': num_comments_range, 'printing': printing}

    if count <= NUM_RESULTS_PER_CALL:
        return search_submissions_base(**kwargs)
    
    return search_submissions_helper(**kwargs)


# Access the '/reddit/search/comment' endpoint repeatedly to fetch comment data (num_results <= count < +inf)
# Bisects time range and recursively searches the left half (and then the right half if necessary)
# Concatenates the results (respects sorting)
#   use None as count for unlimited results
#   use None as endpoints of ranged attributes for unbounded
def search_comments(query=None, ids=None, count=None, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], printing=True):
    if count is None: count = NUM_RESULTS_LIMIT
    else: count = min(count, NUM_RESULTS_LIMIT)
    
    time_range, score_range = list(time_range), list(score_range)
    if time_range[0] is None: time_range[0] = datetime(2005, 12, 1)     # approximate start date of data set
    if time_range[1] is None: time_range[1] = datetime.today()

    kwargs = {'query': query, 'ids': ids, 'count': count, 'fields': fields, 'sort_attribute': sort_attribute, 'sort_rev': sort_rev, 'authors': authors, 'subreddits': subreddits, 'time_range': time_range, 'score_range': score_range, 'printing': printing}

    if count <= NUM_RESULTS_PER_CALL:
        return search_comments_base(**kwargs)
    
    return search_comments_helper(**kwargs)


# Helper function for search_submissions
def search_submissions_helper(query=None, title_query=None, selftext_query=None, ids=None, count=None, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], num_comments_range=[None, None], printing=True):
    num_results = count_submissions(query=query, title_query=title_query, selftext_query=selftext_query, ids=ids, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range, num_comments_range=num_comments_range, printing=printing)

    if num_results == 0: return []
    
    kwargs = {'query': query, 'title_query': title_query, 'selftext_query': selftext_query, 'ids': ids, 'fields': fields, 'sort_attribute': sort_attribute, 'sort_rev': sort_rev, 'authors': authors, 'subreddits': subreddits, 'score_range': score_range, 'num_comments_range': num_comments_range, 'printing': printing}
    
    if num_results > NUM_RESULTS_PER_CALL:
        if printing: print(f'\nSubmissions found: {num_results}. Bisecting time range...')
        a, b = time_range
        midpoint = a + (b - a) / 2
        left_results = search_submissions_helper(**kwargs, count=count, time_range=[a, midpoint])
        remaining = count - len(left_results)
        if remaining > 0:
            right_results = search_submissions_helper(**kwargs, count=remaining, time_range=[midpoint, b])
        else:
            right_results = []
        return left_results + right_results
    else:
        if printing: print(f'\nDownloading {min(count, num_results)} submissions now...')
        return search_submissions_base(**kwargs, count=count, time_range=time_range)


# Helper function for search_comments
def search_comments_helper(query=None, ids=None, count=None, fields=None, sort_attribute=None, sort_rev=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], printing=True):
    num_results = count_comments(query=query, ids=ids, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range, printing=printing)

    if num_results == 0: return []
    
    kwargs = {'query': query, 'ids': ids, 'fields': fields, 'sort_attribute': sort_attribute, 'sort_rev': sort_rev, 'authors': authors, 'subreddits': subreddits, 'score_range': score_range, 'printing': printing}
    
    if num_results > NUM_RESULTS_PER_CALL:
        if printing: print(f'\nComments found: {num_results}. Bisecting time range...')
        a, b = time_range
        midpoint = a + (b - a) / 2
        left_results = search_comments_helper(**kwargs, count=count, time_range=[a, midpoint])
        remaining = count - len(left_results)
        if remaining > 0:
            right_results = search_comments_helper(**kwargs, count=remaining, time_range=[midpoint, b])
        else:
            right_results = []
        return left_results + right_results
    else:
        if printing: print(f'\nDownloading {min(count, num_results)} comments now...')
        return search_comments_base(**kwargs, count=count, time_range=time_range)


# Count the number of submissions satisfying the search predicate; slight abuse of the aggregation feature
# Note: Only use for time periods > 1 day. If < 1 day, use the aggregation feature for batched results
def count_submissions(query=None, title_query=None, selftext_query=None, ids=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], num_comments_range=[None, None], printing=True):
    base_url = 'https://api.pushshift.io/reddit/search/submission/?'
    params = build_url_params(query=query, title_query=title_query, selftext_query=selftext_query, ids=ids, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range, num_comments_range=num_comments_range)
    if False: # query:   # look in metadata for total number of results (TODO: fix metadata issue)
        params['size'], params['metadata'] = 0, True
        results = fetch_data(base_url, params=params, printing=printing)['metadata']['total_results']
        return results
    else:       # abuse the aggregation feature to sum results over time range
        params['aggs'], params['frequency'] = 'created_utc', 'month'
        results = fetch_data(base_url, params=params, printing=printing)
        try:
            items = results['aggs']['created_utc']
            total = sum(month['doc_count'] for month in items)
        except Exception as e:
            total = 0
            if printing: print(f'EXCEPTION: {e}')
        return total


# Count the number of comments satisfying the search predicate; slight abuse of the aggregation feature
# Note: Only use for time periods > 1 day. If < 1 day, use the aggregation feature for batched results
def count_comments(query=None, ids=None, authors=None, subreddits=None, time_range=[None, None], score_range=[None, None], printing=True):
    base_url = 'https://api.pushshift.io/reddit/search/comment/?'
    params = build_url_params(query=query, ids=ids, authors=authors, subreddits=subreddits, time_range=time_range, score_range=score_range)
    if False: # query:   # look in metadata for total number of results (TODO: fix metadata issue)
        params['size'], params['metadata'] = 0, True
        results = fetch_data(base_url, params=params, printing=printing)['metadata']['total_results']
        return results
    else:       # abuse the aggregation feature to sum results over time range
        params['aggs'], params['frequency'] = 'created_utc', 'month'
        results = fetch_data(base_url, params=params, printing=printing)
        try:
            items = results['aggs']['created_utc']
            total = sum(month['doc_count'] for month in items)
        except:
            total = 0
        return total
