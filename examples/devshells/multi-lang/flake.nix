{
  description = "Multi-language (polyglot) development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells = {
          # Default shell with all languages
          default = pkgs.mkShell {
            name = "polyglot-dev";

            packages = with pkgs; [
              # Go
              go_1_22
              gopls
              golangci-lint

              # Python
              python311
              uv       # Fast package installer and resolver
              ruff     # Fast linting (replaces flake8, isort)
              black    # Code formatting
              mypy     # Type checking
              vulture  # Dead code detection
              pyright  # LSP

              # Node.js
              nodejs_20
              nodePackages.typescript
              nodePackages.typescript-language-server

              # Rust
              rustc
              cargo
              rust-analyzer
              clippy

              # Common tools
              git
              jq
              gnumake
              pkg-config
            ];

            shellHook = ''
              echo "🌐 Multi-language development environment"
              echo ""
              echo "Languages available:"
              echo "  Go     $(go version | cut -d' ' -f3)"
              echo "  Python $(python --version)"
              echo "  Node   $(node --version)"
              echo "  Rust   $(rustc --version | cut -d' ' -f2)"
              echo ""
              echo "Use specific shells for focused development:"
              echo "  nix develop .#go      # Go only"
              echo "  nix develop .#python  # Python only"
              echo "  nix develop .#node    # Node.js only"
              echo "  nix develop .#rust    # Rust only"
            '';
          };

          # Language-specific shells for focused work
          go = pkgs.mkShell {
            name = "go-only";
            packages = with pkgs; [ go_1_22 gopls golangci-lint delve ];
            shellHook = ''echo "🐹 Go development environment"'';
          };

          python = pkgs.mkShell {
            name = "python-only";
            packages = with pkgs; [
              python311
              uv       # Fast package installer and resolver
              ruff     # Fast linting (replaces flake8, isort)
              black    # Code formatting
              mypy     # Type checking
              vulture  # Dead code detection
              pyright  # LSP
            ];
            shellHook = ''
              echo "🐍 Python development environment"
              if [ ! -d .venv ]; then uv venv .venv; fi
              source .venv/bin/activate
            '';
          };

          node = pkgs.mkShell {
            name = "node-only";
            packages = with pkgs; [
              nodejs_20
              nodePackages.typescript
              nodePackages.typescript-language-server
            ];
            shellHook = ''
              echo "📦 Node.js development environment"
              export PATH="$PWD/node_modules/.bin:$PATH"
            '';
          };

          rust = pkgs.mkShell {
            name = "rust-only";
            packages = with pkgs; [ rustc cargo rust-analyzer clippy rustfmt ];
            shellHook = ''echo "🦀 Rust development environment"'';
          };
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

