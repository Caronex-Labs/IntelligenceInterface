package main

import (
	"github.com/caronex/intelligence-interface/cmd"
	"github.com/caronex/intelligence-interface/internal/core/logging"
)

func main() {
	defer logging.RecoverPanic("main", func() {
		logging.ErrorPersist("Application terminated due to unhandled panic")
	})

	cmd.Execute()
}
