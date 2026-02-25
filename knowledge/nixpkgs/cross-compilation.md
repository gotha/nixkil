# Cross-Compilation in Nix

Cross-compilation builds packages for a different architecture than the build machine.

## Terminology

```
┌─────────────────────────────────────────────────────────────┐
│  Build Platform   →   Host Platform   →   Target Platform   │
│  (where we build)     (where it runs)     (what it targets) │
└─────────────────────────────────────────────────────────────┘

Example: Building a cross-compiler on x86_64 that runs on x86_64 
         but produces ARM binaries:
- Build:  x86_64-linux
- Host:   x86_64-linux  
- Target: aarch64-linux
```

## Basic Cross-Compilation

```nix
# In a flake
{
  outputs = { nixpkgs, ... }:
    let
      # Native packages for x86_64
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      
      # Cross-compile to aarch64
      pkgsCross = import nixpkgs {
        localSystem = "x86_64-linux";
        crossSystem = "aarch64-linux";
      };
    in {
      packages.x86_64-linux = {
        # Native build
        hello-native = pkgs.hello;
        
        # Cross-compiled for ARM
        hello-arm = pkgsCross.hello;
      };
    };
}
```

## Using pkgsCross

Nixpkgs provides pre-configured cross-compilation targets:

```nix
let
  pkgs = import <nixpkgs> {};
in {
  # ARM 64-bit Linux
  arm64 = pkgs.pkgsCross.aarch64-multiplatform.hello;
  
  # ARM 32-bit Linux
  arm32 = pkgs.pkgsCross.armv7l-hf-multiplatform.hello;
  
  # RISC-V 64-bit
  riscv = pkgs.pkgsCross.riscv64.hello;
  
  # Windows (MinGW)
  windows = pkgs.pkgsCross.mingwW64.hello;
  
  # macOS from Linux (limited support)
  macos = pkgs.pkgsCross.x86_64-darwin.hello;
  
  # Static Linux binaries
  static = pkgs.pkgsStatic.hello;
  
  # Musl-based Linux
  musl = pkgs.pkgsMusl.hello;
}
```

## Available Cross Targets

```nix
pkgs.pkgsCross.aarch64-multiplatform    # ARM64 Linux
pkgs.pkgsCross.armv7l-hf-multiplatform  # ARM32 Linux (hard float)
pkgs.pkgsCross.riscv64                  # RISC-V 64-bit
pkgs.pkgsCross.riscv32                  # RISC-V 32-bit
pkgs.pkgsCross.mingwW64                 # Windows 64-bit
pkgs.pkgsCross.mingw32                  # Windows 32-bit
pkgs.pkgsCross.wasi32                   # WebAssembly
pkgs.pkgsCross.avr                      # AVR microcontrollers
pkgs.pkgsCross.arm-embedded             # ARM bare-metal
```

## Writing Cross-Compatible Packages

```nix
{ lib, stdenv, fetchurl }:

stdenv.mkDerivation {
  pname = "mypackage";
  version = "1.0.0";

  src = fetchurl { /* ... */ };

  # Build-time tools (run on build machine)
  # Use packages from buildPackages
  depsBuildBuild = [ stdenv.cc ];
  
  # Build-time tools that target host
  nativeBuildInputs = [ pkg-config cmake ];
  
  # Libraries linked into final binary (for host platform)
  buildInputs = [ zlib openssl ];

  # Make cross-compilation work
  configurePlatforms = [ "build" "host" ];
  
  meta.platforms = lib.platforms.unix;
}
```

## Build vs Native Inputs

```nix
{
  # Runs on BUILD machine (your machine)
  # Example: code generators, compilers for build scripts
  nativeBuildInputs = [ cmake pkg-config ];
  
  # Runs on HOST machine (target architecture)
  # Example: libraries that get linked
  buildInputs = [ openssl zlib ];
  
  # Special: tools that run on build but produce code for build
  depsBuildBuild = [ ];
  
  # Special: tools that run on host and produce code for target
  # (only for compilers/cross-tools)
  depsBuildTarget = [ ];
}
```

## Checking for Cross-Compilation

```nix
{ lib, stdenv }:

stdenv.mkDerivation {
  # ...
  
  # Skip tests when cross-compiling (can't run target binaries)
  doCheck = !stdenv.buildPlatform.canExecute stdenv.hostPlatform;
  
  # Conditional logic
  postBuild = lib.optionalString (!stdenv.hostPlatform.isWindows) ''
    # Unix-only commands
  '';
  
  # Platform-specific dependencies
  buildInputs = [ zlib ] 
    ++ lib.optionals stdenv.hostPlatform.isLinux [ systemd ]
    ++ lib.optionals stdenv.hostPlatform.isDarwin [ darwin.apple_sdk.frameworks.Security ];
}
```

## Cross-Compiling in Flakes (Full Example)

```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);
    in {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          
          # Cross-compilation helpers
          crossPkgs = target: import nixpkgs {
            localSystem = system;
            crossSystem = target;
          };
        in {
          default = pkgs.hello;
          
          # Only available when building on Linux x86_64
        } // nixpkgs.lib.optionalAttrs (system == "x86_64-linux") {
          hello-aarch64 = (crossPkgs "aarch64-linux").hello;
          hello-arm = (crossPkgs "armv7l-linux").hello;
          hello-static = pkgs.pkgsStatic.hello;
        }
      );
    };
}
```

## Troubleshooting

```bash
# Check if package supports cross-compilation
nix-build '<nixpkgs>' -A pkgsCross.aarch64-multiplatform.hello

# Common issues:
# 1. Missing nativeBuildInputs vs buildInputs distinction
# 2. Tests trying to run target binaries
# 3. Build scripts assuming host == build platform
```

