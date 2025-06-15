package main

import (
	"flag"
	"fmt"
	"os"

	"go_backend_gorm/cmd/standardize/internal"
)

var (
	domainFlag = flag.String("domain", "", "Domain name (required)")
	entityFlag = flag.String("name", "", "Entity name (required for entity command)")
	configFlag = flag.String("config", "", "Configuration file path (YAML)")
)

func main() {
	flag.Parse()

	// Initialize command handler
	commandHandler := internal.NewCommandHandler()

	// Check if config file is provided
	if *configFlag != "" {
		if err := commandHandler.GenerateFromConfig(*configFlag); err != nil {
			fmt.Printf("Error: %s\n", err)
			os.Exit(1)
		}
		fmt.Println("Done!")
		return
	}

	// Fallback to original command-line interface
	if *domainFlag == "" {
		printUsage(commandHandler)
		os.Exit(1)
	}

	// Parse command
	args := flag.Args()
	if len(args) == 0 {
		fmt.Println("Error: command is required")
		printAvailableCommands(commandHandler)
		os.Exit(1)
	}

	// Execute command
	commandName := args[0]
	if err := commandHandler.GenerateLegacy(*domainFlag, *entityFlag, commandName); err != nil {
		fmt.Printf("Error: %s\n", err)
		os.Exit(1)
	}

	fmt.Println("Done!")
}

func printUsage(ch *internal.CommandHandler) {
	fmt.Println("Error: domain flag is required")
	fmt.Println()
	fmt.Println("Usage:")
	fmt.Println("  standardize --config <config_file.yaml>")
	fmt.Println("  standardize --domain <domain_name> [--name <entity_name>] <command>")
	fmt.Println()
	printAvailableCommands(ch)
}

func printAvailableCommands(ch *internal.CommandHandler) {
	fmt.Println("Available commands:")
	for _, cmd := range ch.GetAvailableCommands() {
		fmt.Printf("  %s: %s\n", cmd.Name, cmd.Description)
	}
}
