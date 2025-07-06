package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// DVSSChaincode provides functions for managing DVSS-PPA operations
type DVSSChaincode struct {
	contractapi.Contract
}

// Transaction represents a DVSS operation record
type Transaction struct {
	TxID      string                 `json:"tx_id"`
	DataID    string                 `json:"data_id"`
	Operation string                 `json:"operation"`
	UserID    string                 `json:"user_id"`
	Timestamp string                 `json:"timestamp"`
	ShareInfo ShareInfo              `json:"share_info,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Signature string                 `json:"signature"`
}

// ShareInfo contains information about data shares
type ShareInfo struct {
	ShareIndices []int `json:"share_indices"`
	Threshold    int   `json:"threshold"`
	TotalShares  int   `json:"total_shares"`
}

// AccessLog represents data access logging
type AccessLog struct {
	LogID      string                 `json:"log_id"`
	DataID     string                 `json:"data_id"`
	UserID     string                 `json:"user_id"`
	Action     string                 `json:"action"`
	Permission string                 `json:"permission"`
	Result     string                 `json:"result"`
	Timestamp  string                 `json:"timestamp"`
	IPAddress  string                 `json:"ip_address,omitempty"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
}

// ComplianceEvent represents compliance-related events
type ComplianceEvent struct {
	EventID         string   `json:"event_id"`
	EventType       string   `json:"event_type"`
	DataID          string   `json:"data_id"`
	UserID          string   `json:"user_id"`
	Description     string   `json:"description"`
	Severity        string   `json:"severity"`
	ComplianceTypes []string `json:"compliance_types"`
	Status          string   `json:"status"`
	Timestamp       string   `json:"timestamp"`
	ResolvedAt      string   `json:"resolved_at,omitempty"`
}

// DataIntegrity represents data integrity verification results
type DataIntegrity struct {
	DataID          string                 `json:"data_id"`
	VerificationID  string                 `json:"verification_id"`
	TotalShares     int                    `json:"total_shares"`
	AvailableShares int                    `json:"available_shares"`
	IntegrityScore  float64                `json:"integrity_score"`
	Timestamp       string                 `json:"timestamp"`
	Details         map[string]interface{} `json:"details"`
}

// InitLedger initializes the ledger with sample data
func (s *DVSSChaincode) InitLedger(ctx contractapi.TransactionContextInterface) error {
	fmt.Println("DVSS-PPA Chaincode initialized")

	// Initialize with some sample configuration
	config := map[string]interface{}{
		"version":              "1.0.0",
		"initialized_at":       time.Now().UTC().Format(time.RFC3339),
		"max_threshold":        10,
		"max_total_shares":     20,
		"default_retention":    2555, // days
		"supported_algorithms": []string{"Shamir-SSS", "DVSS-PPA"},
	}

	configJSON, err := json.Marshal(config)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState("DVSS_CONFIG", configJSON)
}

// RecordTransaction records a DVSS operation transaction
func (s *DVSSChaincode) RecordTransaction(ctx contractapi.TransactionContextInterface, txID string, transactionJSON string) error {
	var transaction Transaction
	err := json.Unmarshal([]byte(transactionJSON), &transaction)
	if err != nil {
		return fmt.Errorf("failed to unmarshal transaction: %v", err)
	}

	// Validate transaction data
	if transaction.TxID == "" || transaction.DataID == "" || transaction.UserID == "" {
		return fmt.Errorf("invalid transaction data: missing required fields")
	}

	// Set timestamp if not provided
	if transaction.Timestamp == "" {
		transaction.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}

	// Store transaction
	transactionJSON, err = json.Marshal(transaction)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(fmt.Sprintf("TX_%s", txID), transactionJSON)
	if err != nil {
		return err
	}

	// Update transaction history for data
	err = s.updateTransactionHistory(ctx, transaction.DataID, txID)
	if err != nil {
		return err
	}

	// Update user activity
	err = s.updateUserActivity(ctx, transaction.UserID, txID)
	if err != nil {
		return err
	}

	// Emit event
	eventPayload := map[string]interface{}{
		"tx_id":     txID,
		"data_id":   transaction.DataID,
		"operation": transaction.Operation,
		"user_id":   transaction.UserID,
		"timestamp": transaction.Timestamp,
	}
	eventJSON, _ := json.Marshal(eventPayload)
	ctx.GetStub().SetEvent("TransactionRecorded", eventJSON)

	return nil
}

// GetTransaction retrieves a transaction by ID
func (s *DVSSChaincode) GetTransaction(ctx contractapi.TransactionContextInterface, txID string) (*Transaction, error) {
	transactionJSON, err := ctx.GetStub().GetState(fmt.Sprintf("TX_%s", txID))
	if err != nil {
		return nil, fmt.Errorf("failed to read transaction %s: %v", txID, err)
	}
	if transactionJSON == nil {
		return nil, fmt.Errorf("transaction %s does not exist", txID)
	}

	var transaction Transaction
	err = json.Unmarshal(transactionJSON, &transaction)
	if err != nil {
		return nil, err
	}

	return &transaction, nil
}

