{
  description = "Node.js development environment";

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
          name = "nodejs-dev";

          packages = with pkgs; [
            # Node.js runtime
            nodejs_20
            corepack # For pnpm/yarn management

            # Package managers (pick one or use corepack)
            # yarn
            # pnpm

            # TypeScript
            nodePackages.typescript
            nodePackages.typescript-language-server

            # Linting and formatting
            nodePackages.eslint
            nodePackages.prettier

            # Useful tools
            nodePackages.npm-check-updates # Check for dependency updates
            jq # JSON processing
          ];

          env = {
            # Prevent npm from creating .npm in home directory
            NPM_CONFIG_PREFIX = "$PWD/.npm-global";
            # Node options
            NODE_OPTIONS = "--max-old-space-size=4096";
          };

          shellHook = ''
            echo "📦 Node.js development environment"
            echo "   Node version: $(node --version)"
            echo "   npm version: $(npm --version)"
            echo ""
            
            # Add node_modules/.bin to PATH for local packages
            export PATH="$PWD/node_modules/.bin:$PATH"
            
            # Add npm global bin to PATH
            export PATH="$PWD/.npm-global/bin:$PATH"
            
            echo "Available tools:"
            echo "  node       - JavaScript runtime"
            echo "  npm        - Package manager"
            echo "  npx        - Package runner"
            echo "  tsc        - TypeScript compiler"
            echo "  eslint     - Linter"
            echo "  prettier   - Formatter"
            echo ""
            echo "Quick start:"
            echo "  npm init -y              # Initialize project"
            echo "  npm install              # Install dependencies"
            echo "  npm run dev              # Start dev server (if configured)"
            echo "  npx eslint .             # Lint code"
            echo "  npx prettier --write .   # Format code"
            echo ""
            echo "Using corepack for yarn/pnpm:"
            echo "  corepack enable          # Enable corepack"
            echo "  yarn install             # Use yarn"
            echo "  pnpm install             # Use pnpm"
          '';
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

