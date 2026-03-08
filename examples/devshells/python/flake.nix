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
            uv # Fast package installer and resolver (replaces pip, virtualenv)

            # Code quality tools
            ruff # Fast linting (replaces flake8, isort)
            black # Code formatting
            mypy # Type checking
            vulture # Dead code detection

            # Language server
            pyright # Type checker / Language server

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
              uv venv .venv
            fi

            # Activate venv
            source .venv/bin/activate

            echo "Virtual environment activated: .venv"
            echo ""
            echo "Available tools:"
            echo "  python   - Python interpreter"
            echo "  uv       - Fast package installer"
            echo "  ruff     - Fast linting (replaces flake8, isort)"
            echo "  black    - Code formatting"
            echo "  mypy     - Type checking"
            echo "  vulture  - Dead code detection"
            echo "  pyright  - Language server"
            echo ""
            echo "Quick start:"
            echo "  uv pip install -r requirements.txt  # Install dependencies"
            echo "  uv add <package>                    # Add a dependency"
            echo "  ruff check .                        # Lint code"
            echo "  black .                             # Format code"
            echo "  mypy .                              # Type check"
            echo "  vulture .                           # Find dead code"
          '';
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

