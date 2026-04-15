import feedparser
import random
import time

# A pool of public Nitter instances (open-source Twitter frontends)
# These instances sometimes go down, so having a pool increases reliability
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.cz",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.moomoo.me",
    "https://nitter.unixfox.eu"
]

def get_recent_tweets(handle, max_retries=3):
    """
    Fetches the most recent tweets for a given handle using a public Nitter RSS feed.
    This avoids X API keys but relies on instance uptime.
    """
    for attempt in range(max_retries):
        instance = random.choice(NITTER_INSTANCES)
        rss_url = f"{instance}/{handle}/rss"
        
        try:
            feed = feedparser.parse(rss_url)
            
            # If the feed parsed successfully and has entries, process them
            if feed.entries:
                tweets = []
                for entry in feed.entries:
                    # Nitter RSS entry contents
                    # entry.title: Contains the physical tweet text
                    # entry.published: Publication date/time
                    # entry.link: URL to the tweet
                    
                    tweet_id = entry.link.split('/')[-1]
                    if '#' in tweet_id:
                         tweet_id = tweet_id.split('#')[0]
                         
                    tweet_data = {
                        "id": tweet_id,
                        "text": entry.title,
                        "author": handle,
                        "published": getattr(entry, 'published', ''),
                        "url": entry.link.replace(instance, "https://twitter.com") # convert back to X url
                    }
                    tweets.append(tweet_data)
                    
                return tweets
                
        except Exception as e:
            # Silently catch the error and retry on a new instance
            pass
            
        # Optional: Add a brief delay before retrying
        time.sleep(1)
        
    return [] # Failed all retries
