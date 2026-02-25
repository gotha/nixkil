# stdenv and Build Phases

## What is stdenv?

`stdenv` (standard environment) provides the basic build environment for packages:
- A C compiler (GCC or Clang)
- Core utilities (coreutils, findutils, etc.)
- A shell (bash)
- Standard build tools (make, etc.)

## Build Phases Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Build Phases                             │
├─────────────────────────────────────────────────────────────┤
│ 1. unpackPhase    → Extract source archive                  │
│ 2. patchPhase     → Apply patches                           │
│ 3. configurePhase → Run ./configure, cmake, etc.            │
│ 4. buildPhase     → Compile (make, cargo build, etc.)       │
│ 5. checkPhase     → Run tests (if doCheck = true)           │
│ 6. installPhase   → Install to $out                         │
│ 7. fixupPhase     → Fix rpaths, wrap scripts, etc.          │
│ 8. installCheckPhase → Post-install tests (if enabled)      │
│ 9. distPhase      → Create distribution tarball (rare)      │
└─────────────────────────────────────────────────────────────┘
```

## Phase Hooks

Each phase has pre/post hooks:

```nix
prePatch = ''
  # Runs before patchPhase
'';

postPatch = ''
  # Runs after patchPhase
'';

preBuild = ''
  # Runs before buildPhase
'';

postBuild = ''
  # Runs after buildPhase
'';

# Same pattern for all phases:
# preUnpack, postUnpack
# preConfigure, postConfigure
# preInstall, postInstall
# preFixup, postFixup
# preCheck, postCheck
```

## Controlling Phases

```nix
# Skip phases
dontUnpack = true;       # Source is already unpacked
dontPatch = true;
dontConfigure = true;    # No configure step needed
dontBuild = true;        # Pre-built binaries
dontFixup = true;

# Enable optional phases
doCheck = true;          # Run checkPhase (tests)
doInstallCheck = true;   # Run installCheckPhase
```

## Custom Phase Implementation

```nix
buildPhase = ''
  runHook preBuild
  
  # Your custom build commands
  make -j$NIX_BUILD_CORES
  
  runHook postBuild
'';
```

Always use `runHook` to ensure pre/post hooks execute!

## Configure Phase Options

### Autotools (./configure)
```nix
configureFlags = [
  "--enable-feature"
  "--with-library=${lib}"
  "--prefix=$out"  # Usually automatic
];

# Add to configure script search path
preConfigure = ''
  configureFlagsArray+=(
    "--with-complex-arg=value with spaces"
  )
'';
```

### CMake
```nix
nativeBuildInputs = [ cmake ];

cmakeFlags = [
  "-DENABLE_FEATURE=ON"
  "-DCMAKE_BUILD_TYPE=Release"
];

# CMake is auto-detected, runs:
# cmake -DCMAKE_INSTALL_PREFIX=$out ...
```

### Meson
```nix
nativeBuildInputs = [ meson ninja ];

mesonFlags = [
  "-Dfeature=enabled"
];

# Meson is auto-detected
```

## Build Phase Options

```nix
# Parallel builds
enableParallelBuilding = true;  # Default: true
NIX_BUILD_CORES = 4;            # Or use $NIX_BUILD_CORES

# Make flags
makeFlags = [
  "PREFIX=$(out)"
  "CC=${stdenv.cc}/bin/cc"
];

# Build targets
buildFlags = [ "all" "docs" ];
buildTargets = [ "myprogram" ];
```

## Install Phase Options

```nix
installFlags = [
  "PREFIX=$(out)"
  "DESTDIR=$(out)"
];

installTargets = [ "install" "install-docs" ];

# Manual installation
installPhase = ''
  runHook preInstall
  
  mkdir -p $out/bin $out/share/man/man1
  cp myprogram $out/bin/
  cp myprogram.1 $out/share/man/man1/
  
  runHook postInstall
'';
```

## Fixup Phase

The fixup phase automatically:
- Patches ELF binaries with correct rpaths
- Compresses man pages
- Strips debug symbols (unless `dontStrip = true`)
- Wraps scripts with necessary environment

```nix
# Control fixup behavior
dontStrip = true;           # Keep debug symbols
dontPatchELF = true;        # Don't modify ELF rpaths
dontPatchShebangs = true;   # Don't fix script interpreters
dontAutoPatchelf = true;    # For autoPatchelfHook

# Add wrapper for scripts
postFixup = ''
  wrapProgram $out/bin/myscript \
    --prefix PATH : ${lib.makeBinPath [ coreutils ]} \
    --set MY_VAR "value"
'';
```

## Environment in Phases

```nix
# Available variables
$out              # Output directory
$src              # Source directory/file
$sourceRoot       # Extracted source root
$NIX_BUILD_CORES  # Number of cores
$NIX_BUILD_TOP    # Build directory

# From dependencies (in PATH, etc.)
${pkgs.python3}/bin/python3
${lib.getBin pkgs.coreutils}/bin/cat
```

## Debugging Build Failures

```bash
# Keep build directory on failure
nix-build -K ./default.nix

# Enter build environment
nix-shell ./default.nix

# Run phases manually
cd /tmp/nix-build-*
source $stdenv/setup
unpackPhase
patchPhase
configurePhase
buildPhase
```

