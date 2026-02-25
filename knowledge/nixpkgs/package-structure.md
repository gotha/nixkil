# Nixpkgs Package Structure

## Standard Package Layout

Packages in nixpkgs typically follow this structure:

```
pkgs/
├── by-name/              # New-style packages (preferred)
│   └── he/
│       └── hello/
│           └── package.nix
├── applications/         # GUI applications
│   └── editors/
│       └── vim/
│           └── default.nix
├── development/          # Development tools
│   ├── compilers/
│   ├── libraries/
│   └── tools/
├── servers/              # Server software
└── tools/                # CLI tools
```

## by-name Convention (Preferred)

New packages should use the `pkgs/by-name` structure:

```
pkgs/by-name/he/hello/package.nix
              ^^
              First two letters of package name
```

```nix
# pkgs/by-name/he/hello/package.nix
{
  lib,
  stdenv,
  fetchurl,
}:

stdenv.mkDerivation (finalAttrs: {
  pname = "hello";
  version = "2.12";

  src = fetchurl {
    url = "mirror://gnu/hello/hello-${finalAttrs.version}.tar.gz";
    hash = "sha256-jZkUKv2SV28wsM18tCqNxoCZmLxdYH2Idh9RLibH2yA=";
  };

  meta = {
    description = "A program that produces a familiar greeting";
    homepage = "https://www.gnu.org/software/hello/";
    license = lib.licenses.gpl3Plus;
    maintainers = with lib.maintainers; [ ];
    mainProgram = "hello";
    platforms = lib.platforms.all;
  };
})
```

## Package Naming Conventions

```nix
pname = "my-package";           # Lowercase, hyphens
version = "1.2.3";              # Semantic versioning
# Final name: my-package-1.2.3
```

### Special cases
```nix
# Python packages
pname = "requests";             # Not python3-requests

# Versioned packages
pname = "gcc";
version = "13.2.0";

# Pre-release
version = "1.0.0-rc1";
version = "0-unstable-2024-01-15";  # For git snapshots
```

## Meta Attributes

```nix
meta = with lib; {
  # Required
  description = "Short description (one line, no period)";
  
  # Highly recommended
  homepage = "https://example.com";
  license = licenses.mit;  # See lib.licenses for options
  maintainers = with maintainers; [ username ];
  platforms = platforms.unix;  # or platforms.linux, platforms.darwin, etc.
  
  # Optional
  mainProgram = "my-program";  # If different from pname
  changelog = "https://github.com/owner/repo/releases";
  longDescription = ''
    Longer description that can span
    multiple lines.
  '';
  
  # Mark as broken or insecure
  broken = true;  # Doesn't build
  insecure = true;  # Has security issues
  
  # Unfree software
  license = licenses.unfree;
  # Requires: nixpkgs.config.allowUnfree = true;
};
```

## Common Licenses

```nix
lib.licenses.mit
lib.licenses.asl20      # Apache 2.0
lib.licenses.gpl3Only
lib.licenses.gpl3Plus
lib.licenses.bsd3
lib.licenses.isc
lib.licenses.mpl20      # Mozilla Public License 2.0
lib.licenses.unfree
lib.licenses.free       # Generic free license
```

## Platform Specifications

```nix
# All platforms
platforms = lib.platforms.all;

# By OS
platforms = lib.platforms.linux;
platforms = lib.platforms.darwin;
platforms = lib.platforms.unix;  # Linux + Darwin + BSD

# Specific architectures
platforms = [ "x86_64-linux" "aarch64-linux" ];

# Exclude platforms
platforms = lib.platforms.linux ++ lib.platforms.darwin;
badPlatforms = [ "aarch64-darwin" ];  # Broken on Apple Silicon
```

## Source Hash Formats

```nix
# Preferred: SRI format
hash = "sha256-jZkUKv2SV28wsM18tCqNxoCZmLxdYH2Idh9RLibH2yA=";

# Also accepted
sha256 = "0123456789abcdef...";  # Base16 (64 chars)
sha256 = "sha256-...";          # SRI in sha256 attribute

# Get hash for new package
# nix-prefetch-url https://example.com/file.tar.gz
# nix-prefetch-github owner repo --rev v1.0.0
```

## Testing Your Package

```bash
# Build the package
nix-build -E 'with import <nixpkgs> {}; callPackage ./package.nix {}'

# Or with flakes
nix build --impure --expr '(import <nixpkgs> {}).callPackage ./package.nix {}'

# Check for common issues
nix-shell -p nixpkgs-review --run "nixpkgs-review rev HEAD"
```

## Passthru Attributes

```nix
passthru = {
  # Additional tests
  tests = {
    version = testers.testVersion { package = finalAttrs.finalPackage; };
  };
  
  # Update script
  updateScript = nix-update-script { };
  
  # Expose internals for dependent packages
  inherit src;
};
```

