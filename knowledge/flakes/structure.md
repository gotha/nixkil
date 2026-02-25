# Flake Structure

## Basic Flake Anatomy

```nix
{
  description = "A short description of your project";

  inputs = {
    # Dependencies (other flakes or sources)
  };

  outputs = { self, nixpkgs, ... }@inputs: {
    # What this flake provides
  };
}
```

## Minimal Working Flake

```nix
{
  description = "My project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.${system}.default = pkgs.hello;
      devShells.${system}.default = pkgs.mkShell {
        packages = [ pkgs.hello ];
      };
    };
}
```

## Multi-System Flake

```nix
{
  description = "Cross-platform project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages.default = pkgs.hello;
        devShells.default = pkgs.mkShell {
          packages = [ pkgs.hello ];
        };
        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}
```

## Standard Output Types

```nix
outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    # Packages (nix build .#name)
    packages.${system} = {
      default = pkgs.hello;
      myPackage = pkgs.callPackage ./package.nix { };
    };

    # Development shells (nix develop)
    devShells.${system} = {
      default = pkgs.mkShell { /* ... */ };
      ci = pkgs.mkShell { /* ... */ };
    };

    # Formatter (nix fmt)
    formatter.${system} = pkgs.nixfmt-rfc-style;

    # Apps (nix run)
    apps.${system}.default = {
      type = "app";
      program = "${pkgs.hello}/bin/hello";
    };

    # Checks (nix flake check)
    checks.${system} = {
      formatting = pkgs.runCommand "check-format" { } ''
        ${pkgs.nixfmt-rfc-style}/bin/nixfmt --check ${self}/*.nix
        touch $out
      '';
    };

    # NixOS configurations
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      inherit system;
      modules = [ ./configuration.nix ];
    };

    # Overlays for other flakes to use
    overlays.default = final: prev: {
      myPackage = final.callPackage ./package.nix { };
    };

    # NixOS/home-manager modules
    nixosModules.default = import ./module.nix;
    homeManagerModules.default = import ./hm-module.nix;

    # Library functions
    lib = {
      myHelper = x: x + 1;
    };

    # Templates (nix flake init -t)
    templates = {
      default = {
        path = ./template;
        description = "A basic template";
      };
    };
  };
```

## Flake with Custom Package

```nix
{
  description = "Project with custom package";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        myPackage = pkgs.callPackage ./package.nix { };
      in {
        packages = {
          default = myPackage;
          inherit myPackage;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ myPackage ];
          packages = [ pkgs.nixfmt-rfc-style ];
        };
      }
    );
}
```

## Flake Commands Reference

```bash
# Build default package
nix build

# Build specific package
nix build .#myPackage

# Enter development shell
nix develop

# Run default app
nix run

# Check flake outputs
nix flake check

# Format with configured formatter
nix fmt

# Show flake metadata
nix flake metadata

# Update all inputs
nix flake update

# Update specific input
nix flake lock --update-input nixpkgs

# Initialize from template
nix flake init -t github:owner/repo#template
```

## Lock File

The `flake.lock` file pins exact versions:
- Generated automatically on first `nix build` or `nix flake update`
- Commit to version control for reproducibility
- Update with `nix flake update`

