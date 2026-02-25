# Derivation Anatomy

A derivation is the core building block in Nix. It describes how to build something.

## Basic Structure

```nix
{ lib, stdenv, fetchurl }:

stdenv.mkDerivation {
  pname = "hello";
  version = "2.12";

  src = fetchurl {
    url = "mirror://gnu/hello/hello-2.12.tar.gz";
    sha256 = "sha256-jZkUKv2SV28wsM18tCqNxoCZmLxdYH2Idh9RLibH2yA=";
  };

  # Build inputs
  buildInputs = [ ];      # Runtime dependencies
  nativeBuildInputs = []; # Build-time dependencies

  # Build phases (all optional, have defaults)
  configurePhase = ''
    ./configure --prefix=$out
  '';

  buildPhase = ''
    make
  '';

  installPhase = ''
    make install
  '';

  meta = with lib; {
    description = "A program that produces a familiar greeting";
    homepage = "https://www.gnu.org/software/hello/";
    license = licenses.gpl3Plus;
    maintainers = with maintainers; [ ];
    platforms = platforms.all;
  };
}
```

## Key Attributes

### Source
```nix
# From URL
src = fetchurl {
  url = "https://example.com/source.tar.gz";
  sha256 = "sha256-...";
};

# From GitHub
src = fetchFromGitHub {
  owner = "owner";
  repo = "repo";
  rev = "v1.0.0";
  sha256 = "sha256-...";
};

# Local source (with filtering)
src = lib.cleanSource ./.;

# With specific files excluded
src = lib.cleanSourceWith {
  src = ./.;
  filter = path: type:
    !(lib.hasSuffix ".log" path);
};
```

### Dependencies

```nix
# Build-time only (compilers, build tools)
nativeBuildInputs = [ cmake ninja pkg-config ];

# Runtime dependencies (libraries)
buildInputs = [ openssl zlib ];

# Propagated to dependent packages
propagatedBuildInputs = [ python3Packages.requests ];

# Only for running tests
nativeCheckInputs = [ pytest ];
```

### Build Phases (in order)

1. **unpackPhase** - Extract source archive
2. **patchPhase** - Apply patches
3. **configurePhase** - Run ./configure or cmake
4. **buildPhase** - Run make or equivalent
5. **checkPhase** - Run tests (if doCheck = true)
6. **installPhase** - Install to $out
7. **fixupPhase** - Fix rpaths, wrap scripts, etc.

```nix
# Skip a phase
dontConfigure = true;
dontBuild = true;

# Add hooks before/after phases
preBuild = ''
  echo "Before building..."
'';

postInstall = ''
  mkdir -p $out/share/doc
  cp README.md $out/share/doc/
'';
```

## Output Paths

```nix
# Default output
$out  # /nix/store/...-hello-2.12

# Multiple outputs (reduces closure size)
outputs = [ "out" "dev" "doc" ];

# In installPhase, use specific outputs
installPhase = ''
  mkdir -p $out/bin $dev/include $doc/share/doc
  cp hello $out/bin/
  cp hello.h $dev/include/
  cp README.md $doc/share/doc/
'';
```

## Environment Variables

Available during build:
```nix
$out          # Output path
$src          # Source path
$name         # Derivation name
$system       # Build system (e.g., x86_64-linux)
$NIX_BUILD_CORES  # Number of CPU cores for parallel builds

# From dependencies
$PATH         # Includes bin/ from nativeBuildInputs
$PKG_CONFIG_PATH  # If pkg-config is in nativeBuildInputs
```

## Common Patterns

### Setting environment variables
```nix
env = {
  MY_VAR = "value";
};

# Or directly
MY_VAR = "value";
```

### Running commands at build time
```nix
buildPhase = ''
  runHook preBuild
  make -j$NIX_BUILD_CORES
  runHook postBuild
'';
```

### Patching
```nix
patches = [
  ./fix-build.patch
  (fetchpatch {
    url = "https://github.com/owner/repo/commit/abc123.patch";
    sha256 = "sha256-...";
  })
];

# Or substitute strings
postPatch = ''
  substituteInPlace src/config.h \
    --replace "/usr/local" "$out"
'';
```

### Install from source tree
```nix
installPhase = ''
  runHook preInstall
  
  mkdir -p $out/bin $out/share/man/man1
  cp myprogram $out/bin/
  cp myprogram.1 $out/share/man/man1/
  
  runHook postInstall
'';
```

## Debugging Derivations

```bash
# Build with verbose output
nix-build -K  # Keep build directory on failure

# Enter build environment
nix-shell '<nixpkgs>' -A hello

# Inside nix-shell, run phases manually
unpackPhase
cd $sourceRoot
configurePhase
buildPhase

# Show derivation
nix show-derivation /nix/store/...-hello.drv

# Show build log
nix log /nix/store/...-hello
```

