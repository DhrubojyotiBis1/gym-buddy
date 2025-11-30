package db

import (
	"WriterService/config"
	"fmt"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type gormDbInstance struct {
	Pool *gorm.DB
}

var globalDBVar *gormDbInstance

func InitTable() (*gormDbInstance, error) {
	env := config.MustLoad()
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable", env.DbHost, env.DbUserName, env.DbPassword, "gym_buddy", env.DbPort)
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}
	// This will create / update the `messages` table schema
	exists := db.Migrator().HasTable(Message{})
	if !exists {
		if err := db.AutoMigrate(&Message{}); err != nil {
			log.Println("not able to create messages db")
		}
		log.Println("created message table")
	} else {
		log.Println("table already exists.")
	}
	log.Println("Successfully connected to DB")
	globalDBVar = &gormDbInstance{Pool: db}
	return globalDBVar, nil
}

func GlobalDBFunc() *gormDbInstance {
	return globalDBVar
}

func (gb gormDbInstance) CloseDb() {
	if gb.Pool != nil {
		sqlDB, err := gb.Pool.DB()
		if err != nil {
			log.Println("unable to close the db connection")
		}
		sqlDB.Close()
	}
}
