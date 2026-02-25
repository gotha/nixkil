{
  description = "Rust development environment";

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
          name = "rust-dev";

          packages = with pkgs; [
            # Rust toolchain
            rustc
            cargo
            rustfmt
            clippy

            # Language server
            rust-analyzer

            # Additional tools
            cargo-edit # cargo add/rm/upgrade
            cargo-watch # Auto-rebuild on changes
            cargo-audit # Security audit

            # Build dependencies
            pkg-config
            openssl
            libiconv
          ] ++ lib.optionals stdenv.isDarwin [
            darwin.apple_sdk.frameworks.Security
            darwin.apple_sdk.frameworks.SystemConfiguration
          ];

          env = {
            # Better error messages
            RUST_BACKTRACE = "1";
            # Use sccache for faster rebuilds (optional)
            # RUSTC_WRAPPER = "${pkgs.sccache}/bin/sccache";
          };

          shellHook = ''
            echo "🦀 Rust development environment"
            echo "   Rust version: $(rustc --version)"
            echo "   Cargo version: $(cargo --version)"
            echo ""
            echo "Available tools:"
            echo "  cargo          - Package manager"
            echo "  rustc          - Compiler"
            echo "  rust-analyzer  - Language server"
            echo "  rustfmt        - Formatter"
            echo "  clippy         - Linter"
            echo "  cargo-watch    - Auto-rebuild"
            echo "  cargo-edit     - Dependency management"
            echo "  cargo-audit    - Security audit"
            echo ""
            echo "Quick start:"
            echo "  cargo new myproject     # Create new project"
            echo "  cargo build             # Build project"
            echo "  cargo run               # Build and run"
            echo "  cargo test              # Run tests"
            echo "  cargo clippy            # Lint code"
            echo "  cargo fmt               # Format code"
            echo "  cargo watch -x run      # Auto-rebuild on changes"
          '';
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

