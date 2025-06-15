package internal

import (
	"strings"
	"unicode"
)

// ToSnakeCase converts a string to snake_case
func ToSnakeCase(s string) string {
	if s == "" {
		return ""
	}
	
	var result strings.Builder
	for i, r := range s {
		if unicode.IsUpper(r) {
			// Add underscore before uppercase letter if not at start
			// and if previous character is lowercase or next character is lowercase
			if i > 0 {
				prev := rune(s[i-1])
				// Add underscore if previous character is lowercase
				// or if this is start of acronym followed by lowercase
				if unicode.IsLower(prev) || (i+1 < len(s) && unicode.IsLower(rune(s[i+1]))) {
					result.WriteRune('_')
				}
			}
			result.WriteRune(unicode.ToLower(r))
		} else {
			result.WriteRune(r)
		}
	}
	return result.String()
}

// ToPascalCase converts a string to PascalCase
func ToPascalCase(s string) string {
	if s == "" {
		return ""
	}
	
	var result strings.Builder
	nextUpper := true
	for _, r := range s {
		if r == '_' || r == '-' || r == ' ' {
			nextUpper = true
		} else if nextUpper {
			result.WriteRune(unicode.ToUpper(r))
			nextUpper = false
		} else {
			result.WriteRune(unicode.ToLower(r))
		}
	}
	return result.String()
}

// ToCamelCase converts a string to camelCase
func ToCamelCase(s string) string {
	if s == "" {
		return ""
	}
	
	pascal := ToPascalCase(s)
	if len(pascal) == 0 {
		return ""
	}
	
	// Convert first character to lowercase
	return strings.ToLower(string(pascal[0])) + pascal[1:]
}

// Pluralize adds an 's' to the end of a string
// This is a simple implementation - could be enhanced with proper pluralization rules
func Pluralize(s string) string {
	if s == "" {
		return ""
	}
	
	// Simple pluralization rules
	switch {
	case strings.HasSuffix(s, "y"):
		return s[:len(s)-1] + "ies"
	case strings.HasSuffix(s, "s") || strings.HasSuffix(s, "x") || strings.HasSuffix(s, "z") ||
		 strings.HasSuffix(s, "ch") || strings.HasSuffix(s, "sh"):
		return s + "es"
	default:
		return s + "s"
	}
}

// Singularize removes plural suffix from a string
// This is a simple implementation - could be enhanced with proper singularization rules
func Singularize(s string) string {
	if s == "" {
		return ""
	}
	
	// Simple singularization rules
	switch {
	case strings.HasSuffix(s, "ies"):
		return s[:len(s)-3] + "y"
	case strings.HasSuffix(s, "es"):
		if strings.HasSuffix(s, "ses") || strings.HasSuffix(s, "xes") || strings.HasSuffix(s, "zes") ||
		   strings.HasSuffix(s, "ches") || strings.HasSuffix(s, "shes") {
			return s[:len(s)-2]
		}
		return s[:len(s)-1]
	case strings.HasSuffix(s, "s") && len(s) > 1:
		return s[:len(s)-1]
	default:
		return s
	}
}

// IsValidIdentifier checks if a string is a valid Go identifier
func IsValidIdentifier(s string) bool {
	if s == "" {
		return false
	}
	
	// First character must be letter or underscore
	first := rune(s[0])
	if !unicode.IsLetter(first) && first != '_' {
		return false
	}
	
	// Remaining characters must be letters, digits, or underscores
	for _, r := range s[1:] {
		if !unicode.IsLetter(r) && !unicode.IsDigit(r) && r != '_' {
			return false
		}
	}
	
	return true
}

// SanitizeIdentifier converts a string to a valid Go identifier
func SanitizeIdentifier(s string) string {
	if s == "" {
		return "unnamed"
	}
	
	var result strings.Builder
	
	// Handle first character
	first := rune(s[0])
	if unicode.IsLetter(first) || first == '_' {
		result.WriteRune(first)
	} else if unicode.IsDigit(first) {
		result.WriteRune('_')
		result.WriteRune(first)
	} else {
		result.WriteRune('_')
	}
	
	// Handle remaining characters
	for _, r := range s[1:] {
		if unicode.IsLetter(r) || unicode.IsDigit(r) || r == '_' {
			result.WriteRune(r)
		} else {
			result.WriteRune('_')
		}
	}
	
	return result.String()
}
