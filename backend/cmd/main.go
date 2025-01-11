package main

import (
	"log"

	"github.com/saint/babel-protocol/backend/internal/websocket"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize WebSocket hub
	hub := websocket.NewWebSocketHub()
	go hub.Run()

	// Set up Gin router
	router := gin.Default()

	// WebSocket endpoint
	router.GET("/ws", func(c *gin.Context) {
		hub.HandleWebSocket(c)
	})

	// Start server
	if err := router.Run(":8080"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
