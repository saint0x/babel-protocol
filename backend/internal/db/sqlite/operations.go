package sqlite

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"babel-protocol/backend/api/models"
)

// Content Operations

func (m *DBManager) CreateContent(content *models.Content) error {
	mediaURLs, err := content.MarshalMediaURLs()
	if err != nil {
		return fmt.Errorf("failed to marshal media URLs: %v", err)
	}

	return m.Transaction(func(tx *sql.Tx) error {
		_, err := tx.Exec(`
			INSERT INTO content (
				id, author_id, content_type, content_text, media_urls,
				parent_id, timestamp, signature, hash, processing_status, last_updated
			) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
			content.ID, content.AuthorID, content.ContentType, content.ContentText, mediaURLs,
			content.ParentID, content.Timestamp.Unix(), content.Signature, content.Hash,
			content.ProcessingStatus, content.LastUpdated.Unix(),
		)
		return err
	})
}

func (m *DBManager) GetContent(id string) (*models.Content, error) {
	var content models.Content
	var timestamp, lastUpdated int64
	var mediaURLs string

	err := m.db.QueryRow(`
		SELECT id, author_id, content_type, content_text, media_urls,
			   parent_id, timestamp, signature, hash, processing_status, last_updated
		FROM content WHERE id = ?`, id).Scan(
		&content.ID, &content.AuthorID, &content.ContentType, &content.ContentText, &mediaURLs,
		&content.ParentID, &timestamp, &content.Signature, &content.Hash,
		&content.ProcessingStatus, &lastUpdated,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}

	content.Timestamp = time.Unix(timestamp, 0)
	content.LastUpdated = time.Unix(lastUpdated, 0)
	if err := content.UnmarshalMediaURLs(mediaURLs); err != nil {
		return nil, err
	}

	return &content, nil
}

// User Operations

func (m *DBManager) CreateUser(user *models.User) error {
	sessionData, err := user.MarshalSessionData()
	if err != nil {
		return fmt.Errorf("failed to marshal session data: %v", err)
	}

	return m.Transaction(func(tx *sql.Tx) error {
		_, err := tx.Exec(`
			INSERT INTO users (
				id, public_key, username, created_at,
				authenticity_score, reputation_score, last_active, session_data
			) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
			user.ID, user.PublicKey, user.Username, user.CreatedAt.Unix(),
			user.AuthenticityScore, user.ReputationScore, user.LastActive.Unix(), sessionData,
		)
		return err
	})
}

func (m *DBManager) GetUser(id string) (*models.User, error) {
	var user models.User
	var createdAt, lastActive int64
	var sessionData string

	err := m.db.QueryRow(`
		SELECT id, public_key, username, created_at,
			   authenticity_score, reputation_score, last_active, session_data
		FROM users WHERE id = ?`, id).Scan(
		&user.ID, &user.PublicKey, &user.Username, &createdAt,
		&user.AuthenticityScore, &user.ReputationScore, &lastActive, &sessionData,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}

	user.CreatedAt = time.Unix(createdAt, 0)
	user.LastActive = time.Unix(lastActive, 0)
	if err := user.UnmarshalSessionData(sessionData); err != nil {
		return nil, err
	}

	return &user, nil
}

// Algorithm Cache Operations

func (m *DBManager) SetCache(key string, value string, expiry time.Time) error {
	return m.Transaction(func(tx *sql.Tx) error {
		_, err := tx.Exec(`
			INSERT OR REPLACE INTO algorithm_cache (
				key, value, expiry, created_at, last_accessed
			) VALUES (?, ?, ?, ?, ?)`,
			key, value, expiry.Unix(),
			time.Now().Unix(),
			sql.NullInt64{
				Int64: time.Now().Unix(),
				Valid: true,
			},
		)
		return err
	})
}

func (m *DBManager) GetCache(key string) (string, error) {
	var value string
	var expiry int64

	err := m.db.QueryRow(`
		SELECT value, expiry
		FROM algorithm_cache WHERE key = ? AND expiry > ?`,
		key, time.Now().Unix(),
	).Scan(&value, &expiry)

	if err != nil {
		if err == sql.ErrNoRows {
			return "", nil
		}
		return "", err
	}

	return value, nil
}

