# Troubleshooting Common Nix Errors

## Evaluation Errors

### "undefined variable"

```
error: undefined variable 'pkgs'
```

**Cause:** Variable not in scope.

**Solutions:**
```nix
# Add to function arguments
{ pkgs, ... }: { }

# Or use with statement
with pkgs; [ git vim ]

# Check for typos
pkgs.hello  # not pkg.hello
```

### "attribute missing"

```
error: attribute 'nonexistent' missing
```

**Cause:** Accessing non-existent attribute.

**Solutions:**
```nix
# Use ? to check existence
if attrs ? key then attrs.key else "default"

# Use or for default
attrs.key or "default"

# Check attribute names
builtins.attrNames attrs
```

### "infinite recursion"

```
error: infinite recursion encountered
```

**Cause:** Self-referential definition.

**Solutions:**
```nix
# BAD: Self-reference
rec { x = x + 1; }

# GOOD: Use let binding
let x = 1; in { inherit x; y = x + 1; }

# Check for circular module imports
```

## Build Errors

### "hash mismatch"

```
error: hash mismatch in fixed-output derivation
  specified: sha256-AAAA...
  got:       sha256-BBBB...
```

**Cause:** Source content changed or wrong hash.

**Solutions:**
```bash
# Update hash to the "got" value
sha256 = "sha256-BBBB...";

# Or use lib.fakeHash to get correct hash
sha256 = lib.fakeHash;

# Prefetch to get correct hash
nix-prefetch-url https://example.com/file.tar.gz
nix-prefetch-github owner repo --rev v1.0
```

### "builder failed"

```
error: builder for '/nix/store/...' failed with exit code 1
```

**Solutions:**
```bash
# Keep build directory for inspection
nix-build -K

# Show build log
nix log /nix/store/xxx.drv

# Enter build environment
nix-shell '<nixpkgs>' -A packageName
cd /tmp
unpackPhase
cd source
configurePhase
buildPhase  # Run phases manually
```

### "dependency cycle"

```
error: cycle detected in build
```

**Cause:** Package A depends on B which depends on A.

**Solutions:**
```nix
# Use nativeBuildInputs for build-time deps
nativeBuildInputs = [ cmake ];

# Break cycle with overrideAttrs
pkg.overrideAttrs (old: {
  buildInputs = lib.remove problematicDep old.buildInputs;
})
```

## Flake Errors

### "path not found"

```
error: path '/nix/store/.../flake.nix' does not exist
```

**Cause:** Files not tracked by git.

**Solution:**
```bash
git add flake.nix flake.lock
# Or add all files
git add -A
```

### "flake has no attribute"

```
error: flake 'path:.' does not provide attribute 'packages.x86_64-linux.default'
```

**Cause:** Missing output or wrong system.

**Solution:**
```bash
# List available outputs
nix flake show

# Check your system
nix eval --impure --expr 'builtins.currentSystem'

# Ensure flake supports your system
```

### "follows cycle"

```
error: cycle detected in flake input follows
```

**Cause:** Circular follows declarations.

**Solution:**
```nix
# BAD: Circular
inputs.a.inputs.b.follows = "b";
inputs.b.inputs.a.follows = "a";

# GOOD: One direction
inputs.a.inputs.nixpkgs.follows = "nixpkgs";
inputs.b.inputs.nixpkgs.follows = "nixpkgs";
```

## Store Errors

### "store path already exists"

**Solution:**
```bash
# Garbage collect
nix-collect-garbage -d

# Or delete specific path (careful!)
nix-store --delete /nix/store/xxx
```

### "cannot connect to daemon"

```
error: cannot connect to daemon at '/nix/var/nix/daemon-socket/socket'
```

**Solutions:**
```bash
# macOS
sudo launchctl kickstart -k system/org.nixos.nix-daemon

# Linux (systemd)
sudo systemctl restart nix-daemon
```

## Debugging Tools

```bash
# Show evaluation trace
nix build --show-trace

# Explain why package is in closure
nix why-depends .#package .#dependency

# Compare two derivations
nix-diff /nix/store/a.drv /nix/store/b.drv

# Visualize dependency tree
nix-tree .#package

# Check store path info
nix path-info -rsSh .#package

# Repair store
nix-store --verify --check-contents --repair
```

## Dynamically Linked Binaries

### "No such file or directory" or "Exec format error"

```
./my-binary: No such file or directory
```

or

