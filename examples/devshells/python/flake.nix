{
  description = "Python development environment";

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
        python = pkgs.python311;
      in
      {
        devShells.default = pkgs.mkShell {
          name = "python-dev";

          packages = with pkgs; [
            # Python
            python
            python.pkgs.pip
            python.pkgs.virtualenv

            # Development tools
            ruff # Fast linter and formatter
            pyright # Type checker / Language server
            black # Code formatter (alternative to ruff format)

            # Build dependencies (for packages with C extensions)
            gcc
            pkg-config
            openssl
            zlib
          ];

          env = {
            # Prevent Python from writing .pyc files
            PYTHONDONTWRITEBYTECODE = "1";
            # Enable Python tracebacks on segfaults
            PYTHONFAULTHANDLER = "1";
          };

          shellHook = ''
            echo "🐍 Python development environment"
            echo "   Python version: $(python --version)"
            echo ""
            
            # Create venv if it doesn't exist
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              python -m venv .venv
            fi
            
            # Activate venv
            source .venv/bin/activate
            
            echo "Virtual environment activated: .venv"
            echo ""
            echo "Available tools:"
            echo "  python   - Python interpreter"
            echo "  pip      - Package installer"
            echo "  ruff     - Linter and formatter"
            echo "  pyright  - Type checker"
            echo "  black    - Code formatter"
            echo ""
            echo "Quick start:"
            echo "  pip install -r requirements.txt  # Install dependencies"
            echo "  ruff check .                     # Lint code"
            echo "  ruff format .                    # Format code"
            echo "  pyright                          # Type check"
          '';
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

