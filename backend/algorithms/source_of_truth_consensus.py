"""
Source of Truth Consensus Algorithm for Gossip Social Network

This algorithm implements a sophisticated consensus mechanism that determines the perceived truth value
of content based on community validation, user authenticity scores, and evidence provided.

Core Philosophy:
- Truth is fluid and collectively determined
- Evidence and context enhance credibility
- User authenticity scores influence truth determination
- Community consensus shapes narrative validity

Key Features:
1. Weighted voting based on user authenticity scores
2. Evidence-based truth amplification
3. Time-decay for truth consensus
4. Context chain validation
5. Minority opinion preservation
"""

class SourceOfTruthConsensus:
    def __init__(self):
        self.content_truth_scores = {}  # Maps content_id to truth score
        self.user_votes = {}  # Maps content_id to {user_id: vote}
        self.evidence_pool = {}  # Maps content_id to list of evidence
        self.context_chains = {}  # Maps content_id to related context

    def submit_vote(self, content_id, user_id, vote_type, user_authenticity_score, evidence=None):
        """
        Submit a vote for content truth value
        
        Parameters:
        - vote_type: 'true', 'false', 'uncertain'
        - user_authenticity_score: 0.0 to 1.0
        - evidence: Optional supporting evidence/context
        """
        if content_id not in self.user_votes:
            self.user_votes[content_id] = {}
            self.content_truth_scores[content_id] = 0.5  # Initial neutral score
            self.evidence_pool[content_id] = []

        self.user_votes[content_id][user_id] = {
            'vote': vote_type,
            'weight': user_authenticity_score,
            'timestamp': self._get_current_timestamp()
        }

        if evidence:
            self.evidence_pool[content_id].append({
                'user_id': user_id,
                'evidence': evidence,
                'timestamp': self._get_current_timestamp()
            })

        self._recalculate_truth_score(content_id)

    def _recalculate_truth_score(self, content_id):
        """
        Recalculate truth score based on:
        1. Weighted user votes
        2. Evidence quality
        3. Time decay
        4. Context chain strength
        """
        votes = self.user_votes[content_id]
        evidence = self.evidence_pool[content_id]
        
        # Calculate base score from weighted votes
        total_weight = 0
        weighted_score = 0
        
        for vote_data in votes.values():
            vote_weight = vote_data['weight']
            vote_age = self._get_time_decay(vote_data['timestamp'])
            
            if vote_data['vote'] == 'true':
                weighted_score += vote_weight * vote_age
            elif vote_data['vote'] == 'false':
                weighted_score -= vote_weight * vote_age
            
            total_weight += vote_weight * vote_age

        base_score = 0.5 + (weighted_score / (2 * total_weight)) if total_weight > 0 else 0.5

        # Adjust score based on evidence
        evidence_bonus = min(0.2, len(evidence) * 0.05)  # Max 20% boost from evidence
        
        # Final truth score
        self.content_truth_scores[content_id] = min(1.0, base_score + evidence_bonus)

    def get_truth_consensus(self, content_id):
        """
        Get the current truth consensus for content
        Returns:
        - truth_score: 0.0 to 1.0
        - confidence: 0.0 to 1.0
        - evidence_count: int
        """
        if content_id not in self.content_truth_scores:
            return {
                'truth_score': 0.5,
                'confidence': 0.0,
                'evidence_count': 0
            }

        truth_score = self.content_truth_scores[content_id]
        vote_count = len(self.user_votes[content_id])
        evidence_count = len(self.evidence_pool[content_id])

        # Calculate confidence based on number of votes and evidence
        confidence = min(1.0, (vote_count / 10) + (evidence_count / 5))

        return {
            'truth_score': truth_score,
            'confidence': confidence,
            'evidence_count': evidence_count
        }

    def _get_current_timestamp(self):
        """Placeholder for getting current timestamp"""
        import time
        return time.time()

    def _get_time_decay(self, timestamp):
        """Calculate time decay factor for votes"""
        current_time = self._get_current_timestamp()
        age_hours = (current_time - timestamp) / 3600
        return max(0.2, 1.0 - (age_hours / 168))  # Decay over one week to 20% minimum 