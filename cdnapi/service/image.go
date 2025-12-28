package service

import (
	"bytes"
	"context"
	"io"
	"net/http"
	"production-demo/cdnapi/config"
	"production-demo/pkg/storage"
)

type ImageService interface {
	GetImage(ctx context.Context, imageID string) (io.ReadCloser, string, error)
}

type imageService struct {
	cfg *config.Config
	s3  storage.Storage
}

func NewImageService(cfg *config.Config) ImageService {

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	s3 := storage.NewS3Storage(&cfg.Storage)
	if err := s3.CheckConnection(ctx, cfg.Bucket); err != nil {
		panic("Failed to connect to storage: " + err.Error())
	}

	return &imageService{
		cfg: cfg,
		s3:  s3,
	}
}

func (s *imageService) GetImage(ctx context.Context, imageID string) (io.ReadCloser, string, error) {
	// Assuming imageID is the key in the bucket
	// We might need to determine content type, but minio GetObject usually has info.
	// The storage.Download returns io.ReadCloser.
	// We might want to get content type if possible, but the current storage interface doesn't return metadata on Download.
	// We can just return the reader and let Gin sniff it or just serve it.

	reader, err := s.s3.Download(ctx, s.cfg.Bucket, imageID)
	if err != nil {
		return nil, "", err
	}

	// Sniff the content type from the first 512 bytes (same behavior as net/http).
	buf := make([]byte, 512)
	n, readErr := reader.Read(buf)
	if readErr != nil && readErr != io.EOF {
		_ = reader.Close()
		return nil, "", readErr
	}

	contentType := ""
	if n > 0 {
		contentType = http.DetectContentType(buf[:n])
	}

	// Put the bytes back in front so callers still get the full stream.
	stream := io.MultiReader(bytes.NewReader(buf[:n]), reader)
	return struct {
		io.Reader
		io.Closer
	}{Reader: stream, Closer: reader}, contentType, nil
}