// GetTransactionHistory gets all transactions for a data object
func (s *DVSSChaincode) GetTransactionHistory(ctx contractapi.TransactionContextInterface, dataID string) ([]Transaction, error) {
	historyJSON, err := ctx.GetStub().GetState(fmt.Sprintf("HISTORY_%s", dataID))
	if err != nil {
		return nil, fmt.Errorf("failed to read transaction history: %v", err)
	}

	var txIDs []string
	if historyJSON != nil {
		err = json.Unmarshal(historyJSON, &txIDs)
		if err != nil {
			return nil, err
		}
	}

	var transactions []Transaction
	for _, txID := range txIDs {
		transaction, err := s.GetTransaction(ctx, txID)
		if err != nil {
			continue // Skip failed transactions
		}
		transactions = append(transactions, *transaction)
	}

	return transactions, nil
}

// updateTransactionHistory updates the transaction history for a data object
func (s *DVSSChaincode) updateTransactionHistory(ctx contractapi.TransactionContextInterface, dataID string, txID string) error {
	historyKey := fmt.Sprintf("HISTORY_%s", dataID)
	historyJSON, err := ctx.GetStub().GetState(historyKey)
	if err != nil {
		return err
	}

	var txIDs []string
	if historyJSON != nil {
		err = json.Unmarshal(historyJSON, &txIDs)
		if err != nil {
			return err
		}
	}

	// Add new transaction ID
	txIDs = append(txIDs, txID)

	// Limit history size (keep last 1000 transactions)
	if len(txIDs) > 1000 {
		txIDs = txIDs[len(txIDs)-1000:]
	}

	updatedHistoryJSON, err := json.Marshal(txIDs)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(historyKey, updatedHistoryJSON)
}

// updateUserActivity updates user activity log
func (s *DVSSChaincode) updateUserActivity(ctx contractapi.TransactionContextInterface, userID string, txID string) error {
	activityKey := fmt.Sprintf("USER_ACTIVITY_%s", userID)
	activityJSON, err := ctx.GetStub().GetState(activityKey)
	if err != nil {
		return err
	}

	var activity map[string]interface{}
	if activityJSON != nil {
		err = json.Unmarshal(activityJSON, &activity)
		if err != nil {
			return err
		}
	} else {
		activity = make(map[string]interface{})
	}

	// Update activity counters
	if activity["total_transactions"] == nil {
		activity["total_transactions"] = 0
	}

	totalTx, _ := activity["total_transactions"].(float64)
	activity["total_transactions"] = totalTx + 1
	activity["last_activity"] = time.Now().UTC().Format(time.RFC3339)
	activity["last_tx_id"] = txID

	updatedActivityJSON, err := json.Marshal(activity)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(activityKey, updatedActivityJSON)
}

// RecordAccessLog records data access events
func (s *DVSSChaincode) RecordAccessLog(ctx contractapi.TransactionContextInterface, logJSON string) error {
	var accessLog AccessLog
	err := json.Unmarshal([]byte(logJSON), &accessLog)
	if err != nil {
		return fmt.Errorf("failed to unmarshal access log: %v", err)
	}

	// Validate log data
	if accessLog.LogID == "" || accessLog.DataID == "" || accessLog.UserID == "" {
		return fmt.Errorf("invalid access log: missing required fields")
	}

	// Set timestamp if not provided
	if accessLog.Timestamp == "" {
		accessLog.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}

	// Store access log
	logJSON, err = json.Marshal(accessLog)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(fmt.Sprintf("ACCESS_LOG_%s", accessLog.LogID), logJSON)
}

// RecordComplianceEvent records compliance-related events
func (s *DVSSChaincode) RecordComplianceEvent(ctx contractapi.TransactionContextInterface, eventJSON string) error {
	var event ComplianceEvent
	err := json.Unmarshal([]byte(eventJSON), &event)
	if err != nil {
		return fmt.Errorf("failed to unmarshal compliance event: %v", err)
	}

	// Validate event data
	if event.EventID == "" || event.DataID == "" {
		return fmt.Errorf("invalid compliance event: missing required fields")
	}

	// Set timestamp if not provided
	if event.Timestamp == "" {
		event.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}

	// Store compliance event
	eventJSON, err = json.Marshal(event)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(fmt.Sprintf("COMPLIANCE_%s", event.EventID), eventJSON)
	if err != nil {
		return err
	}

	// Emit compliance event
	eventPayload := map[string]interface{}{
		"event_id":   event.EventID,
		"event_type": event.EventType,
		"data_id":    event.DataID,
		"severity":   event.Severity,
		"timestamp":  event.Timestamp,
	}
	eventData, _ := json.Marshal(eventPayload)
	ctx.GetStub().SetEvent("ComplianceEventRecorded", eventData)

	return nil
}

