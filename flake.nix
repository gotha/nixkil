{
  description = "nixkil - Agent skill for Nix language, package manager, and NixOS";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      let
        pythonEnv = pkgs.python311.withPackages (ps: [
          ps.pytest
          ps.pytest-cov
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          name = "nixkil-dev";

          packages = with pkgs; [
            # Nix tooling
            nixfmt-rfc-style
            nil
            nix-tree
            nix-diff
            statix

            # Development tools
            direnv
            nix-direnv

            # Python for tools and testing
            pythonEnv
          ];

          shellHook = ''
            echo "🔧 nixkil development environment"
            echo "   Nix version: $(nix --version)"
            echo ""
          '';
        };

        apps.test = {
          type = "app";
          program = toString (pkgs.writeShellScript "run-tests" ''
            cd ${self}
            ${pythonEnv}/bin/python -m pytest tests/ -v --ignore=tests/test_examples.py -p no:cacheprovider "$@"
          '');
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

