package api

import (
	"log"

	"github.com/gin-gonic/gin"
)

// LoggerMiddleware logs all incoming requests
func LoggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		log.Printf("%s %s %s", c.ClientIP(), c.Request.Method, c.Request.URL)
		c.Next()
	}
}

// AuthMiddleware handles request authentication
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if !authenticated(c) {
			c.AbortWithStatusJSON(401, gin.H{"error": "Unauthorized"})
			return
		}
		c.Next()
	}
}

// CORSMiddleware handles Cross-Origin Resource Sharing
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(200)
			return
		}

		c.Next()
	}
}

// authenticated checks if the request is authenticated
func authenticated(c *gin.Context) bool {
	// TODO: Implement proper authentication with Hedera
	return true
}
