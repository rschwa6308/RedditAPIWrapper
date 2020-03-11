# Pushshift Wrapper Documentation
This library provides an intuitive interface for accessing the unoffical Reddit API graciously hosted by https://pushshift.io/. It includes functions for downloading arbitrarily large sets of comments and submissions subject to a number of search criteria.

If you intend to use this wrapper heavily, please consider [supporting](https://pushshift.io/donations/) the API's maintainers.

## Overview
The following functions access the https://api.pushshift.io/reddit/search/ endpoints and return the resulting JSON as a python dictionary.
- `search_submissions` fetches arbitrarily many submissions satisfying the search predicate
- `count_submissions` counts the number of submissions satisfying the search predicate
- `search_comments` fetches arbitrarily many comments satisfying the search predicate
- `count_comments` counts the number of comments satisfying the search predicate

## Search Parameters
A search predicate is specified by the arguments passed to the functions listed above. The following table describes their usage. For any ranged argument, using `None` as either endpoint will yield an unbounded interval.

| Argument | Data Type | Description |
| --- | --- | --- |
| `query` | string | search term |
| `title_query` | string | search term (title only) |
| `selftext_query` | string | search term (body only) |
| `ids` | string list | base-36 submission/comment ids |
| `count` | integer | desired number of results (< 10^5) |
| `fields` | string list | desired JSON fields in return data |
| `sort_attribute` | string | name of attribute to sort by |
| `sort_rev` | boolean | sort in reverse order (i.e. descending) |
| `authors` | string list | usernames of authors |
| `subreddits` | string list | names of subreddits |
| `time_range` | (datetime, datetime) | range of values for time created|
| `score_range` | (integer, integer) | range of values for score |
| `num_comments_range` | (integer, integer) | range of values for the number of commments (on a submission) |
| `printing` | boolean | print a progress log to the console |


## Notes
- All arguments are optional, but there are no guarantees regarding the behavior of an underspecified query.
- Some arguments (e.g. title_query, num_comments_range) can only be used in functions relating to submissions.
- The function `pretty_print` (from `Utilities.py`) prints a given dictionary in an easily readable abbreviated form.


## Examples
Complete example:
```python
from PushshiftWrapper import *
from datetime import datetime, timedelta

results = search_submissions(
    query='trump',
    subreddits=['politics'],
    fields=['author', 'score', 'title'],
    time_range=(datetime(2020, 2, 16), None),   # February 16th to present
    count=3000
)

if results:
    print(f'Found {len(results)} submissions.')
    pretty_print(results)
else:
    print('No results found.')  # some network error probably occurred
```

Re-use the same arguments over multiple calls:
```python
kwargs = {
    'query': 'trump',
    'score_range': [20, 30],
    'subreddits': ['factorio', 'politics']
}
comments = search_comments(**kwargs)
submissions = search_submissions(**kwargs, num_comments_range=[None, 100])
```

Manipulate datetime objects for constructing time ranges:
```python
start = datetime(2020, 2, 16)
stop = start + timedelta(days=1)    # datetime.timedelta object
results = search_submissions(
    query='trump',
    subreddits=['politics'],
    time_range=(start, stop)
)
```
