// test.go

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
    // Sample data
    sampleData := Database{
        Users: map[string]User{
            "user1": {Username: "user1", Password: hashPassword("password1"), Bio: "Hello, I'm user1!"},
            "user2": {Username: "user2", Password: hashPassword("password2"), Bio: "Hey there, I'm user2!"},
        },
    }

    // Write sample data to database.yaml
    writeDatabaseToFile(sampleData)

    // Log success message
    fmt.Println("Sample data written to database.yaml successfully!")
}

func hashPassword(password string) string {
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    if err != nil {
        log.Fatal(err)
    }
    return string(hashedPassword)
}

func writeDatabaseToFile(data Database) {
    // Encode data to YAML
    yamlData, err := yaml.Marshal(data)
    if err != nil {
        log.Fatal(err)
    }

    // Write YAML data to database.yaml file
    filename := "database.yaml"
    if _, err := os.Stat(filename); os.IsNotExist(err) {
        // File does not exist, create a new file
        if err := os.WriteFile(filename, yamlData, 0644); err != nil {
            log.Fatal(err)
        }
    } else {
        // File already exists, append data to it
        f, err := os.OpenFile(filename, os.O_APPEND|os.O_WRONLY, 0644)
        if err != nil {
            log.Fatal(err)
        }
        defer f.Close()

        if _, err := f.Write(yamlData); err != nil {
            log.Fatal(err)
        }
    }
}
