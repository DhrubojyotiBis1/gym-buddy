package kafka

import (
	"WriterService/config"
	"WriterService/writer"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/IBM/sarama"
)

// Consumer handles Kafka message consumption
type Consumer struct {
	consumerGroup sarama.ConsumerGroup
	factory       *writer.WriterFactory
	ctx           context.Context
	cancel        context.CancelFunc
	wg            sync.WaitGroup
}

// NewConsumer creates a new Kafka consumer
func NewConsumer(factory *writer.WriterFactory, parent context.Context) (*Consumer, error) {
	env := config.MustLoad()

	cfg := sarama.NewConfig()
	cfg.Consumer.Group.Rebalance.Strategy = sarama.NewBalanceStrategyRoundRobin()

	// Set initial offset based on configuration
	// IMPORTANT: This setting only applies to NEW consumer groups or when no offset is committed.
	// For existing consumer groups with committed offsets, Kafka will automatically resume from
	// the last committed offset (which is the desired behavior for normal operation).
	//
	// To catch up on ALL messages from downtime:
	// Option 1: Use a NEW consumer group ID (change KAFKA_GROUP_ID)
	// Option 2: Reset offsets using Kafka CLI: kafka-consumer-groups --bootstrap-server localhost:9092 --group <group-id> --reset-offsets --to-earliest --topic <topic> --execute
	switch env.KafkaOffset {
	case "oldest":
		cfg.Consumer.Offsets.Initial = sarama.OffsetOldest
		log.Printf("Kafka consumer configured to start from OLDEST offset")
		log.Printf("Note: For existing consumer groups, Kafka resumes from last committed offset.")
		log.Printf("To reprocess all messages, use a new KAFKA_GROUP_ID or reset offsets manually.")
	case "newest":
		cfg.Consumer.Offsets.Initial = sarama.OffsetNewest
		log.Printf("Kafka consumer configured to start from NEWEST offset (only new messages)")
	default:
		cfg.Consumer.Offsets.Initial = sarama.OffsetOldest
		log.Printf("Invalid KAFKA_OFFSET value '%s', defaulting to 'oldest'", env.KafkaOffset)
	}

	// Enable auto-commit for offset tracking
	cfg.Consumer.Offsets.AutoCommit.Enable = true
	cfg.Consumer.Offsets.AutoCommit.Interval = 1 * time.Second

	cfg.Version = sarama.V2_8_0_0

	consumerGroup, err := sarama.NewConsumerGroup(
		[]string{env.KafkaBrokers},
		env.KafkaGroupID,
		cfg,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create consumer group: %w", err)
	}
	log.Printf("Kafka connected with group ID: %s", env.KafkaGroupID)
	// ctx, cancel := context.WithCancel(context.Background())
	ctx, cancel := context.WithCancel(parent)
	return &Consumer{
		consumerGroup: consumerGroup,
		factory:       factory,
		ctx:           ctx,
		cancel:        cancel,
	}, nil
}

// Start starts consuming messages from Kafka
func (c *Consumer) Start(topics []string) error {
	c.wg.Add(1)
	go func() {
		defer c.wg.Done()
		for {

			if c.ctx.Err() != nil {
				log.Println("Consumer context cancelled, stopping...")
				return
			}

			handler := &consumerGroupHandler{
				factory: c.factory,
			}

			// This call blocks while consuming; it will return when
			// ctx is canceed ollr there is an error / rebalance.
			if err := c.consumerGroup.Consume(c.ctx, topics, handler); err != nil {
				log.Printf("Error from consumer: %v", err)

				if c.ctx.Err() != nil {
					return
				}

				time.Sleep(5 * time.Second)
				continue
				// log.Printf("Error from consumer group connections: %v", err)
				// In some setups you might want to continue on some errors and retry.
				// return
			}
		}
	}()

	// log.Printf("Started Kafka consumer for topics: %v", topics)
	return nil
}

// Stop stops the consumer
func (c *Consumer) Stop() error {
	c.cancel()
	c.wg.Wait()
	return c.consumerGroup.Close()
}

// consumerGroupHandler implements sarama.ConsumerGroupHandler
type consumerGroupHandler struct {
	factory *writer.WriterFactory
}

// Setup is run at the beginning of a new session, before ConsumeClaim
func (h *consumerGroupHandler) Setup(k sarama.ConsumerGroupSession) error {
	log.Println("Consumer is successfully connected")
	return nil
}

// Cleanup is run at the end of a session, once all ConsumeClaim goroutines have exited
func (h *consumerGroupHandler) Cleanup(sarama.ConsumerGroupSession) error {
	log.Println("stopped")
	return nil
}

// ConsumeClaim must start a consumer loop of ConsumerGroupClaim's Messages()
func (h *consumerGroupHandler) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
	log.Println("partition - ", claim.Partition(), ": topic - ", claim.Topic())
	for {
		select {
		case message := <-claim.Messages():
			if message == nil {
				return nil
			}

			// Log message receipt
			log.Printf("Received message from Kafka - Topic: %s, Partition: %d, Offset: %d, Key: %s, Value: %s",
				message.Topic, message.Partition, message.Offset, string(message.Key), string(message.Value))

			// Parse JSON message
			var data map[string]interface{}
			if err := json.Unmarshal(message.Value, &data); err != nil {
				log.Printf("Error unmarshaling message: %v", err)
				session.MarkMessage(message, "")
				continue
			}

			// Extract writeIn field
			writeIn, ok := data["writeIn"].(string)
			if !ok {
				log.Printf("Missing or invalid 'writeIn' field in message, skipping")
				session.MarkMessage(message, "")
				continue
			}

			// Get appropriate writer strategy
			writerStrategy, err := h.factory.GetWriter(writeIn)
			if err != nil {
				log.Printf("Error getting writer strategy: %v", err)
				session.MarkMessage(message, "")
				continue
			}

			// Write data using the selected strategy
			if err := writerStrategy.Write(data); err != nil {
				log.Printf("Error writing data: %v", err)
				// You might want to handle retries or dead letter queue here
			} else {
				log.Printf("Successfully processed message with writeIn=%s", writeIn)
			}

			session.MarkMessage(message, "")

		case <-session.Context().Done():
			return nil
		}
	}
}
