package storage

import (
	"bytes"
	"context"
	"errors"
	"io"
	"production-demo/pkg/config"
	"strconv"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
)

var (
	ErrBucketNameRequired = errors.New("bucket name is required")
)

type s3Storage struct {
	cfg *config.StorageConfig
}

func NewS3Storage(cfg *config.StorageConfig) *s3Storage {
	return &s3Storage{
		cfg: cfg,
	}
}

func (s *s3Storage) region() string {
	// The AWS SDK requires a non-empty region for request signing.
	// For MinIO/S3-compatible endpoints, "us-east-1" is the conventional default.
	if strings.TrimSpace(s.cfg.Region) == "" {
		return "us-east-1"
	}
	return s.cfg.Region
}

func (s *s3Storage) endpointURL() string {
	scheme := "http"
	if s.cfg.SSL {
		scheme = "https"
	}

	host := s.cfg.Host
	if strings.Contains(host, "://") {
		parts := strings.SplitN(host, "://", 2)
		host = parts[1]
	}

	port := ""
	if s.cfg.Port != 0 {
		port = ":" + strconv.Itoa(s.cfg.Port)
	}

	return scheme + "://" + host + port
}

func (s *s3Storage) newS3Client(_ context.Context) (*s3.S3, error) {
	endpoint := s.endpointURL()
	forcePathStyle := false
	// If a custom host/port is provided (MinIO, localstack, etc.), path style is usually required.
	if s.cfg.Port != 0 || (s.cfg.Host != "" && !strings.Contains(s.cfg.Host, "amazonaws.com")) {
		forcePathStyle = true
	}

	s3cfg := &aws.Config{
		Region:           aws.String(s.region()),
		Endpoint:         aws.String(endpoint),
		DisableSSL:       aws.Bool(!s.cfg.SSL),
		S3ForcePathStyle: aws.Bool(forcePathStyle),
		Credentials:      credentials.NewStaticCredentials(s.cfg.AccessKey, s.cfg.SecretKey, ""),
	}

	sess, err := session.NewSession(s3cfg)
	if err != nil {
		return nil, err
	}
	return s3.New(sess), nil
}

func (s *s3Storage) isBucketNotFound(err error) bool {
	aerr, ok := err.(awserr.Error)
	if !ok {
		return false
	}
	switch aerr.Code() {
	case s3.ErrCodeNoSuchBucket, "NotFound":
		return true
	default:
		return false
	}
}

func (s *s3Storage) isObjectNotFound(err error) bool {
	aerr, ok := err.(awserr.Error)
	if !ok {
		return false
	}
	switch aerr.Code() {
	case s3.ErrCodeNoSuchKey, "NotFound":
		return true
	default:
		return false
	}
}

func (s *s3Storage) CreateBucket(ctx context.Context, bucketName string) error {
	client, err := s.newS3Client(ctx)
	if err != nil {
		return err
	}

	input := &s3.CreateBucketInput{Bucket: aws.String(bucketName)}
	// AWS requires LocationConstraint for most regions except us-east-1.
	if strings.TrimSpace(s.cfg.Region) != "" && s.cfg.Region != "us-east-1" {
		input.CreateBucketConfiguration = &s3.CreateBucketConfiguration{
			LocationConstraint: aws.String(s.cfg.Region),
		}
	}

	_, err = client.CreateBucketWithContext(ctx, input)
	return err
}

func (s *s3Storage) ensureBucket(ctx context.Context, bucketName string) error {
	if bucketName == "" {
		return ErrBucketNameRequired
	}
	if err := s.CheckConnection(ctx, bucketName); err == nil {
		return nil
	} else if s.isBucketNotFound(err) {
		return s.CreateBucket(ctx, bucketName)
	} else {
		return err
	}
}

func (s *s3Storage) CheckConnection(ctx context.Context, bucketName string) error {
	if bucketName == "" {
		return ErrBucketNameRequired
	}
	client, err := s.newS3Client(ctx)
	if err != nil {
		return err
	}

	input := &s3.HeadBucketInput{
		Bucket: aws.String(bucketName),
	}
	if _, err := client.HeadBucketWithContext(ctx, input); err != nil {
		return err
	}
	return nil
}

