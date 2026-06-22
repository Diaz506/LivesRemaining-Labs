"""
Lab 0: Synthetic Event Generator for Lives Remaining Labs

Generates realistic player events for local testing and demo.
Output: data/raw_events.csv (100k events)

**FICTIONAL COMPANY:** Lives Remaining Labs is a fictional game studio for this Databricks reference implementation.

Usage:
  python scripts/generate_events.py --output data/raw_events.csv --count 100000

Dependencies:
  faker, pandas, numpy
"""

import argparse
import json
import uuid
from datetime import datetime, timedelta
import random

try:
    import pandas as pd
    from faker import Faker
except ImportError:
    print("Error: Install dependencies: pip install pandas faker numpy")
    exit(1)

fake = Faker()

# Constants
EVENT_TYPES = ["login", "kill", "death", "purchase", "session_end", "logout"]
GAME_MODES = ["deathmatch", "capture_flag", "ranked", "casual"]
REGIONS = ["NA", "EU", "APAC", "LATAM"]
PLATFORMS = ["PC", "Console", "Mobile"]
WEAPONS = ["sniper_rifle", "assault_rifle", "shotgun", "pistol", "rocket_launcher"]
SKINS = ["dragon_blue", "neon_pink", "gold_warrior", "shadow_assassin", "fire_phoenix"]


def generate_player_id():
    """Generate consistent player ID."""
    return f"player_{uuid.uuid4().hex[:12]}"


def generate_event_id():
    """Generate unique event ID."""
    return str(uuid.uuid4())


def generate_login_event(player_id, timestamp):
    """Generate login event."""
    return {
        "event_id": generate_event_id(),
        "player_id": player_id,
        "event_type": "login",
        "timestamp": timestamp.isoformat(),
        "game_mode": random.choice(GAME_MODES),
        "region": random.choice(REGIONS),
        "platform": random.choice(PLATFORMS),
        "payload": json.dumps({
            "session_token": str(uuid.uuid4()),
            "ip_country": fake.country_code()
        }),
        "ingest_ts": (timestamp + timedelta(seconds=random.randint(1, 10))).isoformat(),
        "ingest_date": timestamp.date().isoformat()
    }


def generate_kill_event(player_id, timestamp):
    """Generate kill event."""
    return {
        "event_id": generate_event_id(),
        "player_id": player_id,
        "event_type": "kill",
        "timestamp": timestamp.isoformat(),
        "game_mode": random.choice(GAME_MODES),
        "region": random.choice(REGIONS),
        "platform": random.choice(PLATFORMS),
        "payload": json.dumps({
            "opponent_id": generate_player_id(),
            "weapon": random.choice(WEAPONS),
            "headshot": random.choice([True, False]),
            "experience_granted": random.randint(50, 200)
        }),
        "ingest_ts": (timestamp + timedelta(seconds=random.randint(1, 10))).isoformat(),
        "ingest_date": timestamp.date().isoformat()
    }


def generate_death_event(player_id, timestamp):
    """Generate death event."""
    return {
        "event_id": generate_event_id(),
        "player_id": player_id,
        "event_type": "death",
        "timestamp": timestamp.isoformat(),
        "game_mode": random.choice(GAME_MODES),
        "region": random.choice(REGIONS),
        "platform": random.choice(PLATFORMS),
        "payload": json.dumps({
            "killed_by": generate_player_id(),
            "weapon": random.choice(WEAPONS),
            "distance_m": random.randint(5, 500)
        }),
        "ingest_ts": (timestamp + timedelta(seconds=random.randint(1, 10))).isoformat(),
        "ingest_date": timestamp.date().isoformat()
    }


def generate_purchase_event(player_id, timestamp):
    """Generate purchase event."""
    skin = random.choice(SKINS)
    price = random.choice([4.99, 9.99, 19.99, 29.99])
    return {
        "event_id": generate_event_id(),
        "player_id": player_id,
        "event_type": "purchase",
        "timestamp": timestamp.isoformat(),
        "game_mode": random.choice(GAME_MODES),
        "region": random.choice(REGIONS),
        "platform": random.choice(PLATFORMS),
        "payload": json.dumps({
            "item_id": f"skin_{skin}",
            "item_name": f"{skin.replace('_', ' ').title()} Skin",
            "item_price_usd": price,
            "currency": "USD",
            "payment_method": random.choice(["credit_card", "paypal", "google_play", "apple_pay"])
        }),
        "ingest_ts": (timestamp + timedelta(seconds=random.randint(1, 10))).isoformat(),
        "ingest_date": timestamp.date().isoformat()
    }


