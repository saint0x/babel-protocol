"""
Engagement Analytics Algorithm for Gossip Social Network

This algorithm implements a sophisticated engagement tracking and analysis system that measures
and evaluates user interactions with content, focusing on quality of engagement over quantity.

Core Philosophy:
- Quality engagement over vanity metrics
- Context-aware interaction analysis
- Evidence-based participation rewards
- Community value contribution tracking
- Authenticity-weighted engagement scoring

Key Features:
1. Multi-dimensional engagement scoring
2. Time-weighted interaction analysis
3. Evidence-based engagement boost
4. Context chain tracking
5. User participation rewards
"""

class EngagementAnalytics:
    def __init__(self):
        self.content_engagement = {}  # Maps content_id to engagement metrics
        self.user_engagement = {}     # Maps user_id to engagement history
        self.interaction_chains = {}  # Maps content_id to interaction chains
        self.engagement_weights = {
            'view': 1,
            'like': 2,
            'comment': 5,
            'share': 3,
            'evidence_addition': 8,
            'context_addition': 6,
            'quality_discussion': 10
        }

    def record_interaction(self, content_id, user_id, interaction_type, interaction_data=None):
        """
        Record a user interaction with content
        
        Parameters:
        - interaction_type: type of interaction (view, like, comment, etc.)
        - interaction_data: additional data about the interaction
        """
        # Initialize content engagement tracking if needed
        if content_id not in self.content_engagement:
            self.content_engagement[content_id] = {
                'interactions': {},
                'total_score': 0,
                'quality_score': 0,
                'engagement_rate': 0,
                'interaction_chain': []
            }

        # Initialize user engagement tracking if needed
        if user_id not in self.user_engagement:
            self.user_engagement[user_id] = {
                'interaction_history': [],
                'engagement_score': 0,
                'quality_contributions': 0
            }

        # Record the interaction
        timestamp = self._get_current_timestamp()
        interaction = {
            'type': interaction_type,
            'timestamp': timestamp,
            'data': interaction_data,
            'weight': self.engagement_weights.get(interaction_type, 1)
        }

        # Update content engagement
        if interaction_type not in self.content_engagement[content_id]['interactions']:
            self.content_engagement[content_id]['interactions'][interaction_type] = []
        self.content_engagement[content_id]['interactions'][interaction_type].append(interaction)

        # Update user engagement history
        self.user_engagement[user_id]['interaction_history'].append({
            'content_id': content_id,
            'interaction': interaction
        })

        # Recalculate scores
        self._update_content_scores(content_id)
        self._update_user_scores(user_id)

    def _update_content_scores(self, content_id):
        """
        Update engagement scores for content based on:
        1. Interaction weights
        2. Time decay
        3. Quality of interactions
        4. Engagement patterns
        """
        content = self.content_engagement[content_id]
        total_score = 0
        quality_score = 0
        interaction_count = 0

        for interaction_type, interactions in content['interactions'].items():
            type_weight = self.engagement_weights[interaction_type]
            
            for interaction in interactions:
                time_factor = self._get_time_decay(interaction['timestamp'])
                interaction_score = type_weight * time_factor
                
                # Add quality bonuses for certain interactions
                if interaction['data'] and interaction['data'].get('quality_markers'):
                    quality_bonus = self._calculate_quality_bonus(interaction['data']['quality_markers'])
                    interaction_score *= (1 + quality_bonus)
                
                total_score += interaction_score
                if interaction_type in ['comment', 'evidence_addition', 'context_addition']:
                    quality_score += interaction_score
                
                interaction_count += 1

        # Update content engagement metrics
        content['total_score'] = total_score
        content['quality_score'] = quality_score
        content['engagement_rate'] = total_score / max(1, interaction_count)

    def _update_user_scores(self, user_id):
        """
        Update engagement scores for user based on:
        1. Interaction history
        2. Quality of contributions
        3. Consistency of engagement
        """
        user = self.user_engagement[user_id]
        total_score = 0
        quality_contributions = 0

        for interaction_record in user['interaction_history']:
            interaction = interaction_record['interaction']
            time_factor = self._get_time_decay(interaction['timestamp'])
            
            # Calculate base score
            interaction_score = interaction['weight'] * time_factor
            
            # Add quality bonuses
            if interaction['data'] and interaction['data'].get('quality_markers'):
                quality_bonus = self._calculate_quality_bonus(interaction['data']['quality_markers'])
                interaction_score *= (1 + quality_bonus)
                quality_contributions += quality_bonus
            
            total_score += interaction_score

        # Update user engagement metrics
        user['engagement_score'] = total_score
        user['quality_contributions'] = quality_contributions

    def get_content_analytics(self, content_id):
        """
        Get comprehensive analytics for content
        Returns dict with various engagement metrics
        """
        if content_id not in self.content_engagement:
            return {
                'total_score': 0,
                'quality_score': 0,
                'engagement_rate': 0,
                'interaction_counts': {}
            }

        content = self.content_engagement[content_id]
        interaction_counts = {
            itype: len(interactions)
            for itype, interactions in content['interactions'].items()
        }

        return {
            'total_score': content['total_score'],
            'quality_score': content['quality_score'],
            'engagement_rate': content['engagement_rate'],
            'interaction_counts': interaction_counts
        }

    def get_user_analytics(self, user_id):
        """
        Get comprehensive analytics for user
        Returns dict with various engagement metrics
        """
        if user_id not in self.user_engagement:
            return {
                'engagement_score': 0,
                'quality_contributions': 0,
                'interaction_count': 0
            }

        user = self.user_engagement[user_id]
        return {
            'engagement_score': user['engagement_score'],
            'quality_contributions': user['quality_contributions'],
            'interaction_count': len(user['interaction_history'])
        }

    def _calculate_quality_bonus(self, quality_markers):
        """Calculate quality bonus based on interaction quality markers"""
        # Quality markers might include: evidence provided, context added, 
        # constructive discussion, etc.
        bonus = sum(0.1 for marker in quality_markers if marker)
        return min(0.5, bonus)  # Cap bonus at 50%

    def _get_current_timestamp(self):
        """Get current timestamp"""
        import time
        return time.time()

    def _get_time_decay(self, timestamp):
        """Calculate time decay factor for engagement"""
        current_time = self._get_current_timestamp()
        age_hours = (current_time - timestamp) / 3600
        return max(0.2, 1.0 - (age_hours / 168))  # Decay over one week to 20% minimum 