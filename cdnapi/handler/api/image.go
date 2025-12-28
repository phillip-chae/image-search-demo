package api

import (
	"net/http"
	"production-demo/cdnapi/service"

	"github.com/gin-gonic/gin"
)

type ImageHandler struct {
	svc service.ImageService
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func NewImageHandler(svc service.ImageService) *ImageHandler {
	return &ImageHandler{
		svc: svc,
	}
}

// GetImage godoc
// @Summary     Get image by ID
// @Description Streams the raw image bytes and sets Content-Type based on detected image format.
// @Tags        images
// @Produce     image/jpeg
// @Produce     image/png
// @Produce     image/gif
// @Produce     image/avif
// @Produce     image/webp
// @Produce     application/octet-stream
// @Param       image_id path string true "Image ID"
// @Success     200 {file} file "Image file"
// @Failure     400 {object} api.ErrorResponse
// @Failure     404 {object} api.ErrorResponse
// @Router      /images/{image_id} [get]
func (h *ImageHandler) GetImage(c *gin.Context) {
	imageID := c.Param("image_id")
	if imageID == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "image_id is required"})
		return
	}

	reader, contentType, err := h.svc.GetImage(c.Request.Context(), imageID)
	if err != nil {
		// Check if it's a not found error
		// For now just return 404 or 500
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "Image not found or error retrieving it"})
		return
	}
	defer reader.Close()

	if contentType == "" {
		contentType = "application/octet-stream"
	}

	extraHeaders := map[string]string{
		"Content-Disposition": "inline",
	}

	c.DataFromReader(http.StatusOK, -1, contentType, reader, extraHeaders)
}
