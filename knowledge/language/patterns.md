# Common Nix Patterns

## Overlays

Overlays modify or extend nixpkgs. They are functions that take two arguments:
- `final`: The final fixed-point of the package set (use for dependencies)
- `prev`: The previous package set (use for the original package)

```nix
# Basic overlay structure
final: prev: {
  # Add a new package
  myPackage = final.callPackage ./my-package.nix { };

  # Override an existing package
  vim = prev.vim.override {
    python3 = final.python311;
  };
}
```

### Using overlays in a flake

```nix
{
  outputs = { self, nixpkgs }:
    let
      myOverlay = final: prev: {
        myTool = prev.hello.overrideAttrs (old: {
          pname = "my-tool";
        });
      };

      pkgs = import nixpkgs {
        system = "x86_64-linux";
        overlays = [ myOverlay ];
      };
    in {
      packages.x86_64-linux.default = pkgs.myTool;
    };
}
```

## Overrides

### override vs overrideAttrs

```nix
# override: Change function arguments (inputs to the package)
pkgs.hello.override {
  stdenv = pkgs.clangStdenv;  # Build with clang instead of gcc
}

# overrideAttrs: Change derivation attributes
pkgs.hello.overrideAttrs (oldAttrs: {
  pname = "hello-custom";
  patches = oldAttrs.patches or [] ++ [ ./my-patch.patch ];
  buildInputs = oldAttrs.buildInputs ++ [ pkgs.zlib ];
})
```

### overrideAttrs with finalAttrs

```nix
# New pattern: finalAttrs gives access to the final attribute set
pkgs.hello.overrideAttrs (finalAttrs: prevAttrs: {
  version = "2.0";
  src = pkgs.fetchurl {
    url = "mirror://gnu/hello/hello-${finalAttrs.version}.tar.gz";
    hash = "sha256-abc123...";
  };
})
```

## callPackage

The `callPackage` pattern provides automatic dependency injection.

```nix
# my-package.nix
{ lib, stdenv, fetchurl, zlib }:  # Dependencies as function arguments

stdenv.mkDerivation {
  pname = "my-package";
  version = "1.0";
  # ...
}
```

```nix
# Usage
pkgs.callPackage ./my-package.nix { }

# With overrides
pkgs.callPackage ./my-package.nix {
  zlib = pkgs.zlib-ng;  # Use different zlib
}
```

### How callPackage works

```nix
# Simplified implementation
callPackage = path: overrides:
  let
    f = import path;
    args = builtins.intersectAttrs (builtins.functionArgs f) pkgs;
  in
    f (args // overrides);
```

## lib Functions

The `lib` attrset contains many useful functions.

### List operations
```nix
lib.flatten [ [ 1 2 ] [ 3 [ 4 ] ] ]       # [ 1 2 3 4 ]
lib.unique [ 1 2 1 3 ]                     # [ 1 2 3 ]
lib.take 2 [ 1 2 3 4 ]                     # [ 1 2 ]
lib.drop 2 [ 1 2 3 4 ]                     # [ 3 4 ]
lib.partition (x: x > 2) [ 1 2 3 4 ]       # { right = [ 3 4 ]; wrong = [ 1 2 ]; }
```

### Attrset operations
```nix
lib.filterAttrs (n: v: v != null) { a = 1; b = null; }  # { a = 1; }
lib.mapAttrs' (n: v: { name = "prefix_${n}"; value = v; }) { a = 1; }
lib.recursiveUpdate { a.b = 1; } { a.c = 2; }  # { a = { b = 1; c = 2; }; }
lib.attrByPath [ "a" "b" ] "default" { a.b = "value"; }  # "value"
```

### String operations
```nix
lib.concatStrings [ "a" "b" "c" ]          # "abc"
lib.concatStringsSep ", " [ "a" "b" ]      # "a, b"
lib.splitString ":" "a:b:c"                # [ "a" "b" "c" ]
lib.hasPrefix "hello" "hello world"        # true
lib.removeSuffix ".nix" "file.nix"         # "file"
lib.optionalString true "included"         # "included"
lib.optionalString false "excluded"        # ""
```

### Conditionals
```nix
lib.optional true "value"                  # [ "value" ]
lib.optional false "value"                 # [ ]
lib.optionals true [ "a" "b" ]             # [ "a" "b" ]
lib.optionalAttrs true { a = 1; }          # { a = 1; }
lib.mkIf true { setting = "value"; }       # For NixOS modules
```

### Merging
```nix
lib.mkMerge [ { a = 1; } { b = 2; } ]      # { a = 1; b = 2; }
lib.mkForce "value"                        # Override with high priority
lib.mkDefault "value"                      # Set with low priority
```

## Module Pattern

NixOS modules follow a standard structure:

```nix
{ config, lib, pkgs, ... }:

let
  cfg = config.services.myService;
in {
  options.services.myService = {
    enable = lib.mkEnableOption "my service";
    
    port = lib.mkOption {
      type = lib.types.port;
      default = 8080;
      description = "Port to listen on";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.myService = {
      wantedBy = [ "multi-user.target" ];
      serviceConfig.ExecStart = "${pkgs.myService}/bin/myservice --port ${toString cfg.port}";
    };
  };
}
```

## Fixed-Point Pattern (lib.fix)

```nix
# Self-referential attrsets
lib.fix (self: {
  a = 1;
  b = self.a + 1;  # References itself
})
# Result: { a = 1; b = 2; }

# This is how overlays work internally
lib.fix (self: 
  lib.foldl' (acc: overlay: acc // (overlay self acc)) basePackages overlays
)
```

