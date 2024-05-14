// main.go

package main

import (
	"babel/backend/api"
	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Define authentication endpoints
	router.POST("/register", api.Register)
	router.POST("/login", api.Login)
	router.GET("/profile", api.Profile)

	// Define content management endpoints
	router.POST("/posts", api.CreatePost)
	router.GET("/posts/:id", api.GetPost)
	router.PUT("/posts/:id", api.UpdatePost)
	router.DELETE("/posts/:id", api.DeletePost)

	router.POST("/posts/:id/comments", api.CreateComment)
	router.GET("/posts/:id/comments/:comment_id", api.GetComment)
	router.PUT("/posts/:id/comments/:comment_id", api.UpdateComment)
	router.DELETE("/posts/:id/comments/:comment_id", api.DeleteComment)

	// Run the server
	router.Run(":8080")
}
