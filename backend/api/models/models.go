package models

import (
	"encoding/json"
	"time"
)

// Content represents a piece of content in the system
type Content struct {
	ID               string    `json:"id"`
	AuthorID         string    `json:"author_id"`
	ContentType      string    `json:"content_type"`
	ContentText      string    `json:"content_text"`
	MediaURLs        []string  `json:"media_urls"`
	ParentID         *string   `json:"parent_id,omitempty"`
	Timestamp        time.Time `json:"timestamp"`
	Signature        string    `json:"signature"`
	Hash             string    `json:"hash"`
	ProcessingStatus string    `json:"processing_status"`
	LastUpdated      time.Time `json:"last_updated"`
}

// Vote represents a vote on a piece of content
type Vote struct {
	ContentID string    `json:"content_id"`
	VoterID   string    `json:"voter_id"`
	VoteType  string    `json:"vote_type"`
	Timestamp time.Time `json:"timestamp"`
}

// Evidence represents supporting evidence for a piece of content
type Evidence struct {
	ContentID    string    `json:"content_id"`
	SubmitterID  string    `json:"submitter_id"`
	EvidenceType string    `json:"evidence_type"`
	URL          string    `json:"url"`
	Description  string    `json:"description"`
	Timestamp    time.Time `json:"timestamp"`
}

// User represents a user in the system
type User struct {
	ID                string       `json:"id"`
	PublicKey         string       `json:"public_key"`
	Username          string       `json:"username"`
	CreatedAt         time.Time    `json:"created_at"`
	AuthenticityScore float64      `json:"authenticity_score"`
	ReputationScore   float64      `json:"reputation_score"`
	LastActive        time.Time    `json:"last_active"`
	SessionData       *UserSession `json:"session_data,omitempty"`
}

// UserSession represents user session data
type UserSession struct {
	LastLogin     time.Time `json:"last_login"`
	LoginCount    int       `json:"login_count"`
	LastIPAddress string    `json:"last_ip_address"`
}

// MarshalMediaURLs converts media URLs to JSON string
func (c *Content) MarshalMediaURLs() (string, error) {
	if len(c.MediaURLs) == 0 {
		return "[]", nil
	}
	data, err := json.Marshal(c.MediaURLs)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// UnmarshalMediaURLs converts JSON string to media URLs
func (c *Content) UnmarshalMediaURLs(data string) error {
	if data == "" || data == "[]" {
		c.MediaURLs = []string{}
		return nil
	}
	return json.Unmarshal([]byte(data), &c.MediaURLs)
}

// MarshalSessionData converts session data to JSON string
func (u *User) MarshalSessionData() (string, error) {
	if u.SessionData == nil {
		return "", nil
	}
	data, err := json.Marshal(u.SessionData)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// UnmarshalSessionData converts JSON string to session data
func (u *User) UnmarshalSessionData(data string) error {
	if data == "" {
		u.SessionData = nil
		return nil
	}
	u.SessionData = &UserSession{}
	return json.Unmarshal([]byte(data), u.SessionData)
}

// AlgorithmError represents an error that occurred during algorithm execution
type AlgorithmError struct {
	AlgorithmName   string                 `json:"algorithm_name"`
	ErrorType       string                 `json:"error_type"`
	ErrorMessage    string                 `json:"error_message"`
	Context         map[string]interface{} `json:"context"`
	Timestamp       time.Time              `json:"timestamp"`
	Resolved        bool                   `json:"resolved"`
	ResolutionNotes string                 `json:"resolution_notes,omitempty"`
}

// AlgorithmMetric represents a metric recorded during algorithm execution
type AlgorithmMetric struct {
	AlgorithmName string                 `json:"algorithm_name"`
	MetricName    string                 `json:"metric_name"`
	Value         float64                `json:"value"`
	Timestamp     time.Time              `json:"timestamp"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}
