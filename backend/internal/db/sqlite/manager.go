package sqlite

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sync"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

const (
	dbFileName = "babel.db"
	schemaFile = "schema.sql"
)

// DBManager handles database connections and operations
type DBManager struct {
	db   *sql.DB
	mu   sync.RWMutex
	path string
}

// NewDBManager creates a new database manager instance
func NewDBManager(dataDir string) (*DBManager, error) {
	// Ensure data directory exists
	if err := os.MkdirAll(dataDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create data directory: %v", err)
	}

	dbPath := filepath.Join(dataDir, dbFileName)
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %v", err)
	}

	// Set connection pool settings
	db.SetMaxOpenConns(1) // SQLite only supports one writer
	db.SetMaxIdleConns(1)
	db.SetConnMaxLifetime(time.Hour)

	manager := &DBManager{
		db:   db,
		path: dbPath,
	}

	// Initialize schema
	if err := manager.initSchema(); err != nil {
		db.Close()
		return nil, fmt.Errorf("failed to initialize schema: %v", err)
	}

	return manager, nil
}

// initSchema initializes the database schema
func (m *DBManager) initSchema() error {
	schemaPath := filepath.Join(filepath.Dir(m.path), schemaFile)
	schema, err := os.ReadFile(schemaPath)
	if err != nil {
		return fmt.Errorf("failed to read schema file: %v", err)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	_, err = m.db.Exec(string(schema))
	if err != nil {
		return fmt.Errorf("failed to execute schema: %v", err)
	}

	return nil
}

// Close closes the database connection
func (m *DBManager) Close() error {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.db.Close()
}

// Transaction executes a function within a database transaction
func (m *DBManager) Transaction(fn func(*sql.Tx) error) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	tx, err := m.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %v", err)
	}

	if err := fn(tx); err != nil {
		if rbErr := tx.Rollback(); rbErr != nil {
			log.Printf("failed to rollback transaction: %v", rbErr)
		}
		return err
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %v", err)
	}

	return nil
}

// Helper functions for JSON handling

func jsonArrayToString(arr []string) (string, error) {
	if arr == nil {
		return "[]", nil
	}
	bytes, err := json.Marshal(arr)
	if err != nil {
		return "", fmt.Errorf("failed to marshal JSON array: %v", err)
	}
	return string(bytes), nil
}

func stringToJSONArray(s string) ([]string, error) {
	if s == "" {
		return []string{}, nil
	}
	var arr []string
	if err := json.Unmarshal([]byte(s), &arr); err != nil {
		return nil, fmt.Errorf("failed to unmarshal JSON array: %v", err)
	}
	return arr, nil
}

// Maintenance performs routine database maintenance
func (m *DBManager) Maintenance() error {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Run VACUUM to reclaim space and defragment
	_, err := m.db.Exec("VACUUM;")
	if err != nil {
		return fmt.Errorf("failed to vacuum database: %v", err)
	}

	// Analyze tables for query optimization
	_, err = m.db.Exec("ANALYZE;")
	if err != nil {
		return fmt.Errorf("failed to analyze database: %v", err)
	}

	// Clean expired cache entries
	_, err = m.db.Exec(`
		DELETE FROM algorithm_cache 
		WHERE expiry < ?;
	`, time.Now().Unix())
	if err != nil {
		return fmt.Errorf("failed to clean cache: %v", err)
	}

	return nil
}

// GetDB returns the underlying database connection
// Use with caution and prefer using the DBManager methods
func (m *DBManager) GetDB() *sql.DB {
	return m.db
}
