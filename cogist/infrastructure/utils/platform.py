"""Platform utilities - Infrastructure Layer

Provides cross-platform constants and utilities.
"""
import platform

# Global constant for platform detection
# Values: "Darwin" (macOS), "Windows", "Linux"
PLATFORM = platform.system()
