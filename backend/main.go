package api

import (
	"log"

	"github.com/gin-gonic/gin"
)

func main() {
	// Load configuration
	config, err := LoadConfig("config.json")
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	// Initialize Hedera client
	hederaClient, err := NewHederaClient(config.HederaAccountID, config.HederaPrivateKey)
	if err != nil {
		log.Fatalf("Error initializing Hedera client: %v", err)
	}

	// Initialize WebSocket hub
	hub := NewWebSocketHub()
	go hub.Run()

	// Create Gin router
	router := gin.Default()

	// Apply middleware
	router.Use(LoggerMiddleware())
	router.Use(CORSMiddleware())
	router.Use(AuthMiddleware())

	// Set up WebSocket route
	router.GET("/ws", gin.WrapF(hub.HandleWebSocket))

	// Set up API routes
	api := router.Group("/api")
	setupAPIRoutes(api, hederaClient, hub)

	// Start server
	port := config.Port
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}

func setupAPIRoutes(router *gin.RouterGroup, hederaClient *HederaClient, hub *WebSocketHub) {
	// Content routes
	router.POST("/content", CreateContentHandler(hederaClient))
	router.GET("/content/:id", GetContentHandler(hederaClient))
	router.POST("/content/:id/vote", VoteContentHandler(hederaClient, hub))
	router.POST("/content/:id/evidence", AddEvidenceHandler(hederaClient, hub))

	// User routes
	router.GET("/user/profile", GetUserProfileHandler())
	router.GET("/user/reputation", GetUserReputationHandler())

	// Analytics routes
	router.GET("/analytics/content/:id", GetContentAnalyticsHandler())
	router.GET("/analytics/trending", GetTrendingContentHandler())
}
