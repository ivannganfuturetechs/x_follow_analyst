import os
import json
import time
from dotenv import load_dotenv

from scraper import get_recent_tweets
from database import get_session, Tweet, EngagementSnapshot

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS_FILE = os.path.join(BASE_DIR, "config", "targets.json")

def load_targets():
    """Loads the list of X handles to monitor."""
    with open(TARGETS_FILE, "r") as f:
        return json.load(f)

def monitor_loop():
    """Main loop to poll targets, analyze engagement, and send alerts."""
    targets = load_targets()
    print(f"Starting monitoring for {len(targets)} targets...")
    
    interval = int(os.getenv("POLLING_INTERVAL_MINUTES", 120)) * 60
    db_session = get_session()
    
    while True:
        for target in targets:
            handle = target['handle']
            baseline_views = target.get('baseline_views', 100000)
            print(f"Checking updates for @{handle}...")
            
            try:
                # 1. Fetch latest tweets (via Nitter RSS Scraper)
                recent_tweets = get_recent_tweets(handle)
                
                if recent_tweets:
                    print(f"    --> Found {len(recent_tweets)} recent tweets.")
                    
                    for t_data in recent_tweets:
                        # 2. Store / Update Database
                        tweet = db_session.query(Tweet).filter_by(id=t_data['id']).first()
                        
                        is_new_tweet = False
                        if not tweet:
                            # New tweet logic
                            tweet = Tweet(
                                id=t_data['id'],
                                handle=t_data['author'],
                                text=t_data['text'],
                                published_at=t_data['published']
                            )
                            db_session.add(tweet)
                            is_new_tweet = True
                        
                        # Add engagement snapshot
                        # Note: Nitter RSS doesn't provide these natively (defaults to 0)
                        # We capture them cleanly here so we can inject them when we switch
                        # to an alternative scraper like Apify or Playwright.
                        views = t_data.get('views', 0)
                        retweets = t_data.get('retweets', 0)
                        likes = t_data.get('likes', 0)
                        
                        snapshot = EngagementSnapshot(
                            tweet_id=tweet.id,
                            views=views,
                            retweets=retweets,
                            likes=likes
                        )
                        db_session.add(snapshot)
                        
                        # 3. Trigger LLM analysis for ANY new tweet (since Nitter lacks view counts, we analyze all new entries)
                        if is_new_tweet:
                            print(f"    [NEW TWEET] Triggering LLM analysis for {tweet.id}...")
                            
                            from llm import analyze_tweet
                            from alert import send_whatsapp_alert
                            
                            analysis = analyze_tweet(tweet.text, tweet.handle)
                            
                            if analysis and analysis['is_market_moving']:
                                print(f"    [ALERT] High Impact Claim Detected! Int: {analysis['intensity_score']}/10")
                                print(f"    [ALERT] Tickers: {analysis['tickers']}")
                                
                                # 5. Send WhatsApp Alert
                                alert_msg = (
                                    f"🚨 *MARKET ALERT* 🚨\n"
                                    f"👤 @{tweet.handle}\n"
                                    f"📈 Tickers: {', '.join(analysis['tickers']) if analysis.get('tickers') else 'None'}\n"
                                    f"🔥 Intensity: {analysis['intensity_score']}/10\n"
                                    f"📝 Claim: {analysis['claim_summary']}\n"
                                    f"💡 Reasoning: {analysis['reasoning']}\n"
                                    f"🔗 Link: {t_data.get('url', '')}"
                                )
                                send_whatsapp_alert(alert_msg)
                
                    db_session.commit()
                else:
                    print(f"    --> No tweets returned (Instances may be rate-limited/offline).")
                    
            except Exception as e:
                print(f"    --> Error fetching @{handle}: {e}")
                db_session.rollback()
            
        print(f"\\nSleeping for {interval / 60} minutes...")
        time.sleep(interval)

if __name__ == "__main__":
    monitor_loop()
