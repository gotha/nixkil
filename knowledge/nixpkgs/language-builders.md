# Language-Specific Builders

Nixpkgs provides specialized builders for different programming languages.

## Python: buildPythonPackage

```nix
{ lib, python3Packages, fetchPypi }:

python3Packages.buildPythonPackage rec {
  pname = "requests";
  version = "2.31.0";
  format = "pyproject";  # or "setuptools", "flit", "wheel"

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-...";
  };

  # Build-time dependencies
  build-system = [
    python3Packages.setuptools
  ];

  # Runtime dependencies
  dependencies = [
    python3Packages.urllib3
    python3Packages.certifi
  ];

  # Test dependencies
  nativeCheckInputs = [
    python3Packages.pytest
  ];

  pythonImportsCheck = [ "requests" ];

  meta = { /* ... */ };
}
```

### Python application (not importable)
```nix
python3Packages.buildPythonApplication {
  pname = "mycli";
  # ... same as buildPythonPackage
}
```

## Go: buildGoModule

```nix
{ lib, buildGoModule, fetchFromGitHub }:

buildGoModule rec {
  pname = "mygo";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "owner";
    repo = "repo";
    rev = "v${version}";
    hash = "sha256-...";
  };

  # Go module hash (use lib.fakeHash first, then update)
  vendorHash = "sha256-...";
  # Or if no dependencies:
  vendorHash = null;

  # For private modules
  proxyVendor = true;

  # Build specific subpackages
  subPackages = [ "cmd/mygo" ];

  # Build flags
  ldflags = [
    "-s" "-w"
    "-X main.version=${version}"
  ];

  meta = { /* ... */ };
}
```

## Rust: buildRustPackage

```nix
{ lib, rustPlatform, fetchFromGitHub }:

rustPlatform.buildRustPackage rec {
  pname = "myrust";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "owner";
    repo = "repo";
    rev = "v${version}";
    hash = "sha256-...";
  };

  # Cargo.lock hash
  cargoHash = "sha256-...";
  # Or use cargoLock for more control:
  # cargoLock.lockFile = ./Cargo.lock;

  # Native dependencies
  nativeBuildInputs = [ pkg-config ];
  buildInputs = [ openssl ];

  # Cargo features
  buildFeatures = [ "feature1" "feature2" ];

  # Build specific binaries
  cargoBuildFlags = [ "--bin" "mybin" ];

  meta = { /* ... */ };
}
```

## Node.js: buildNpmPackage

```nix
{ lib, buildNpmPackage, fetchFromGitHub }:

buildNpmPackage rec {
  pname = "mynode";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "owner";
    repo = "repo";
    rev = "v${version}";
    hash = "sha256-...";
  };

  npmDepsHash = "sha256-...";

  # If package.json is in a subdirectory
  sourceRoot = "${src.name}/packages/mypackage";

  # Build commands
  npmBuildScript = "build";  # npm run build

  meta = { /* ... */ };
}
```

## Java: Maven

```nix
{ lib, maven, fetchFromGitHub }:

maven.buildMavenPackage rec {
  pname = "myjava";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "owner";
    repo = "repo";
    rev = "v${version}";
    hash = "sha256-...";
  };

  mvnHash = "sha256-...";

  installPhase = ''
    mkdir -p $out/share/java
    cp target/*.jar $out/share/java/
  '';

  meta = { /* ... */ };
}
```

## Haskell: haskellPackages

```nix
{ lib, haskellPackages, fetchFromGitHub }:

haskellPackages.mkDerivation {
  pname = "myhaskell";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "owner";
    repo = "repo";
    rev = "v${version}";
    hash = "sha256-...";
  };

  isLibrary = false;
  isExecutable = true;

  libraryHaskellDepends = [ /* ... */ ];
  executableHaskellDepends = [ /* ... */ ];

  meta = { /* ... */ };
}
```

## Getting Dependency Hashes

```bash
# Go vendorHash
nix-build -E '(import <nixpkgs> {}).buildGoModule { 
  pname = "test"; version = "0"; 
  src = ./.; vendorHash = lib.fakeHash; 
}'
# Copy the hash from the error message

# Rust cargoHash (similar approach)
# Use lib.fakeHash, build, copy real hash from error

# Node npmDepsHash
# Use lib.fakeHash, build, copy real hash from error

# Or use prefetch tools
nix-prefetch-github owner repo --rev v1.0.0
```

