package router

import (
	"production-demo/cdnapi/handler/api"

	"github.com/gin-gonic/gin"

	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

func NewRouter(imageHandler *api.ImageHandler) *gin.Engine {
	r := gin.Default()

	// Swagger UI
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	r.GET("/images/:image_id", imageHandler.GetImage)

	// Health check
	healthHandler := api.NewHealthHandler()
	r.GET("/health", healthHandler.GetHealth)

	return r
}
