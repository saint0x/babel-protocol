package api

import (
  "encoding/json"
  "net/http"
)

// CreatePostHandler handles the creation of a new post
func CreatePostHandler(w http.ResponseWriter, r *http.Request) {
  var postReq PostRequest
  err := json.NewDecoder(r.Body).Decode(&postReq)
  if err != nil {
    http.Error(w, err.Error(), http.StatusBadRequest)
    return
  }

  postResp, err := CreatePost(postReq)
  if err != nil {
    http.Error(w, "Failed to create post", http.StatusInternalServerError)
    return
  }

  resp, err := json.Marshal(postResp)
  if err != nil {
    http.Error(w, err.Error(), http.StatusInternalServerError)
    return
  }

  w.Header().Set("Content-Type", "application/json")
  w.WriteHeader(http.StatusOK)
  w.Write(resp)
}

// AddCommentHandler handles the addition of a comment to a post
func AddCommentHandler(w http.ResponseWriter, r *http.Request) {
  var commentReq CommentRequest
  err := json.NewDecoder(r.Body).Decode(&commentReq)
  if err != nil {
    http.Error(w, err.Error(), http.StatusBadRequest)
    return
  }

  commentResp, err := AddComment(commentReq)
  if err != nil {
    http.Error(w, "Failed to add comment", http.StatusInternalServerError)
    return
  }

  resp, err := json.Marshal(commentResp)
  if err != nil {
    http.Error(w, err.Error(), http.StatusInternalServerError)
    return
  }

  w.Header().Set("Content-Type", "application/json")
  w.WriteHeader(http.StatusOK)
  w.Write(resp)
}

// LikePostHandler handles the liking of a post
func LikePostHandler(w http.ResponseWriter, r *http.Request) {
  var likeReq LikeRequest
  err := json.NewDecoder(r.Body).Decode(&likeReq)
  if err != nil {
    http.Error(w, err.Error(), http.StatusBadRequest)
    return
  }

  err = LikePost(likeReq)
  if err != nil {
    http.Error(w, "Failed to like post", http.StatusInternalServerError)
    return
  }

  w.WriteHeader(http.StatusOK)
}

// DislikePostHandler handles the disliking of a post
func DislikePostHandler(w http.ResponseWriter, r *http.Request) {
  var dislikeReq DislikeRequest
  err := json.NewDecoder(r.Body).Decode(&dislikeReq)
  if err != nil {
    http.Error(w, err.Error(), http.StatusBadRequest)
    return
  }

  err = DislikePost(dislikeReq)
  if err != nil {
    http.Error(w, "Failed to dislike post", http.StatusInternalServerError)
    return
  }

  w.WriteHeader(http.StatusOK)
}

// LoginHandler handles user login requests.
func LoginHandler(w http.ResponseWriter, r *http.Request) {
  // Login logic goes here
}

// LogoutHandler handles user logout requests.
func LogoutHandler(w http.ResponseWriter, r *http.Request) {
  // Logout logic goes here
}

// ProfileHandler handles user profile requests.
func ProfileHandler(w http.ResponseWriter, r *http.Request) {
  // Profile logic goes here
}
