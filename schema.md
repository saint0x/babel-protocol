# 🌐 Babel Protocol Schema Design

> ## 📦 Hashgraph Storage (Immutable Ledger)
> 
> ### 📝 Content Records
> 
> #### Content
> | Field | Type | Description |
> |-------|------|-------------|
> | id | UUID | Primary identifier |
> | author_id | UUID | Content creator reference |
> | content_type | STRING | "post", "comment", "evidence" |
> | content_text | TEXT | Main content body |
> | media_urls | [STRING] | Array of media references |
> | parent_id | UUID? | For replies/evidence chains |
> | timestamp | TIMESTAMP | Creation time |
> | signature | STRING | Cryptographic signature |
> | hash | STRING | Content hash |
> 
> #### Content Metadata
> | Field | Type | Description |
> |-------|------|-------------|
> | content_id | UUID | Reference to content |
> | topics | [STRING] | Content topics |
> | entities | [STRING] | Named entities |
> | language | STRING | Content language |
> | sentiment_score | FLOAT | Content sentiment |
> | evidence_count | INT | Number of evidence pieces |
> | context_references | [UUID] | Related content |
> 
> ### 👤 User Records
> 
> #### User
> | Field | Type | Description |
> |-------|------|-------------|
> | id | UUID | Primary identifier |
> | public_key | STRING | User's public key |
> | username | STRING | Display name |
> | created_at | TIMESTAMP | Account creation time |
> | authenticity_score | FLOAT | User's truth score |
> | reputation_score | FLOAT | Overall reputation |
> 
> #### User Credentials
> | Field | Type | Description |
> |-------|------|-------------|
> | user_id | UUID | Reference to user |
> | hashed_password | STRING | Encrypted password |
> | salt | STRING | Password salt |
> | last_login | TIMESTAMP | Last login time |
> | security_settings | JSONB | Security preferences |
> 
> ### ⚖️ Consensus Records
> 
> #### Truth Consensus
> | Field | Type | Description |
> |-------|------|-------------|
> | content_id | UUID | Reference to content |
> | voter_id | UUID | Voter reference |
> | vote_type | STRING | "true", "false", "uncertain" |
> | vote_weight | FLOAT | Vote importance |
> | evidence_ids | [UUID] | Supporting evidence |
> | timestamp | TIMESTAMP | Vote time |
> 
> #### Evidence Chain
> | Field | Type | Description |
> |-------|------|-------------|
> | content_id | UUID | Reference to content |
> | evidence_id | UUID | Evidence identifier |
> | submitter_id | UUID | Evidence submitter |
> | evidence_type | STRING | "url", "image", "text" |
> | evidence_text | TEXT | Evidence content |
> | quality_score | FLOAT | Evidence quality |
> | timestamp | TIMESTAMP | Submission time |

---

> ## 📊 PostgreSQL (Analytics & Historical Data)
> 
> ### User Analytics
> ```sql
> CREATE TABLE user_behavior_metrics (
>     user_id UUID PRIMARY KEY,
>     total_posts INT,
>     total_interactions INT,
>     quality_contributions INT,
>     truth_accuracy FLOAT,
>     engagement_score FLOAT,
>     created_at TIMESTAMP,
>     updated_at TIMESTAMP
> );
> 
> CREATE TABLE user_reputation_history (
>     id UUID PRIMARY KEY,
>     user_id UUID,
>     old_score FLOAT,
>     new_score FLOAT,
>     reason STRING,
>     timestamp TIMESTAMP,
>     FOREIGN KEY (user_id) REFERENCES users(id)
> );
> ```
> 
> ### Content Analytics
> ```sql
> CREATE TABLE content_performance (
>     content_id UUID PRIMARY KEY,
>     views_count INT,
>     engagement_rate FLOAT,
>     truth_score FLOAT,
>     quality_score FLOAT,
>     virality_score FLOAT,
>     created_at TIMESTAMP,
>     updated_at TIMESTAMP
> );
> 
> CREATE TABLE content_visibility_history (
>     id UUID PRIMARY KEY,
>     content_id UUID,
>     visibility_level STRING,
>     reason STRING,
>     timestamp TIMESTAMP,
>     FOREIGN KEY (content_id) REFERENCES content(id)
> );
> ```
> 
> ### Algorithm Performance
> ```sql
> CREATE TABLE algorithm_adjustments (
>     id UUID PRIMARY KEY,
>     algorithm_type STRING,
>     parameters JSONB,
>     performance_metrics JSONB,
>     timestamp TIMESTAMP
> );
> 
> CREATE TABLE algorithm_feedback (
>     id UUID PRIMARY KEY,
>     algorithm_type STRING,
>     user_id UUID,
>     feedback_type STRING,
>     feedback_data JSONB,
>     timestamp TIMESTAMP
> );
> ```

