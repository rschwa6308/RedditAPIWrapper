# --- Example usage for aggregating usernames and saving to files --- #
from datetime import date, datetime, timedelta
import os

from PushshiftWrapper import search_submissions, search_comments
from Utilities import write_list_to_file, daterange


# Takes a subreddit name and a time_range
# Returns the set of usernames which submitted or commented (guaranteed distinct)
def get_usernames(subreddit, time_range, printing=True):
    query_kwargs = {
        'subreddits': [subreddit],
        'time_range': time_range,
        'fields': ['author']
    }
    submissions = search_submissions(**query_kwargs, printing=printing)
    comments = search_comments(**query_kwargs, printing=printing)

    submission_authors = [sub['author'] for sub in submissions]
    comment_authors = [com['author'] for com in comments]

    return set(submission_authors + comment_authors)


# Generate a formatted filename for the given subreddit and date
BASE_PATH = os.path.join(os.path.dirname(__file__), 'Usernames')
FILE_EXTENSION = 'txt'
def format_filename(subreddit, day):
    return os.path.join(BASE_PATH, subreddit, f'{day.isoformat()}.{FILE_EXTENSION}')


# Takes a subreddit name and a day (date object)
# Downloads the relevent usernames and saves them under 'Usernames/subreddit/YYY-MM-DD.txt'
def fetch_and_save_usernames(subreddit, day, skip_existing=True, printing=True):
    filename = format_filename(subreddit, day)
    if skip_existing and os.path.isfile(filename):
        return

    start_time = datetime.combine(day, datetime.min.time())     # 00:00:00
    stop_time = start_time + timedelta(days=1)

    names = get_usernames(subreddit, [start_time, stop_time], printing=printing)
    sorted_names = sorted(list(names))

    write_list_to_file(filename, sorted_names)


if __name__ == '__main__':
    subreddits = ['dubstep', 'metal', 'jazz', 'classicalmusic', 'trap', 'vaporwave', 'kpop', 'indieheads']
    days = list(daterange(date(2017, 1, 1), date.today()))
    for subreddit in subreddits:
        for day in days:
            print(f'Getting usernames from r/{subreddit} on {day}... ', end='', flush=True)
            fetch_and_save_usernames(subreddit, day, printing=False)
            print('Done.')