// RecordIntegrityVerification records data integrity verification results
func (s *DVSSChaincode) RecordIntegrityVerification(ctx contractapi.TransactionContextInterface, verificationJSON string) error {
	var verification DataIntegrity
	err := json.Unmarshal([]byte(verificationJSON), &verification)
	if err != nil {
		return fmt.Errorf("failed to unmarshal integrity verification: %v", err)
	}

	// Validate verification data
	if verification.DataID == "" || verification.VerificationID == "" {
		return fmt.Errorf("invalid integrity verification: missing required fields")
	}

	// Set timestamp if not provided
	if verification.Timestamp == "" {
		verification.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}

	// Store verification result
	verificationJSON, err = json.Marshal(verification)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(fmt.Sprintf("INTEGRITY_%s", verification.VerificationID), verificationJSON)
}

// GetAccessStatistics generates access statistics for a data object
func (s *DVSSChaincode) GetAccessStatistics(ctx contractapi.TransactionContextInterface, dataID string, daysStr string) (map[string]interface{}, error) {
	days, err := strconv.Atoi(daysStr)
	if err != nil {
		return nil, fmt.Errorf("invalid days parameter: %v", err)
	}

	// Get transaction history
	transactions, err := s.GetTransactionHistory(ctx, dataID)
	if err != nil {
		return nil, err
	}

	// Calculate statistics
	cutoffTime := time.Now().UTC().AddDate(0, 0, -days)
	stats := map[string]interface{}{
		"data_id":        dataID,
		"period_days":    days,
		"total_accesses": 0,
		"unique_users":   make(map[string]bool),
		"operations":     make(map[string]int),
		"last_access":    "",
		"access_trend":   []int{},
	}

	uniqueUsers := make(map[string]bool)
	operations := make(map[string]int)
	var lastAccess time.Time

	for _, tx := range transactions {
		txTime, err := time.Parse(time.RFC3339, tx.Timestamp)
		if err != nil {
			continue
		}

		if txTime.After(cutoffTime) {
			stats["total_accesses"] = stats["total_accesses"].(int) + 1
			uniqueUsers[tx.UserID] = true
			operations[tx.Operation]++

			if txTime.After(lastAccess) {
				lastAccess = txTime
				stats["last_access"] = tx.Timestamp
			}
		}
	}

	stats["unique_users"] = len(uniqueUsers)
	stats["operations"] = operations

	return stats, nil
}

// QueryTransactionsByUser gets all transactions for a specific user
func (s *DVSSChaincode) QueryTransactionsByUser(ctx contractapi.TransactionContextInterface, userID string) ([]Transaction, error) {
	// Create a query string for CouchDB
	queryString := fmt.Sprintf(`{
		"selector": {
			"user_id": "%s"
		},
		"sort": [{"timestamp": "desc"}],
		"limit": 100
	}`, userID)

	resultsIterator, err := ctx.GetStub().GetQueryResult(queryString)
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var transactions []Transaction
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var transaction Transaction
		err = json.Unmarshal(queryResponse.Value, &transaction)
		if err != nil {
			return nil, err
		}

		transactions = append(transactions, transaction)
	}

	return transactions, nil
}

// GetSystemMetrics returns overall system metrics
func (s *DVSSChaincode) GetSystemMetrics(ctx contractapi.TransactionContextInterface) (map[string]interface{}, error) {
	// This would typically aggregate data from the ledger
	// For demonstration, we return mock metrics
	metrics := map[string]interface{}{
		"total_data_objects":      1000,
		"total_transactions":      5000,
		"active_users":            50,
		"average_integrity_score": 0.95,
		"compliance_violations":   2,
		"system_uptime":           "99.9%",
		"last_updated":            time.Now().UTC().Format(time.RFC3339),
	}

	return metrics, nil
}

// VerifyTransactionIntegrity verifies the integrity of a transaction
func (s *DVSSChaincode) VerifyTransactionIntegrity(ctx contractapi.TransactionContextInterface, txID string) (bool, error) {
	transaction, err := s.GetTransaction(ctx, txID)
	if err != nil {
		return false, err
	}

	// Verify signature (simplified - in real implementation would use proper cryptographic verification)
	if transaction.Signature == "" {
		return false, fmt.Errorf("transaction has no signature")
	}

	// Additional integrity checks can be added here
	return true, nil
}

func main() {
	dvssChaincode := new(DVSSChaincode)

	chaincode, err := contractapi.NewChaincode(dvssChaincode)
	if err != nil {
		panic(fmt.Sprintf("Error creating DVSS chaincode: %v", err))
	}

	if err := chaincode.Start(); err != nil {
		panic(fmt.Sprintf("Error starting DVSS chaincode: %v", err))
	}
}
