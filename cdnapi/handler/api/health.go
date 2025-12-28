package api

import "github.com/gin-gonic/gin"

type HealthHandler struct{}

type HealthResponse struct {
	Status string `json:"status"`
}

func NewHealthHandler() *HealthHandler {
	return &HealthHandler{}
}

// GetHealth godoc
// @Summary     Health check
// @Description Returns service health status
// @Tags        health
// @Produce     json
// @Success     200 {object} api.HealthResponse
// @Router      /health [get]
func (h *HealthHandler) GetHealth(c *gin.Context) {
	c.JSON(200, HealthResponse{Status: "ok"})
}
