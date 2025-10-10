# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-language learning repository containing deep learning projects, tools, and implementations across various programming languages including Python, Rust, Go, C++, Kotlin, Android, and Node.js.

## Key Architecture

### Python Projects

#### Investment Analyst System (`python/investment_analyst/`)
A sophisticated LLM Agent-based investment analysis system with multiple MCP (Model Context Protocol) modules:
- Workflow orchestrator for task coordination and error handling
- Specialized MCP modules for industry analysis, financial data extraction, validation
- Comprehensive testing with pytest (`python run_tests.py`)

#### MCP Servers (`python/mcp/`)
- **Grafana MCP**: Grafana integration server with client setup
- **ADB MCP**: Android Debug Bridge integration

#### OpenAI Chat (`python/openai_chat/`)
Basic OpenAI API integration examples

### Rust Projects (`rust/`)

**Core Application** ("rurl"):
- HTTP client with multipart and JSON support
- Lua scripting integration via mlua
- OpenAI image chat functionality as separate binary
- Async runtime with tokio
- Build system using Cargo and Make

**Key Dependencies**: reqwest, tokio, mlua, serde, hyper

### C++ Projects (`cpp/jason/`)
Modern C++ library featuring:
- JSON parser
- Network components and coroutines
- Smart pointer implementations
- Cache system

### Go Projects (`go/`)
Multiple applications including:
- Kibana log processing with protobuf
- Music player implementation
- CGO examples

## Common Development Commands

### Python
```bash
# Investment Analyst System
cd python/investment_analyst
python main.py                    # Run the main system
python run_tests.py              # Run all tests
pytest tests/                    # Run pytest directly
pip install -r requirements.txt  # Install dependencies

# MCP Servers
cd python/mcp/grafana
pip install -r requirements.txt
python server.py                 # Start MCP server
```

### Rust
```bash
cd rust
make build                       # Build release version
make run                         # Run with debug flags
make test                        # Run tests
cargo test                       # Alternative test command
cargo test test_analyze_image_buffer_sync -- --nocapture  # Specific test
```

### Go
```bash
cd go/[project-name]
go mod tidy                      # Update dependencies
go run .                         # Run project
```

### C++
```bash
cd cpp/jason
# Uses standard cmake/make build system (check for CMakeLists.txt or Makefile)
```

## Project Structure

- **Language-specific directories**: Each language has its own top-level directory
- **Independent projects**: Most projects are self-contained with their own dependency management
- **Shared patterns**: Each language directory follows standard conventions (requirements.txt, Cargo.toml, go.mod, etc.)

## Testing

- **Python**: pytest-based testing with comprehensive test coverage
- **Rust**: Built-in cargo test framework
- **Investment Analyst**: Dedicated test runner with `python run_tests.py`

## Build Systems

- **Python**: pip + requirements.txt
- **Rust**: Cargo with Makefile wrapper
- **Go**: Go modules
- **C++**: CMake/Make (project-specific)
- **Node.js**: npm (though package.json is currently empty)

## MCP Protocol

The repository implements several MCP (Model Context Protocol) servers, particularly in the Python ecosystem. These servers provide structured interfaces for external service integration like Grafana and ADB.