// Consensus Operations

func (m *DBManager) RecordVote(contentID, voterID, voteType string, voteWeight float64, evidenceIDs []string) error {
	evidenceIDsJSON, err := json.Marshal(evidenceIDs)
	if err != nil {
		return fmt.Errorf("failed to marshal evidence IDs: %v", err)
	}

	return m.Transaction(func(tx *sql.Tx) error {
		_, err := tx.Exec(`
			INSERT OR REPLACE INTO truth_consensus (
				content_id, voter_id, vote_type, vote_weight,
				evidence_ids, timestamp, last_updated
			) VALUES (?, ?, ?, ?, ?, ?, ?)`,
			contentID, voterID, voteType, voteWeight,
			string(evidenceIDsJSON), time.Now().Unix(), time.Now().Unix(),
		)
		return err
	})
}

type VoteInfo struct {
	ContentID   string    `json:"content_id"`
	VoterID     string    `json:"voter_id"`
	VoteType    string    `json:"vote_type"`
	VoteWeight  float64   `json:"vote_weight"`
	EvidenceIDs []string  `json:"evidence_ids"`
	Timestamp   time.Time `json:"timestamp"`
	LastUpdated time.Time `json:"last_updated"`
}

func (m *DBManager) GetContentVotes(contentID string) ([]*VoteInfo, error) {
	rows, err := m.db.Query(`
		SELECT content_id, voter_id, vote_type, vote_weight,
			   evidence_ids, timestamp, last_updated
		FROM truth_consensus WHERE content_id = ?`, contentID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var votes []*VoteInfo
	for rows.Next() {
		var vote VoteInfo
		var timestamp, lastUpdated int64
		var evidenceIDsJSON string

		err := rows.Scan(
			&vote.ContentID, &vote.VoterID, &vote.VoteType, &vote.VoteWeight,
			&evidenceIDsJSON, &timestamp, &lastUpdated,
		)
		if err != nil {
			return nil, err
		}

		vote.Timestamp = time.Unix(timestamp, 0)
		vote.LastUpdated = time.Unix(lastUpdated, 0)
		if err := json.Unmarshal([]byte(evidenceIDsJSON), &vote.EvidenceIDs); err != nil {
			return nil, err
		}

		votes = append(votes, &vote)
	}

	return votes, rows.Err()
}

// Error Logging Operations

func (m *DBManager) LogError(err *models.AlgorithmError) error {
	contextJSON, jsonErr := json.Marshal(err.Context)
	if jsonErr != nil {
		return fmt.Errorf("failed to marshal error context: %v", jsonErr)
	}

	return m.Transaction(func(tx *sql.Tx) error {
		_, dbErr := tx.Exec(`
			INSERT INTO algorithm_errors (
				algorithm_name, error_type, error_message,
				context, timestamp, resolved, resolution_notes
			) VALUES (?, ?, ?, ?, ?, ?, ?)`,
			err.AlgorithmName, err.ErrorType, err.ErrorMessage,
			string(contextJSON), err.Timestamp.Unix(), err.Resolved, err.ResolutionNotes,
		)
		return dbErr
	})
}

// Metrics Operations

func (m *DBManager) RecordMetric(metric *models.AlgorithmMetric) error {
	metadataJSON, err := json.Marshal(metric.Metadata)
	if err != nil {
		return fmt.Errorf("failed to marshal metric metadata: %v", err)
	}

	return m.Transaction(func(tx *sql.Tx) error {
		_, err := tx.Exec(`
			INSERT INTO algorithm_metrics (
				algorithm_name, metric_name, value,
				timestamp, metadata
			) VALUES (?, ?, ?, ?, ?)`,
			metric.AlgorithmName, metric.MetricName, metric.Value,
			metric.Timestamp.Unix(), string(metadataJSON),
		)
		return err
	})
}
