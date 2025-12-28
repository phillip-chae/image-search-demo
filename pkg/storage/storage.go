package storage

import (
	"context"
	"io"
)

type Storage interface {
	CreateBucket(ctx context.Context, bucketName string) error
	Upload(ctx context.Context, bucketName string, fileContent io.ReadSeeker, key string, extraArgs ...string) error
	Download(ctx context.Context, bucketName string, key string) (io.ReadCloser, error)
	Delete(ctx context.Context, bucketName string, key string) error
	IsExists(ctx context.Context, bucketName string, key string) (bool, error)
}
