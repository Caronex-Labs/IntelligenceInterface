package utils

import (
	"context"
	"fmt"
	"os"
	"time"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// ILogger defines the interface for logging operations
type ILogger interface {
	WithContext(ctx context.Context) *Logger
	LogRequest(ctx context.Context, method, path string, status int, duration time.Duration)
	LogError(ctx context.Context, err error, msg string, fields ...zap.Field)
	Write(p []byte) (n int, err error)
	LogOperation(ctx context.Context, operation string, fn func() error) error
	LogMethodEntry(ctx context.Context, method string, params ...interface{})
	LogMethodExit(ctx context.Context, method string, err error, duration time.Duration)
	LogDBOperation(ctx context.Context, operation string, query string, args ...interface{}) func(error)
	LogMetric(ctx context.Context, metric string, value float64, labels ...string)
	Debug(msg string, fields ...zap.Field)
	Info(msg string, fields ...zap.Field)
	Warn(msg string, fields ...zap.Field)
	Error(msg string, fields ...zap.Field)
	Fatal(msg string, fields ...zap.Field)
}

// Logger wraps zap logger with additional context and methods
type Logger struct {
	*zap.Logger
}

// Wrap zap's field constructors for convenience
var (
	String   = zap.String
	Int      = zap.Int
	Bool     = zap.Bool
	Float64  = zap.Float64
	Error    = zap.Error
	Any      = zap.Any
	Duration = zap.Duration
)

var _ ILogger = (*Logger)(nil) // Ensure Logger implements ILogger

// LogConfig holds logging configuration
type LogConfig struct {
	Level      string
	OutputPath string
	DevMode    bool
}

// NewLogger creates a new logger instance based on the provided configuration
func NewLogger(config LogConfig) (*Logger, error) {
	// Determine the output destination
	var output zapcore.WriteSyncer
	switch config.OutputPath {
	case "stdout":
		output = zapcore.AddSync(os.Stdout)
	case "stderr":
		output = zapcore.AddSync(os.Stderr)
	default:
		file, err := os.OpenFile(config.OutputPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			return nil, fmt.Errorf("failed to open log file: %w", err)
		}
		output = zapcore.AddSync(file)
	}

	// Create encoder config based on development mode
	encoderConfig := zapcore.EncoderConfig{
		TimeKey:        "timestamp",
		LevelKey:       "level",
		NameKey:        "logger",
		CallerKey:      "caller",
		FunctionKey:    zapcore.OmitKey,
		MessageKey:     "message",
		StacktraceKey:  "stacktrace",
		LineEnding:     zapcore.DefaultLineEnding,
		EncodeLevel:    zapcore.LowercaseLevelEncoder,
		EncodeTime:     zapcore.ISO8601TimeEncoder,
		EncodeDuration: zapcore.SecondsDurationEncoder,
		EncodeCaller:   zapcore.ShortCallerEncoder,
	}

	// Use different encoding in development mode
	var encoder zapcore.Encoder
	if config.DevMode {
		encoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
		encoder = zapcore.NewConsoleEncoder(encoderConfig)
	} else {
		encoder = zapcore.NewJSONEncoder(encoderConfig)
	}

	// Create core
	core := zapcore.NewCore(
		encoder,
		output,
		getZapLevel(config.Level),
	)

	// Create options
	opts := []zap.Option{
		zap.AddCaller(),
		zap.AddStacktrace(zapcore.ErrorLevel),
	}

	// Create logger
	zapLogger := zap.New(core, opts...)
	return &Logger{zapLogger}, nil
}

// NewDevelopmentLogger creates a new development logger
func NewDevelopmentLogger() (*Logger, error) {
	return NewLogger(LogConfig{
		Level:      "debug",
		OutputPath: "stdout",
		DevMode:    true,
	})
}

// NewProductionLogger creates a new production logger
func NewProductionLogger() (*Logger, error) {
	return NewLogger(LogConfig{
		Level:      "info",
		OutputPath: "stdout",
		DevMode:    false,
	})
}

// WithContext adds context values to the logger
func (l *Logger) WithContext(ctx context.Context) *Logger {
	if ctx == nil {
		return l
	}

	newLogger := l.Logger

	// Add request ID if present
	if requestID, ok := ctx.Value("request_id").(string); ok {
		newLogger = newLogger.With(zap.String("request_id", requestID))
	}

	// Add user ID if present
	if userID, ok := ctx.Value("user_id").(string); ok {
		newLogger = newLogger.With(zap.String("user_id", userID))
	}

	// Add trace ID if present (for distributed tracing)
	if traceID, ok := ctx.Value("trace_id").(string); ok {
		newLogger = newLogger.With(zap.String("trace_id", traceID))
	}

	return &Logger{newLogger}
}

// LogRequest logs HTTP request details
func (l *Logger) LogRequest(ctx context.Context, method, path string, status int, duration time.Duration) {
	l.WithContext(ctx).Info("http_request",
		zap.String("method", method),
		zap.String("path", path),
		zap.Int("status", status),
		zap.Duration("duration", duration),
		zap.String("event", "request"),
	)
}

// LogError logs error details with context and additional fields
func (l *Logger) LogError(ctx context.Context, err error, msg string, fields ...zap.Field) {
	allFields := append(fields, zap.Error(err))
	l.WithContext(ctx).Error(msg, allFields...)
}

// Write implements io.Writer interface for compatibility with standard library
func (l *Logger) Write(p []byte) (n int, err error) {
	l.Info(string(p))
	return len(p), nil
}

// getZapLevel converts string level to zapcore.Level
func getZapLevel(level string) zapcore.Level {
	switch level {
	case "debug":
		return zapcore.DebugLevel
	case "info":
		return zapcore.InfoLevel
	case "warn":
		return zapcore.WarnLevel
	case "error":
		return zapcore.ErrorLevel
	case "dpanic":
		return zapcore.DPanicLevel
	case "panic":
		return zapcore.PanicLevel
	case "fatal":
		return zapcore.FatalLevel
	default:
		return zapcore.InfoLevel
	}
}

// LogOperation logs the start and end of an operation with timing
func (l *Logger) LogOperation(ctx context.Context, operation string, fn func() error) error {
	start := time.Now()
	l.WithContext(ctx).Debug("starting_operation",
		zap.String("operation", operation),
		zap.String("event", "operation_start"),
	)

	err := fn()
	duration := time.Since(start)

	logger := l.WithContext(ctx)
	if err != nil {
		logger.Error("operation_failed",
			zap.String("operation", operation),
			zap.String("event", "operation_end"),
			zap.Duration("duration", duration),
			zap.Error(err),
		)
	} else {
		logger.Debug("operation_completed",
			zap.String("operation", operation),
			zap.String("event", "operation_end"),
			zap.Duration("duration", duration),
		)
	}

	return err
}

// LogMethodEntry logs entry into a method with parameters
func (l *Logger) LogMethodEntry(ctx context.Context, method string, params ...interface{}) {
	fields := make([]zap.Field, 0, len(params)/2+1)
	fields = append(fields, zap.String("method", method))

	for i := 0; i < len(params); i += 2 {
		if i+1 < len(params) {
			fields = append(fields, zap.Any(params[i].(string), params[i+1]))
		}
	}

	l.WithContext(ctx).Debug("method_entry", fields...)
}

// LogMethodExit logs exit from a method with result
func (l *Logger) LogMethodExit(ctx context.Context, method string, err error, duration time.Duration) {
	logger := l.WithContext(ctx)
	fields := []zap.Field{
		zap.String("method", method),
		zap.Duration("duration", duration),
	}

	if err != nil {
		fields = append(fields, zap.Error(err))
		logger.Error("method_exit", fields...)
	} else {
		logger.Debug("method_exit", fields...)
	}
}

// LogDBOperation logs database operations with timing
func (l *Logger) LogDBOperation(ctx context.Context, operation string, query string, args ...interface{}) func(error) {
	start := time.Now()
	l.WithContext(ctx).Debug("db_operation_start",
		zap.String("operation", operation),
		zap.String("query", query),
		zap.Any("args", args),
	)

	return func(err error) {
		duration := time.Since(start)
		logger := l.WithContext(ctx)

		if err != nil {
			logger.Error("db_operation_failed",
				zap.String("operation", operation),
				zap.String("query", query),
				zap.Duration("duration", duration),
				zap.Error(err),
			)
		} else {
			logger.Debug("db_operation_completed",
				zap.String("operation", operation),
				zap.String("query", query),
				zap.Duration("duration", duration),
			)
		}
	}
}

// LogMetric logs a metric with its value and optional labels
func (l *Logger) LogMetric(ctx context.Context, metric string, value float64, labels ...string) {
	fields := make([]zap.Field, 0, len(labels)/2+2)
	fields = append(fields,
		zap.String("metric", metric),
		zap.Float64("value", value),
	)

	for i := 0; i < len(labels); i += 2 {
		if i+1 < len(labels) {
			fields = append(fields, zap.String(labels[i], labels[i+1]))
		}
	}

	l.WithContext(ctx).Info("metric", fields...)
}