func (s *s3Storage) Upload(ctx context.Context, bucketName string, fileContent io.ReadSeeker, key string, extraArgs ...string) error {
	if bucketName == "" {
		return ErrBucketNameRequired
	}
	if key == "" {
		return errors.New("key is required")
	}
	client, err := s.newS3Client(ctx)
	if err != nil {
		return err
	}

	input := &s3.PutObjectInput{
		Body:   fileContent,
		Bucket: aws.String(bucketName),
		Key:    aws.String(key),
	}

	m := map[string]*string{}
	for _, val := range extraArgs {
		s := strings.Split(val, ";")
		if len(s) == 2 {
			key := s[0]
			value := aws.String(s[1])
			m[key] = value
		}
	}
	if len(m) > 0 {
		input.Metadata = m
	}

	if _, err := client.PutObjectWithContext(ctx, input); err != nil {
		// Mirror Python behavior: if bucket is missing, create it and retry once.
		if s.isBucketNotFound(err) {
			if berr := s.ensureBucket(ctx, bucketName); berr == nil {
				if _, rerr := client.PutObjectWithContext(ctx, input); rerr == nil {
					return nil
				}
			}
		}
		return err
	}

	return nil
}

func (s *s3Storage) Download(ctx context.Context, bucketName string, key string) (io.ReadCloser, error) {
	if bucketName == "" {
		return nil, ErrBucketNameRequired
	}
	if key == "" {
		return nil, errors.New("key is required")
	}
	client, err := s.newS3Client(ctx)
	if err != nil {
		return nil, err
	}

	input := &s3.GetObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(key),
	}

	result, err := client.GetObjectWithContext(ctx, input)
	if err != nil {
		// Mirror Python behavior: if bucket is missing, create it and retry once.
		if s.isBucketNotFound(err) {
			if berr := s.ensureBucket(ctx, bucketName); berr == nil {
				result2, rerr := client.GetObjectWithContext(ctx, input)
				if rerr == nil {
					return result2.Body, nil
				}
				return nil, rerr
			}
		}
		return nil, err
	}

	return result.Body, nil
}

func (s *s3Storage) IsExists(ctx context.Context, bucketName string, key string) (bool, error) {
	if bucketName == "" {
		return false, ErrBucketNameRequired
	}
	if key == "" {
		return false, errors.New("key is required")
	}
	client, err := s.newS3Client(ctx)
	if err != nil {
		return false, err
	}

	input := &s3.HeadObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(key),
	}

	if _, err := client.HeadObjectWithContext(ctx, input); err != nil {
		if s.isObjectNotFound(err) {
			return false, nil
		}
		if s.isBucketNotFound(err) {
			// In Python, existence checks simply return False on failure.
			// Here we attempt to create the bucket if missing, then re-check.
			if berr := s.ensureBucket(ctx, bucketName); berr == nil {
				_, rerr := client.HeadObjectWithContext(ctx, input)
				if rerr == nil {
					return true, nil
				}
				if s.isObjectNotFound(rerr) {
					return false, nil
				}
				return false, rerr
			}
		}
		return false, err
	}
	return true, nil
}

func (s *s3Storage) Delete(ctx context.Context, bucketName string, key string) error {
	if bucketName == "" {
		return ErrBucketNameRequired
	}
	if key == "" {
		return errors.New("key is required")
	}
	client, err := s.newS3Client(ctx)
	if err != nil {
		return err
	}

	input := &s3.DeleteObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(key),
	}
	if _, err := client.DeleteObjectWithContext(ctx, input); err != nil {
		if s.isBucketNotFound(err) {
			// If bucket doesn't exist, create it (Python sometimes autocreates) and retry.
			if berr := s.ensureBucket(ctx, bucketName); berr == nil {
				_, _ = client.DeleteObjectWithContext(ctx, input)
			}
		}
		return err
	}
	return nil
}

// Helpers for callers that have byte slices (matches the Python wrapper ergonomics)
func (s *s3Storage) UploadBytes(ctx context.Context, bucketName string, content []byte, key string, meta ...string) error {
	return s.Upload(ctx, bucketName, bytes.NewReader(content), key, meta...)
}