def generate_session_end_event(player_id, timestamp):
    """Generate session_end event."""
    return {
        "event_id": generate_event_id(),
        "player_id": player_id,
        "event_type": "session_end",
        "timestamp": timestamp.isoformat(),
        "game_mode": random.choice(GAME_MODES),
        "region": random.choice(REGIONS),
        "platform": random.choice(PLATFORMS),
        "payload": json.dumps({
            "total_kills": random.randint(0, 100),
            "total_deaths": random.randint(0, 50),
            "total_earned_xp": random.randint(100, 10000),
            "duration_seconds": random.randint(300, 7200),
            "items_purchased": random.randint(0, 5)
        }),
        "ingest_ts": (timestamp + timedelta(seconds=random.randint(1, 10))).isoformat(),
        "ingest_date": timestamp.date().isoformat()
    }


def generate_logout_event(player_id, timestamp):
    """Generate logout event."""
    return {
        "event_id": generate_event_id(),
        "player_id": player_id,
        "event_type": "logout",
        "timestamp": timestamp.isoformat(),
        "game_mode": None,
        "region": random.choice(REGIONS),
        "platform": random.choice(PLATFORMS),
        "payload": json.dumps({"reason": random.choice(["user_quit", "timeout", "connection_lost"])}),
        "ingest_ts": (timestamp + timedelta(seconds=random.randint(1, 10))).isoformat(),
        "ingest_date": timestamp.date().isoformat()
    }


def generate_events(num_events=100000, num_players=10000, days_back=30):
    """Generate synthetic events."""
    events = []
    players = [generate_player_id() for _ in range(num_players)]
    
    start_date = datetime.utcnow() - timedelta(days=days_back)
    
    print(f"Generating {num_events:,} events for {num_players:,} players...")
    
    for i in range(num_events):
        if i % 10000 == 0:
            print(f"  {i:,} / {num_events:,}")
        
        player_id = random.choice(players)
        event_date = start_date + timedelta(
            days=random.randint(0, days_back - 1),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        event_type = random.choice(EVENT_TYPES)
        
        if event_type == "login":
            event = generate_login_event(player_id, event_date)
        elif event_type == "kill":
            event = generate_kill_event(player_id, event_date)
        elif event_type == "death":
            event = generate_death_event(player_id, event_date)
        elif event_type == "purchase":
            event = generate_purchase_event(player_id, event_date)
        elif event_type == "session_end":
            event = generate_session_end_event(player_id, event_date)
        else:  # logout
            event = generate_logout_event(player_id, event_date)
        
        events.append(event)
    
    return events


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Lives Remaining Labs events.")
    parser.add_argument("--output", default="data/raw_events.csv", help="Output CSV file")
    parser.add_argument("--count", type=int, default=100000, help="Number of events to generate")
    parser.add_argument("--players", type=int, default=10000, help="Number of unique players")
    parser.add_argument("--days", type=int, default=30, help="Days of history to generate")
    
    args = parser.parse_args()
    
    # Generate events
    events = generate_events(args.count, args.players, args.days)
    
    # Convert to DataFrame
    df = pd.DataFrame(events)
    
    # Save to CSV
    df.to_csv(args.output, index=False)
    print(f"\n✅ Saved {len(df):,} events to {args.output}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total events: {len(df):,}")
    print(f"  Unique players: {df['player_id'].nunique():,}")
    print(f"  Event types: {df['event_type'].value_counts().to_dict()}")
    print(f"  Date range: {df['ingest_date'].min()} to {df['ingest_date'].max()}")
    print(f"  Regions: {df['region'].value_counts().to_dict()}")
    print(f"  Platforms: {df['platform'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
