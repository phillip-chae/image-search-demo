package config

import (
	"strings"

	"github.com/knadh/koanf/parsers/yaml"
	"github.com/knadh/koanf/providers/env"
	"github.com/knadh/koanf/providers/file"
	"github.com/knadh/koanf/v2"
)

// BasicConfig handles configuration loading using koanf
type BasicConfig struct {
	k *koanf.Koanf
}

// NewBasicConfig creates a new config BasicConfig
func NewBasicConfig() *BasicConfig {
	return &BasicConfig{
		k: koanf.New("."),
	}
}

// Load reads a YAML file and overrides with environment variables
// filePath: Path to the YAML config file (optional, can be empty)
// envPrefix: Prefix for environment variables (e.g. "APP_")
// target: Pointer to the struct where config will be unmarshaled
func (l *BasicConfig) Load(filePath string, envPrefix string, target any) error {
	// 1. Load from YAML file if provided
	if filePath != "" {
		if err := l.k.Load(file.Provider(filePath), yaml.Parser()); err != nil {
			// It's often useful to ignore "file not found" if we rely on env vars,
			// but strict loading is safer. Let's return error.
			// If you want optional file loading, check os.Stat before calling Load.
			return err
		}
	}

	// 2. Load from Environment variables
	// We use a callback to transform ENV_VARS to dot.notation
	// e.g. APP_SERVER_PORT -> server.port
	err := l.k.Load(env.Provider(envPrefix, ".", func(s string) string {
		// Remove the prefix
		s = strings.TrimPrefix(s, envPrefix)

		// Handle case where prefix didn't include the separator (e.g. "APP" vs "APP_")
		s = strings.TrimPrefix(s, "_")

		// Transform to lowercase and replace underscores with dots
		// SERVER_PORT -> server.port
		return strings.ReplaceAll(strings.ToLower(s), "_", ".")
	}), nil)

	if err != nil {
		return err
	}

	// 3. Unmarshal into the target struct
	// We configure it to use "yaml" tags, so it's compatible with existing structs
	return l.k.UnmarshalWithConf("", target, koanf.UnmarshalConf{
		Tag: "yaml",
	})
}
