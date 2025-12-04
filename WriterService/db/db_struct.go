package db

import (
	"time"
)

type Message struct {
	ID            uint    `gorm:"primaryKey"`
	Text          *string `gorm:"type:text"` // nullable
	HasAttachment bool    `gorm:"not null;default:false"`
	Visible       bool    `gorm:"not null;default:true"`

	CreatedAt time.Time `gorm:"not null;default:now()"`
	UpdatedAt time.Time `gorm:"not null;default:now()"`

	SenderID       uint `gorm:"not null"`
	ConversationID uint `gorm:"not null"`
}

// Explicit table name if you want "messages" specifically
func (Message) TableName() string {
	return "messages"
}
