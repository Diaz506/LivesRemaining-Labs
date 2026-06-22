# Lives Remaining Labs — Data Schema

**FICTIONAL COMPANY:** Lives Remaining Labs is a fictional game studio for this Databricks reference implementation.

## Event Types

All events share a common envelope, then carry type-specific payload JSON.

```
player_id: str (UUID)
event_id: str (UUID, unique)
event_type: str (enum: login, kill, death, purchase, session_end, logout)
timestamp: datetime (UTC)
game_mode: str (enum: deathmatch, capture_flag, ranked, casual)
region: str (enum: NA, EU, APAC, LATAM)
platform: str (enum: PC, Console, Mobile)
payload: JSON (type-specific)
ingest_ts: datetime (server-side ingestion time)
```

---

## Bronze Table: `lives_remaining_raw_events`

Raw events exactly as received. Partitioned by `ingest_date`.

| Column | Type | Example |
|--------|------|---------|
| event_id | string | `550e8400-e29b-41d4-a716-446655440000` |
| player_id | string | `player_123abc` |
| event_type | string | `kill` \| `death` \| `purchase` \| `login` \| `logout` \| `session_end` |
| timestamp | timestamp | `2025-01-15 14:32:45.123` |
| game_mode | string | `deathmatch` \| `ranked` \| `capture_flag` |
| region | string | `NA` \| `EU` \| `APAC` \| `LATAM` |
| platform | string | `PC` \| `Console` \| `Mobile` |
| payload | string (JSON) | `{"opponent_id": "...", "weapon": "..."}` |
| ingest_ts | timestamp | `2025-01-15 14:33:10.567` |
| ingest_date | date | `2025-01-15` |

---

## Silver Tables

### `player_sessions`

Aggregated session-level data. One row per session.

| Column | Type | Note |
|--------|------|------|
| session_id | string | Derived from login → logout |
| player_id | string | FK to player profiles |
| login_ts | timestamp | Start of session |
| logout_ts | timestamp | End of session (or null if active) |
| duration_min | double | `(logout_ts - login_ts) / 60` |
| game_mode | string | Primary mode played in session |
| region | string | Region player logged in from |
| platform | string | PC / Console / Mobile |
| kills | integer | Total kills in session |
| deaths | integer | Total deaths in session |
| kd_ratio | double | kills / (deaths + 1) |
| matches_played | integer | Count of game matches |
| matches_won | integer | Matches won |
| win_rate | double | matches_won / matches_played |
| items_purchased | integer | In-game purchases |
| spent_usd | double | Total spend (USD) in session |
| experience_gain | integer | XP earned |

---

### `player_events_cleaned`

Normalized event log with parsed payloads. Inherits all Bronze columns + parsed fields.

| Column | Type | Note |
|--------|------|------|
| (all Bronze fields) | - | - |
| event_type_normalized | string | Deduplicated/normalized type |
| opponent_id | string | From kill/death payload (nulls for non-combat) |
| weapon | string | Weapon used (combat events only) |
| item_name | string | Item purchased (purchase events only) |
| item_price_usd | double | Purchase amount |
| experience_granted | integer | XP value of kill/achievement |

---

## Gold Tables

### `churn_features_daily`

One row per player per day. Features computed from 7-day and 30-day windows.

| Column | Type | Note |
|--------|------|------|
| player_id | string | Player identifier |
| compute_date | date | Date features computed |
| days_since_login | integer | Days since last login as of compute_date |
| login_count_7d | integer | Logins in past 7 days |
| login_count_30d | integer | Logins in past 30 days |
| avg_session_duration_7d | double | Avg session length (minutes) |
| total_playtime_7d | double | Total playtime (hours) |
| kill_count_7d | integer | Total kills |
| match_count_7d | integer | Matches played |
| win_rate_7d | double | Win rate (%) |
| avg_spend_7d | double | Avg daily spend (USD) |
| avg_spend_30d | double | Avg daily spend (USD) over 30d |
| total_spend_30d | double | Cumulative spend (USD) in 30d |
| is_new_player | boolean | Created account < 30 days ago |
| platform_primary | string | Most-used platform |
| region_primary | string | Most-used region |
| churn_label | integer | **Target**: 1 = churned in next 7 days, 0 = retained |

---

### `arpu_features_daily`

One row per player per day. Revenue prediction features.

| Column | Type | Note |
|--------|------|------|
| player_id | string | - |
| compute_date | date | - |
| avg_spend_7d | double | Average daily spend last 7 days |
| avg_spend_30d | double | Average daily spend last 30 days |
| total_spend_90d | double | Cumulative spend last 90 days |
| avg_spend_all_time | double | Lifetime ARPU |
| purchase_frequency_7d | integer | Purchase count |
| purchase_frequency_30d | integer | Purchase count |
| days_since_first_purchase | integer | Account age (days) |
| days_since_last_purchase | integer | Recency (days) |
| premium_tier | string | Enum: free, bronze, silver, gold, platinum |
| is_whale | boolean | Spend > 95th percentile |

---

## Sample Events (JSON Payloads by Type)

### `login`
```json
{
  "event_type": "login",
  "platform": "PC",
  "region": "NA",
  "payload": {
    "session_token": "...",
    "ip_country": "US"
  }
}
```

### `kill`
```json
{
  "event_type": "kill",
  "payload": {
    "opponent_id": "player_456def",
    "weapon": "sniper_rifle",
    "headshot": true,
    "experience_granted": 150
  }
}
```

### `purchase`
```json
{
  "event_type": "purchase",
  "payload": {
    "item_id": "skin_dragon_blue",
    "item_name": "Dragon Blue Skin",
    "item_price_usd": 9.99,
    "currency": "USD",
    "payment_method": "credit_card"
  }
}
```

### `session_end`
```json
{
  "event_type": "session_end",
  "payload": {
    "total_kills": 42,
    "total_deaths": 18,
    "total_earned_xp": 5000,
    "duration_seconds": 1800,
    "items_purchased": 2
  }
}
```

---

## Data Volume Estimates

| Metric | Value |
|--------|-------|
| Events per day | 50M (typical mobile title) |
| Daily active players (DAU) | 500K |
| Events per player per day | ~100 |
| Retention (Day 1) | ~40% |
| Retention (Day 30) | ~5% |
| ARPU | $3–5 (free-to-play) |
