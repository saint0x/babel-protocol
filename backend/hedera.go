package api

import (
	"github.com/hashgraph/hedera-sdk-go/v2"
)

// HederaClient manages Hedera network interactions
type HederaClient struct {
	client *hedera.Client
}

// NewHederaClient creates a new Hedera client
func NewHederaClient(accountID string, privateKey string) (*HederaClient, error) {
	client := hedera.ClientForTestnet()
	operatorID, err := hedera.AccountIDFromString(accountID)
	if err != nil {
		return nil, err
	}

	operatorKey, err := hedera.PrivateKeyFromString(privateKey)
	if err != nil {
		return nil, err
	}

	client.SetOperator(operatorID, operatorKey)
	return &HederaClient{client: client}, nil
}

// CreateTopic creates a new consensus topic
func (h *HederaClient) CreateTopic() (*hedera.TopicID, error) {
	txResponse, err := hedera.NewTopicCreateTransaction().
		Execute(h.client)
	if err != nil {
		return nil, err
	}

	receipt, err := txResponse.GetReceipt(h.client)
	if err != nil {
		return nil, err
	}

	return receipt.TopicID, nil
}

// SubmitMessage submits a message to a consensus topic
func (h *HederaClient) SubmitMessage(topicID hedera.TopicID, message []byte) error {
	_, err := hedera.NewTopicMessageSubmitTransaction().
		SetTopicID(topicID).
		SetMessage(message).
		Execute(h.client)
	return err
}

// SubscribeToTopic subscribes to messages on a topic
func (h *HederaClient) SubscribeToTopic(topicID hedera.TopicID, callback func([]byte)) error {
	_, err := hedera.NewTopicMessageQuery().
		SetTopicID(topicID).
		Subscribe(h.client, func(message hedera.TopicMessage) {
			callback(message.Contents)
		})
	return err
}
