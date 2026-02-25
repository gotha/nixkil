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