```
./my-binary: cannot execute: required file not found
```

**Cause:** Pre-compiled binaries expect the dynamic linker at `/lib64/ld-linux-x86-64.so.2` or similar paths that don't exist on NixOS. This happens with:
- Downloaded binaries (VSCode extensions, language servers, etc.)
- Proprietary software
- Binaries from Docker images or other Linux distros

### Solution 1: nix-ld (Recommended First Approach)

[nix-ld](https://github.com/nix-community/nix-ld) provides a compatibility shim that makes most dynamically linked binaries work automatically.

**Enable in NixOS configuration:**

```nix
# configuration.nix or in your NixOS module
{ config, pkgs, ... }:
{
  programs.nix-ld.enable = true;

  # Optional: Add common libraries that binaries might need
  programs.nix-ld.libraries = with pkgs; [
    stdenv.cc.cc.lib
    zlib
    openssl
    curl
    glib
    # Add more as needed based on what binaries require
  ];
}
```

**Rebuild and try the binary:**

```bash
sudo nixos-rebuild switch
./my-binary  # Should work now
```

**Finding missing libraries:**

```bash
# Check what libraries a binary needs
ldd ./my-binary

# Find which Nix package provides a library
nix-locate libssl.so.1.1 | head
```

### Solution 2: buildFHSEnv (Fallback)

If nix-ld doesn't work (complex binaries, hardcoded paths, etc.), use [buildFHSEnv](https://ryantm.github.io/nixpkgs/builders/special/fhs-environments/) to create a FHS-compliant environment.

**For running a binary:**

```nix
# shell.nix or in a flake devShell
{ pkgs ? import <nixpkgs> {} }:

let
  fhsEnv = pkgs.buildFHSEnv {
    name = "my-binary-env";
    targetPkgs = pkgs: with pkgs; [
      # Common libraries
      stdenv.cc.cc.lib
      zlib
      glib
      # Add libraries your binary needs
      openssl
      curl
      xorg.libX11
      xorg.libXcursor
    ];
    runScript = "bash";
  };
in
fhsEnv
```

**Run with:**

```bash
nix-shell
# Now inside FHS environment
./my-binary
```

**For a specific binary wrapper:**

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.buildFHSEnv {
  name = "my-wrapped-binary";
  targetPkgs = pkgs: with pkgs; [
    stdenv.cc.cc.lib
    zlib
    openssl
  ];
  runScript = "/path/to/my-binary";
}
```

**In a flake:**

```nix
{
  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.my-binary =
      let pkgs = nixpkgs.legacyPackages.x86_64-linux;
      in pkgs.buildFHSEnv {
        name = "my-binary";
        targetPkgs = pkgs: with pkgs; [
          stdenv.cc.cc.lib
          zlib
        ];
        runScript = "${./my-binary}";
      };
  };
}
```

### When to Use Which

| Scenario | Recommended Solution |
|----------|---------------------|
| Simple binaries, VSCode extensions | nix-ld |
| Most downloaded CLI tools | nix-ld |
| Complex GUI applications | buildFHSEnv |
| Binaries with hardcoded `/usr` paths | buildFHSEnv |
| Steam, proprietary games | buildFHSEnv (or steam-run) |
| nix-ld doesn't work | buildFHSEnv |

### Debugging Library Issues

```bash
# See what dynamic linker a binary expects
file ./my-binary

# List required libraries
ldd ./my-binary

# Check for missing libraries (shows "not found")
ldd ./my-binary | grep "not found"

# Find package providing a library
nix-locate --top-level libfoo.so

# Trace library loading
LD_DEBUG=libs ./my-binary 2>&1 | head -50
```

## Common Pitfalls

### Using <nixpkgs> (impure)

```nix
# BAD: Impure, uses NIX_PATH
import <nixpkgs> {}

# GOOD: Use flake input
inputs.nixpkgs.legacyPackages.${system}
```

### Forgetting to use runHook

```nix
# BAD: Skips pre/post hooks
buildPhase = ''
  make
'';

# GOOD: Runs hooks
buildPhase = ''
  runHook preBuild
  make
  runHook postBuild
'';
```

### Wrong nativeBuildInputs vs buildInputs

```nix
# BAD: cmake in buildInputs (runs on target, not build machine)
buildInputs = [ cmake ];

# GOOD: Build tools in nativeBuildInputs
nativeBuildInputs = [ cmake ];
buildInputs = [ openssl ];  # Runtime deps
```

