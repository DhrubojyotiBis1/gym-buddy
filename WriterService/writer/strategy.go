package writer

// WriterStrategy defines the interface for different writing strategies
type WriterStrategy interface {
	Write(data map[string]interface{}) error
}
