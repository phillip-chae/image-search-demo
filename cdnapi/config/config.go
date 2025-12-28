package config

import (
	"production-demo/pkg/config"
)

type Config struct {
	Logger  config.LoggerConfig
	Storage config.StorageConfig `mapstructure:"storage"`
	Server  ServerConfig         `mapstructure:"server"`
	Bucket  string               `mapstructure:"bucket"`
}

type ServerConfig struct {
	Port int `mapstructure:"port"`
}