---

> ## ⚡ Redis (Real-time Metrics)
> 
> ### Content Metrics
> ```redis
> content:{id}:metrics {
>     visibility_score: FLOAT
>     engagement_velocity: FLOAT
>     truth_consensus: FLOAT
>     trending_score: FLOAT
>     last_updated: TIMESTAMP
> }
> 
> content:{id}:interactions {
>     views: INT
>     likes: INT
>     shares: INT
>     comments: INT
>     evidence_count: INT
> }
> ```
> 
> ### User Metrics
> ```redis
> user:{id}:metrics {
>     authenticity_score: FLOAT
>     engagement_level: FLOAT
>     recent_interactions: LIST
>     online_status: STRING
>     last_active: TIMESTAMP
> }
> 
> user:{id}:feed_cache {
>     content_ids: LIST
>     timestamp: TIMESTAMP
>     ttl: 300  # 5 minutes
> }
> ```
> 
> ### Trending Data
> ```redis
> trending:topics {
>     ZADD topic_name score timestamp
> }
> 
> trending:content {
>     ZADD content_id velocity timestamp
> }
> ```
> 
> ### Algorithm Cache
> ```redis
> algo:recommendations:{user_id} {
>     content_ids: LIST
>     parameters: HASH
>     timestamp: TIMESTAMP
>     ttl: 600  # 10 minutes
> }
> 
> algo:consensus:{content_id} {
>     truth_score: FLOAT
>     confidence: FLOAT
>     vote_count: INT
>     last_updated: TIMESTAMP
> }
> ```

---

> ## 🔍 Indices
> 
> ### PostgreSQL Indices
> ```sql
> -- User Analytics
> CREATE INDEX idx_user_behavior_user_id 
>     ON user_behavior_metrics(user_id);
> CREATE INDEX idx_user_reputation_user_id 
>     ON user_reputation_history(user_id);
> CREATE INDEX idx_user_reputation_timestamp 
>     ON user_reputation_history(timestamp);
> 
> -- Content Analytics
> CREATE INDEX idx_content_performance_score 
>     ON content_performance(quality_score, truth_score);
> CREATE INDEX idx_content_visibility_content_id 
>     ON content_visibility_history(content_id);
> CREATE INDEX idx_content_visibility_timestamp 
>     ON content_visibility_history(timestamp);
> 
> -- Algorithm Performance
> CREATE INDEX idx_algorithm_adjustments_type 
>     ON algorithm_adjustments(algorithm_type);
> CREATE INDEX idx_algorithm_feedback_type 
>     ON algorithm_feedback(algorithm_type, timestamp);
> ```
> 
> ### Redis Indices
> | Type | Command | Purpose |
> |------|---------|----------|
> | Sorted Sets | `ZADD trending:topics` | Track trending topics |
> | Sorted Sets | `ZADD trending:content` | Track trending content |
> | Sets | `SADD active:users` | Track active users |
> | Sets | `SADD trending:hashtags` | Track trending hashtags |
> | Lists | `LPUSH user:{id}:feed` | User feed caching |
> | Lists | `LPUSH content:{id}:comments` | Content comments |
> 
> ### Hashgraph Indices
> 
> #### Content Indices
> - `content_by_author`
> - `content_by_timestamp`
> - `content_by_topic`
> - `content_by_evidence_count`
> 
> #### User Indices
> - `users_by_reputation`
> - `users_by_authenticity`
> - `users_by_contribution`
> 
> #### Consensus Indices
> - `consensus_by_content`
> - `evidence_by_content`
> - `votes_by_user` 