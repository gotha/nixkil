# Introduction to devenv

## What is devenv?

`devenv` is a fast, declarative, and reproducible developer environment tool built on Nix. It provides a higher-level abstraction over Nix flakes with built-in support for:

- Language-specific toolchains
- Background services (databases, caches, etc.)
- Pre-commit hooks
- Process management
- Container generation

## Why devenv over raw flake devShells?

| Feature | Flake devShell | devenv |
|---------|---------------|--------|
| Language support | Manual setup | Built-in modules |
| Services (postgres, redis) | Complex shellHook | Simple declaration |
| Pre-commit hooks | Manual integration | Built-in |
| Process management | External tools | Built-in (process-compose) |
| Hot reload | Manual | Automatic |
| Learning curve | Steeper | Gentler |

## Quick Start

### Installation

```bash
# Install devenv
nix-env -iA devenv -f https://github.com/cachix/devenv/tarball/latest

# Or add to your system configuration
# NixOS/nix-darwin/home-manager
```

### Initialize a Project

```bash
cd my-project
devenv init
```

This creates:
- `devenv.nix` - Main configuration
- `devenv.yaml` - Input sources
- `.envrc` - direnv integration

### Basic devenv.nix

```nix
{ pkgs, ... }:

{
  # Development packages
  packages = [ pkgs.git pkgs.curl ];

  # Enable a language
  languages.python = {
    enable = true;
    version = "3.11";
  };

  # Environment variables
  env.DATABASE_URL = "postgres://localhost/mydb";

  # Shell hook
  enterShell = ''
    echo "Welcome to the development environment!"
  '';
}
```

### Enter the Environment

```bash
# Manual entry
devenv shell

# With direnv (automatic)
direnv allow
# Environment activates when entering directory
```

## Core Commands

```bash
devenv init          # Initialize new project
devenv shell         # Enter development shell
devenv up            # Start background services
devenv test          # Run tests
devenv build         # Build outputs
devenv gc            # Garbage collect old environments
devenv info          # Show environment info
devenv search <pkg>  # Search for packages
```

## Project Structure

```
my-project/
├── devenv.nix       # Main configuration
├── devenv.yaml      # Inputs and settings
├── devenv.lock      # Locked dependencies
├── .envrc           # direnv integration
└── .devenv/         # Generated files (gitignored)
    ├── state/       # Service state
    └── gc/          # GC roots
```

## devenv.yaml

```yaml
inputs:
  nixpkgs:
    url: github:NixOS/nixpkgs/nixos-24.11

# Optional: additional inputs
# my-input:
#   url: github:owner/repo

# Allow unfree packages
allowUnfree: true

# Import other devenv configurations
imports:
  - ./devenv-extra.nix
```

## When to Use devenv

**Use devenv when:**
- You need background services (databases, message queues)
- You want quick language setup without manual configuration
- You need pre-commit hooks
- You want process management for multiple services
- Team members are less familiar with Nix

**Use raw flake devShells when:**
- You need maximum control over the environment
- You're building complex multi-output flakes
- You want minimal dependencies
- You're already comfortable with Nix
- You need to integrate with existing Nix infrastructure

## Integration with Flakes

devenv can be used inside a flake:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    devenv.url = "github:cachix/devenv";
  };

  outputs = { self, nixpkgs, devenv, ... }@inputs:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      devShells.x86_64-linux.default = devenv.lib.mkShell {
        inherit inputs pkgs;
        modules = [ ./devenv.nix ];
      };
    };
}
```

