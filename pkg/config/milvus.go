package config

import (
	"time"
)

const (
	MILVUSDB_HOST     = "MILVUSDB_HOST"
	MILVUSDB_PORT     = "MILVUSDB_PORT"
	MILVUSDB_USERNAME = "MILVUSDB_USERNAME"
	MILVUSDB_PASSWORD = "MILVUSDB_PASSWORD"
)

type MilvusConfig struct {
	Host            string
	Port            int
	SSL             bool
	Username        string
	Password        string
	Timeout         time.Duration
	FlushInterval   time.Duration
	MaxConnIdleTime time.Duration
	MaxPoolSize     uint64
	MinPoolSize     uint64
}

func NewDefaultMilvusConfig() MilvusConfig {
	return MilvusConfig{
		Host:            "127.0.0.1",
		Port:            19530,
		SSL:             false,
		Username:        "",
		Password:        "",
		MaxConnIdleTime: 15,
		FlushInterval:   300,
		MaxPoolSize:     100,
		MinPoolSize:     1,
		Timeout:         10,
	}
}
