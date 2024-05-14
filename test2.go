// test2.go

package main

import (
    "fmt"
    "log"
    "os"

    "golang.org/x/crypto/bcrypt"
    "github.com/go-yaml/yaml"
)

type Database struct {
    Users map[string]User `yaml:"users"`
}

type User struct {
    Username string `yaml:"username"`
    Password string `yaml:"password"`
    Bio      string `yaml:"bio"`
}

func main() {
    // Read data from database.yaml
    data, err := readDatabaseFromFile()
    if err != nil {
        log.Fatal(err)
    }

    // Test login functionality
    username := "user1"
    password := "password1"
    if authenticateUser(data, username, password) {
        // Authentication successful, print user profile
        fmt.Println("Login successful!")
        fmt.Println("User Profile:")
        fmt.Println("Username:", data.Users[username].Username)
        fmt.Println("Bio:", data.Users[username].Bio)
    } else {
        fmt.Println("Login failed: invalid username or password")
    }
}

func readDatabaseFromFile() (Database, error) {
    var data Database

    // Open database.yaml file
    file, err := os.Open("database.yaml")
    if err != nil {
        return data, err
    }
    defer file.Close()

    // Decode YAML data from file
    decoder := yaml.NewDecoder(file)
    if err := decoder.Decode(&data); err != nil {
        return data, err
    }

    return data, nil
}

func authenticateUser(data Database, username, password string) bool {
    // Check if username exists in the database
    user, ok := data.Users[username]
    if !ok {
        return false // Username not found
    }

    // Compare hashed password with the provided password
    if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(password)); err != nil {
        return false // Password does not match
    }

    return true // Authentication successful
}
