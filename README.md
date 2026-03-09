# nixkil

An agent skill for Nix language programming, Nix package manager, and NixOS.

## Overview

This project provides AI agent capabilities for working with:

- **Nix Language** - Functional language for package definitions and system configurations
- **Nix Package Manager** - Reproducible, declarative package management
- **NixOS** - Linux distribution built on Nix principles

## Installation

You can use [npx skills](https://www.npmjs.com/package/skills)

```sh
npx skills add gotha/nixkil
```

or you can clone as a git submodule in your project:

```bash
# Add as submodule
git submodule add https://github.com/gotha/nixkil.git .skills/nixkil

# Initialize submodules (for cloning existing projects)
git submodule update --init --recursive
```

Then configure your AI assistant to use the skill from `.skills/nixkil` or symlink in `.augment/skills` (for example).



## Development

```bash
# Enter development shell
nix develop

# Format Nix files
nix fmt

# Lint Nix files
nix develop -c statix check .
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Format code: `nix fmt`
5. Commit with a descriptive message
6. Push and open a pull request

### Project Structure

```
nixkil/
├── knowledge/          # Markdown documentation for AI context
│   ├── language/       # Nix language reference
│   ├── nixpkgs/        # Package management docs
│   ├── flakes/         # Flakes documentation
│   ├── devenv/         # Devenv usage guides
│   ├── nixos/          # NixOS configuration
│   ├── nix-darwin/     # macOS configuration
│   ├── home-manager/   # User environment management
│   ├── macos-linux-builder/  # Cross-compilation on macOS
│   └── troubleshooting/      # Common issues and solutions
├── examples/           # Working example configurations
│   ├── devshells/      # Language-specific dev environments
│   └── devenv/         # Devenv examples with services
└── prompts/            # System prompts for AI agents
```

### Adding Knowledge

Add markdown files to the appropriate subdirectory in `knowledge/`. The AI will use these for context when answering questions.

## License

MIT

