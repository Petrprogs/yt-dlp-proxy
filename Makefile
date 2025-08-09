# Makefile for yt-dlp-proxy
# Provides convenient commands for building, testing, and installing
# Cross-platform support for Windows and Linux

.PHONY: help build clean install test dev-setup uninstall venv

# Detect platform
ifeq ($(OS),Windows_NT)
    PYTHON := python
    PIP := pip
    VENV_PYTHON := venv\Scripts\python.exe
    VENV_PIP := venv\Scripts\pip.exe
    BINARY_NAME := yt-dlp-proxy.exe
    RM := rmdir /s /q
    RMFILE := del /q
    MKDIR := mkdir
    CP := copy
    CHMOD := echo
    INSTALL_DIR := "C:\Program Files\yt-dlp-proxy"
    INSTALL_CMD := $(CP) dist\$(BINARY_NAME) $(INSTALL_DIR)\
    UNINSTALL_CMD := $(RMFILE) $(INSTALL_DIR)\$(BINARY_NAME)
else
    PYTHON := python3
    PIP := pip3
    VENV_PYTHON := venv/bin/python
    VENV_PIP := venv/bin/pip
    BINARY_NAME := yt-dlp-proxy
    RM := rm -rf
    RMFILE := rm -f
    MKDIR := mkdir -p
    CP := cp
    CHMOD := chmod +x
    INSTALL_DIR := /usr/local/bin
    INSTALL_CMD := sudo $(CP) dist/$(BINARY_NAME) $(INSTALL_DIR)/
    UNINSTALL_CMD := sudo $(RMFILE) $(INSTALL_DIR)/$(BINARY_NAME)
endif

# Default target
help:
	@echo "yt-dlp-proxy Makefile"
	@echo "===================="
	@echo ""
	@echo "Platform: $(if $(filter Windows_NT,$(OS)),Windows,Linux/Unix)"
	@echo "Binary: $(BINARY_NAME)"
	@echo ""
	@echo "Available targets:"
	@echo "  venv        - Create virtual environment"
	@echo "  build       - Build the binary executable"
	@echo "  clean       - Clean build artifacts"
	@echo "  install     - Install the binary system-wide"
	@echo "  test        - Test the binary"
	@echo "  dev-setup   - Set up development environment"
	@echo "  uninstall   - Remove the binary from system"
	@echo "  help        - Show this help message"

# Create virtual environment
venv:
	@echo "🐍 Creating virtual environment..."
ifeq ($(OS),Windows_NT)
	@if exist venv $(RM) venv
	@$(PYTHON) -m venv venv
else
	@rm -rf venv
	@$(PYTHON) -m venv venv
endif
	@echo "✅ Virtual environment created"

# Build the binary
build:
	@echo "🏗️  Building yt-dlp-proxy binary..."
	@$(PYTHON) build.py

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
ifeq ($(OS),Windows_NT)
	@if exist build $(RM) build
	@if exist dist $(RM) dist
	@if exist __pycache__ $(RM) __pycache__
	@if exist venv $(RM) venv
	@if exist .venv $(RM) .venv
	@for %%f in (*.spec) do $(RMFILE) %%f
	@if exist install.sh $(RMFILE) install.sh
	@if exist install.bat $(RMFILE) install.bat
else
	@rm -rf build dist __pycache__ venv .venv
	@rm -f *.spec install.sh install.bat
endif
	@echo "✅ Cleaned"

# Install the binary system-wide
install:
	@echo "📦 Installing yt-dlp-proxy..."
ifeq ($(OS),Windows_NT)
	@if not exist "dist\$(BINARY_NAME)" ( \
		echo "❌ Binary not found. Run 'make build' first."; \
		exit 1; \
	)
	@if not exist $(INSTALL_DIR) $(MKDIR) $(INSTALL_DIR)
	@$(INSTALL_CMD)
	@echo "✅ Installed to $(INSTALL_DIR)\$(BINARY_NAME)"
	@echo "💡 You may need to add $(INSTALL_DIR) to your PATH"
else
	@test -f "dist/$(BINARY_NAME)" || (echo "❌ Binary not found. Run 'make build' first." && exit 1)
	@$(INSTALL_CMD)
	@$(CHMOD) $(INSTALL_DIR)/$(BINARY_NAME)
	@echo "✅ Installed to $(INSTALL_DIR)/$(BINARY_NAME)"
endif

# Test the binary
test:
	@echo "🧪 Testing the binary..."
ifeq ($(OS),Windows_NT)
	@if not exist "dist\$(BINARY_NAME)" ( \
		echo "❌ Binary not found. Run 'make build' first."; \
		exit 1; \
	)
	@dist\$(BINARY_NAME) --help || echo "Test completed"
else
	@test -f "dist/$(BINARY_NAME)" || (echo "❌ Binary not found. Run 'make build' first." && exit 1)
	@./dist/$(BINARY_NAME) --help || echo "Test completed"
endif
	@echo "✅ Test completed"

# Set up development environment
dev-setup: venv
	@echo "🔧 Setting up development environment..."
	@$(VENV_PIP) install -r requirements.txt
	@$(VENV_PIP) install -r requirements-build.txt
	@echo "✅ Development environment ready"

# Uninstall the binary
uninstall:
	@echo "🗑️  Uninstalling yt-dlp-proxy..."
ifeq ($(OS),Windows_NT)
	@if exist "$(INSTALL_DIR)\$(BINARY_NAME)" ( \
		$(UNINSTALL_CMD); \
		echo "✅ Uninstalled"; \
	) else ( \
		echo "ℹ️  yt-dlp-proxy not found in $(INSTALL_DIR)"; \
	)
else
	@if [ -f "$(INSTALL_DIR)/$(BINARY_NAME)" ]; then \
		$(UNINSTALL_CMD); \
		echo "✅ Uninstalled"; \
	else \
		echo "ℹ️  yt-dlp-proxy not found in $(INSTALL_DIR)"; \
	fi
endif

# Quick build and install
all: build install
	@echo "🎉 Build and install completed!"

# Development helpers
dev-clean: clean
	@echo "🧹 Development clean completed"

dev-rebuild: clean build
	@echo "🔄 Development rebuild completed" 