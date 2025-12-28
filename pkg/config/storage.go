package config

const (
	STORAGE_S3    uint32 = 0
	STORAGE_MINIO uint32 = 1
)

const (
	STORAGE_HOST = "STORAGE_HOST"
	STORAGE_PORT = "STORAGE_PORT"
)

type StorageConfig struct {
	Type         uint32
	Region       string
	Host         string
	Port         int
	SSL          bool
	AccessKey    string
	SecretKey    string
	BucketPrefix string
}

func NewDefaultStorageConfig() StorageConfig {
	return StorageConfig{
		Type:         STORAGE_S3,
		Region:       "",
		Host:         "",
		Port:         0,
		SSL:          false,
		AccessKey:    "",
		SecretKey:    "",
		BucketPrefix: "",
	}
}
