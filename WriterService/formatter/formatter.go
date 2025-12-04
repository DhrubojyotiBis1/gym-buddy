package formatter

import "time"

type TimeConfig struct {
	TimeLayout string
}

var cfg = TimeConfig{
	TimeLayout: "2006-01-02 15:04:05",
}
var t = time.Now()

func Format() {

}

type Message struct {
	ID             int       `db:"id" json:"id"`
	Body           *string   `db:"body" json:"body,omitempty"` // nullable in DB
	HasAttachment  bool      `db:"has_attachment" json:"has_attachment"`
	Visible        bool      `db:"visible" json:"visible"`
	CreatedAt      time.Time `db:"created_at" json:"created_at"`
	UpdatedAt      time.Time `db:"updated_at" json:"updated_at"`
	SenderID       int       `db:"sender_id" json:"sender_id"`
	ConversationID int       `db:"conversation_id" json:"conversation_id"`
}
