package main

import (
	"fmt"
	"log"
	"production-demo/cdnapi/config"
	"production-demo/cdnapi/handler/api"
	"production-demo/cdnapi/router"
	"production-demo/cdnapi/service"
	pkgConfig "production-demo/pkg/config"

	_ "production-demo/cdnapi/docs"
)

// @title           CDN API
// @version         1.0
// @description     Simple CDN API for serving images.
// @BasePath        /

func main() {
	// Load config
	var cfg config.Config
	config := pkgConfig.NewBasicConfig()

	// Load from conf/cdnapi.yaml and override with env vars starting with CDNAPI_
	// e.g. CDNAPI_STORAGE_HOST -> storage.host
	if err := config.Load("conf/cdnapi.yaml", "", &cfg); err != nil {
		log.Printf("Failed to load config: %v, using defaults", err)
	}

	// Initialize Service
	// Assuming bucket name is in config or default
	bucketName := cfg.Bucket
	if bucketName == "" {
		bucketName = "images"
	}

	imageService := service.NewImageService(&cfg)

	// Initialize Handler
	imageHandler := api.NewImageHandler(imageService)

	// Initialize Router
	r := router.NewRouter(imageHandler)

	// Run Server
	port := cfg.Server.Port
	if port == 0 {
		port = 8000
	}

	addr := fmt.Sprintf(":%d", port)
	log.Printf("Starting CDN API on %s", addr)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
