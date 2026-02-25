{
  description = "Go development environment";

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
        devShells.default = pkgs.mkShell {
          name = "go-dev";

          packages = with pkgs; [
            # Go compiler and tools
            go_1_22
            gopls # Language server
            golangci-lint # Linter
            delve # Debugger
            gotools # Additional tools (goimports, etc.)
            go-tools # staticcheck

            # Build dependencies
            gcc
            pkg-config

            # Useful utilities
            gnumake
            git
          ];

          env = {
            # Go environment
            GOPATH = "$HOME/go";
            CGO_ENABLED = "1";
          };

          shellHook = ''
            echo "🐹 Go development environment"
            echo "   Go version: $(go version | cut -d' ' -f3)"
            echo ""
            echo "Available tools:"
            echo "  go       - Go compiler"
            echo "  gopls    - Language server (for IDE)"
            echo "  golangci-lint - Linter"
            echo "  dlv      - Debugger"
            echo ""
            
            # Add local bin to PATH for go install
            export PATH="$GOPATH/bin:$PATH"
          '';
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

