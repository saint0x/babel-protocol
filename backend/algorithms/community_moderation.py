"""
Community Moderation Algorithm for Gossip Social Network

This algorithm implements a community-driven moderation system that aligns with our platform's philosophy
of minimal centralized moderation while maintaining content quality through collective action.

Core Philosophy:
- Community self-regulation over centralized control
- Weighted influence based on user authenticity
- Progressive content visibility adjustment
- Preservation of minority viewpoints
- Evidence-based moderation decisions

Key Features:
1. Dynamic visibility scoring
2. User reputation weighting
3. Content quality assessment
4. Automated threshold management
5. Appeal mechanism support
"""

class CommunityModerationSystem:
    def __init__(self):
        self.content_scores = {}  # Maps content_id to moderation scores
        self.user_actions = {}    # Maps content_id to user moderation actions
        self.appeal_records = {}  # Maps content_id to appeal history
        self.visibility_thresholds = {
            'high': 0.8,
            'normal': 0.5,
            'reduced': 0.3,
            'minimal': 0.1
        }

    def record_moderation_action(self, content_id, user_id, action_type, user_authenticity_score, evidence=None):
        """
        Record a moderation action from a user
        
        Parameters:
        - action_type: 'upvote', 'downvote', 'flag', 'support'
        - user_authenticity_score: 0.0 to 1.0
        - evidence: Optional supporting evidence for action
        """
        if content_id not in self.content_scores:
            self.content_scores[content_id] = {
                'visibility_score': 1.0,
                'quality_score': 0.5,
                'flag_count': 0,
                'support_count': 0
            }
            self.user_actions[content_id] = {}

        # Record user action
        self.user_actions[content_id][user_id] = {
            'action': action_type,
            'weight': user_authenticity_score,
            'timestamp': self._get_current_timestamp(),
            'evidence': evidence
        }

        self._recalculate_content_scores(content_id)

    def _recalculate_content_scores(self, content_id):
        """
        Recalculate content scores based on:
        1. User actions and their weights
        2. Evidence quality
        3. Time-based factors
        4. Community consensus
        """
        actions = self.user_actions[content_id]
        
        # Initialize counters
        weighted_score = 0
        total_weight = 0
        flag_count = 0
        support_count = 0
        
        # Calculate weighted scores
        for action_data in actions.values():
            weight = action_data['weight']
            time_factor = self._get_time_decay(action_data['timestamp'])
            adjusted_weight = weight * time_factor
            
            if action_data['action'] == 'upvote':
                weighted_score += adjusted_weight
            elif action_data['action'] == 'downvote':
                weighted_score -= adjusted_weight * 0.8  # Downvotes have slightly less impact
            elif action_data['action'] == 'flag':
                flag_count += 1
                weighted_score -= adjusted_weight * 1.2  # Flags have more impact
            elif action_data['action'] == 'support':
                support_count += 1
                weighted_score += adjusted_weight * 1.1  # Support slightly counters flags
                
            total_weight += adjusted_weight

        # Calculate base visibility score
        base_score = 0.5 + (weighted_score / (2 * total_weight)) if total_weight > 0 else 0.5
        
        # Adjust for flags and support
        flag_impact = min(0.3, flag_count * 0.05)  # Max 30% reduction from flags
        support_boost = min(0.2, support_count * 0.04)  # Max 20% boost from support
        
        # Update content scores
        self.content_scores[content_id].update({
            'visibility_score': max(0.0, min(1.0, base_score - flag_impact + support_boost)),
            'quality_score': base_score,
            'flag_count': flag_count,
            'support_count': support_count
        })

    def get_content_visibility(self, content_id):
        """
        Get content visibility level and scores
        Returns dict with visibility level and scores
        """
        if content_id not in self.content_scores:
            return {
                'visibility_level': 'normal',
                'visibility_score': 1.0,
                'quality_score': 0.5,
                'flag_count': 0,
                'support_count': 0
            }

        scores = self.content_scores[content_id]
        visibility_score = scores['visibility_score']

        # Determine visibility level
        if visibility_score >= self.visibility_thresholds['high']:
            visibility_level = 'high'
        elif visibility_score >= self.visibility_thresholds['normal']:
            visibility_level = 'normal'
        elif visibility_score >= self.visibility_thresholds['reduced']:
            visibility_level = 'reduced'
        else:
            visibility_level = 'minimal'

        return {
            'visibility_level': visibility_level,
            'visibility_score': visibility_score,
            'quality_score': scores['quality_score'],
            'flag_count': scores['flag_count'],
            'support_count': scores['support_count']
        }

    def submit_appeal(self, content_id, user_id, appeal_text, evidence=None):
        """
        Submit an appeal for content moderation decision
        Returns appeal_id if successful
        """
        if content_id not in self.appeal_records:
            self.appeal_records[content_id] = []

        appeal_id = len(self.appeal_records[content_id])
        
        self.appeal_records[content_id].append({
            'appeal_id': appeal_id,
            'user_id': user_id,
            'timestamp': self._get_current_timestamp(),
            'appeal_text': appeal_text,
            'evidence': evidence,
            'status': 'pending'
        })

        return appeal_id

    def _get_current_timestamp(self):
        """Get current timestamp"""
        import time
        return time.time()

    def _get_time_decay(self, timestamp):
        """Calculate time decay factor for moderation actions"""
        current_time = self._get_current_timestamp()
        age_hours = (current_time - timestamp) / 3600
        return max(0.3, 1.0 - (age_hours / 72))  # Decay over 3 days to 30% minimum 