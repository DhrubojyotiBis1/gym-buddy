// DBWriter implements WriterStrategy for writing to PostgreSQL database
package writer

import (
	"WriterService/db"
	"log"

	"gorm.io/gorm"
)

type DBWriter struct {
	pool *gorm.DB
}

// NewDBWriter creates a new DBWriter instance and ensures the table exists
func NewDBWriter(pool *gorm.DB) *DBWriter {
	dw := &DBWriter{
		pool: pool,
	}
	return dw
}

// Write writes data to the database
func (dw *DBWriter) Write(data map[string]interface{}) error {
	delete(data, "writeIn")
	if err := dw.pool.Model(&db.Message{}).Create(&data).Error; err != nil {
		log.Println("Error writing data:", err)
		return err
	} else {
		log.Println("Inserted row from map")
	}
	return nil
}
