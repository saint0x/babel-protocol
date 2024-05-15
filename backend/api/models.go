package api

// PostRequest represents a request to create a new post.
type PostRequest struct {
  UserID  string `json:"user_id"`
  Content string `json:"content"`
}

// PostResponse represents a response from creating a new post.
type PostResponse struct {
  PostID string `json:"post_id"`
}

// CommentRequest represents a request to add a comment to a post.
type CommentRequest struct {
  UserID  string `json:"user_id"`
  PostID  string `json:"post_id"`
  Content string `json:"content"`
}

// CommentResponse represents a response from adding a comment to a post.
type CommentResponse struct {
  CommentID string `json:"comment_id"`
}

// LikeRequest represents a request to like a post.
type LikeRequest struct {
  UserID string `json:"user_id"`
  PostID string `json:"post_id"`
}

// DislikeRequest represents a request to dislike a post.
type DislikeRequest struct {
  UserID string `json:"user_id"`
  PostID string `json:"post_id"`
}
