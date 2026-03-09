# nixkil

An agent skill for Nix language programming, Nix package manager, and NixOS.

## Overview

This project provides AI agent capabilities for working with:

- **Nix Language** - Functional language for package definitions and system configurations
- **Nix Package Manager** - Reproducible, declarative package management
- **NixOS** - Linux distribution built on Nix principles

## Installation

### Using npx skills (Recommended)

The easiest way to install is using [npx skills](https://www.npmjs.com/package/skills):

```bash
npx skills add gotha/nixkil
```

### Using git submodule

Alternatively, clone as a git submodule in your project:

```bash
# Add as submodule
git submodule add https://github.com/gotha/nixkil.git .skills/nixkil

# Initialize submodules (for cloning existing projects)
git submodule update --init --recursive
```

Then configure your AI assistant to use the skill from `.skills/nixkil`.

## Updating

### If installed via npx skills

```bash
npx skills update gotha/nixkil
```

### If installed via git submodule

```bash
# Navigate to your project root
cd /path/to/your/project

# Update the submodule to latest
git submodule update --remote .skills/nixkil

# Commit the update
git add .skills/nixkil
git commit -m "Update nixkil skill to latest version"
```



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

