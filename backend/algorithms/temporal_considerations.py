"""
Temporal Considerations Algorithm for Gossip Social Network

This algorithm manages the temporal aspects of content and user interactions, implementing
time-based decay and boost factors that influence content visibility and user engagement scores.

Core Philosophy:
- Time-aware content relevance
- Engagement velocity tracking
- Trend detection and amplification
- Historical context preservation
- Dynamic content lifecycle management

Key Features:
1. Time-decay scoring
2. Engagement velocity calculation
3. Trend detection
4. Content lifecycle management
5. Historical significance preservation
"""

class TemporalConsiderations:
    def __init__(self):
        self.content_temporal_data = {}  # Maps content_id to temporal metrics
        self.trend_data = {}            # Maps topics/tags to trend metrics
        self.velocity_thresholds = {
            'viral': 5.0,
            'trending': 2.0,
            'rising': 1.2,
            'stable': 0.8,
            'declining': 0.5
        }

    def update_content_temporal_metrics(self, content_id, engagement_data, timestamp=None):
        """
        Update temporal metrics for content
        
        Parameters:
        - engagement_data: recent engagement metrics
        - timestamp: timestamp of update (default: current time)
        """
        if timestamp is None:
            timestamp = self._get_current_timestamp()

        if content_id not in self.content_temporal_data:
            self.content_temporal_data[content_id] = {
                'creation_time': timestamp,
                'engagement_history': [],
                'velocity': 0.0,
                'acceleration': 0.0,
                'lifecycle_stage': 'new'
            }

        temporal_data = self.content_temporal_data[content_id]
        
        # Record engagement snapshot
        temporal_data['engagement_history'].append({
            'timestamp': timestamp,
            'metrics': engagement_data
        })

        # Keep only recent history (last 24 hours)
        cutoff_time = timestamp - (24 * 3600)
        temporal_data['engagement_history'] = [
            entry for entry in temporal_data['engagement_history']
            if entry['timestamp'] > cutoff_time
        ]

        # Update velocity and acceleration
        self._calculate_engagement_dynamics(content_id)
        
        # Update lifecycle stage
        self._update_lifecycle_stage(content_id)

    def _calculate_engagement_dynamics(self, content_id):
        """
        Calculate engagement velocity and acceleration
        """
        data = self.content_temporal_data[content_id]
        history = data['engagement_history']
        
        if len(history) < 2:
            return

        # Sort history by timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        # Calculate velocity (rate of engagement change)
        recent_window = history[-6:]  # Last 6 snapshots
        if len(recent_window) >= 2:
            time_diff = recent_window[-1]['timestamp'] - recent_window[0]['timestamp']
            if time_diff > 0:
                engagement_diff = (
                    recent_window[-1]['metrics']['total_engagement'] -
                    recent_window[0]['metrics']['total_engagement']
                )
                data['velocity'] = engagement_diff / time_diff
                
                # Calculate acceleration
                if len(recent_window) >= 3:
                    mid_point = len(recent_window) // 2
                    velocity1 = (
                        recent_window[mid_point]['metrics']['total_engagement'] -
                        recent_window[0]['metrics']['total_engagement']
                    ) / (recent_window[mid_point]['timestamp'] - recent_window[0]['timestamp'])
                    
                    velocity2 = (
                        recent_window[-1]['metrics']['total_engagement'] -
                        recent_window[mid_point]['metrics']['total_engagement']
                    ) / (recent_window[-1]['timestamp'] - recent_window[mid_point]['timestamp'])
                    
                    data['acceleration'] = (velocity2 - velocity1) / (
                        recent_window[-1]['timestamp'] - recent_window[0]['timestamp']
                    )

    def _update_lifecycle_stage(self, content_id):
        """
        Update content lifecycle stage based on velocity and age
        """
        data = self.content_temporal_data[content_id]
        current_time = self._get_current_timestamp()
        age_hours = (current_time - data['creation_time']) / 3600
        
        # Determine lifecycle stage based on velocity and age
        velocity = data['velocity']
        
        if age_hours < 1:  # First hour
            if velocity >= self.velocity_thresholds['viral']:
                stage = 'viral'
            elif velocity >= self.velocity_thresholds['trending']:
                stage = 'trending'
            else:
                stage = 'new'
        elif age_hours < 24:  # First day
            if velocity >= self.velocity_thresholds['viral']:
                stage = 'viral'
            elif velocity >= self.velocity_thresholds['trending']:
                stage = 'trending'
            elif velocity >= self.velocity_thresholds['rising']:
                stage = 'rising'
            elif velocity >= self.velocity_thresholds['stable']:
                stage = 'stable'
            else:
                stage = 'declining'
        else:  # After first day
            if velocity >= self.velocity_thresholds['trending']:
                stage = 'resurgent'
            elif velocity >= self.velocity_thresholds['stable']:
                stage = 'stable'
            else:
                stage = 'archived'

        data['lifecycle_stage'] = stage

    def get_content_temporal_metrics(self, content_id):
        """
        Get temporal metrics for content
        Returns dict with various temporal metrics
        """
        if content_id not in self.content_temporal_data:
            return {
                'age_hours': 0,
                'velocity': 0.0,
                'acceleration': 0.0,
                'lifecycle_stage': 'new'
            }

        data = self.content_temporal_data[content_id]
        current_time = self._get_current_timestamp()
        
        return {
            'age_hours': (current_time - data['creation_time']) / 3600,
            'velocity': data['velocity'],
            'acceleration': data['acceleration'],
            'lifecycle_stage': data['lifecycle_stage']
        }

    def get_trending_topics(self, timeframe_hours=24):
        """
        Get trending topics based on engagement velocity
        Returns list of trending topics with scores
        """
        current_time = self._get_current_timestamp()
        cutoff_time = current_time - (timeframe_hours * 3600)
        
        trending_scores = {}
        
        # Aggregate velocities by topic/tag
        for content_id, data in self.content_temporal_data.items():
            if data['engagement_history'] and data['engagement_history'][-1]['timestamp'] > cutoff_time:
                for topic in data['engagement_history'][-1]['metrics'].get('topics', []):
                    if topic not in trending_scores:
                        trending_scores[topic] = 0
                    trending_scores[topic] += data['velocity']

        # Sort topics by score
        trending_topics = sorted(
            trending_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return trending_topics

    def calculate_temporal_boost(self, content_id):
        """
        Calculate temporal boost factor for content
        Returns float boost factor (0.0 to 2.0)
        """
        if content_id not in self.content_temporal_data:
            return 1.0

        data = self.content_temporal_data[content_id]
        stage = data['lifecycle_stage']
        
        # Define boost factors for different lifecycle stages
        stage_boosts = {
            'viral': 2.0,
            'trending': 1.8,
            'rising': 1.5,
            'new': 1.3,
            'stable': 1.0,
            'declining': 0.7,
            'resurgent': 1.4,
            'archived': 0.5
        }
        
        return stage_boosts.get(stage, 1.0)

    def _get_current_timestamp(self):
        """Get current timestamp"""
        import time
        return time.time() 