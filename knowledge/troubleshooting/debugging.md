# Debugging Techniques

## Evaluation Debugging

### Show Trace

```bash
# Show full stack trace on errors
nix build --show-trace

nix eval --show-trace .#packages.x86_64-linux.default
```

### builtins.trace

```nix
# Print value during evaluation
let
  x = builtins.trace "x is being evaluated" 42;
in x + 1

# Trace with expression value
let
  config = { port = 8080; };
in builtins.trace "config: ${builtins.toJSON config}" config.port

# Conditional tracing
lib.traceIf (x > 100) "x is large: ${toString x}" x

# Trace and return value
lib.traceValSeq myAttrSet
```

### REPL Debugging

```bash
# Start Nix REPL
nix repl

# Load a flake
nix repl .#

# Or load nixpkgs
:l <nixpkgs>
```

```nix
# In REPL
:t expression        # Show type
:p expression        # Print value
:b derivation        # Build derivation
:doc builtins.map    # Show documentation
:e pkgs.hello        # Edit package
```

## Build Debugging

### Keep Build Directory

```bash
# Don't delete build directory on failure
nix-build -K

# Find the kept directory
ls /tmp/nix-build-*
```

### Enter Build Environment

```bash
# Method 1: nix-shell into package
nix-shell '<nixpkgs>' -A hello

# Method 2: nix develop with package inputs
nix develop .#myPackage

# Then run phases manually
cd /tmp
unpackPhase
cd $sourceRoot
patchPhase
configurePhase
buildPhase
checkPhase
installPhase
```

### Build Logs

```bash
# Show build log for a derivation
nix log /nix/store/xxx.drv

# Or by package
nix log nixpkgs#hello

# Follow build output
nix build -L .#myPackage
```

## Dependency Analysis

### nix why-depends

```bash
# Why does package A include package B?
nix why-depends .#myApp nixpkgs#openssl

# With full path
nix why-depends /nix/store/xxx-myapp /nix/store/yyy-openssl
```

### nix-diff

```bash
# Compare two derivations
nix-diff /nix/store/a.drv /nix/store/b.drv

# Find what changed between two builds
nix-diff $(nix path-info nixpkgs#hello) $(nix path-info nixpkgs#hello --derivation)
```

### nix-tree

```bash
# Interactive dependency tree viewer
nix-tree .#myPackage

# Show closure size breakdown
nix-tree --derivation .#myPackage
```

### Closure Analysis

```bash
# Show closure size
nix path-info -sSh .#myPackage

# Recursive closure
nix path-info -rsSh .#myPackage

# Find what's taking space
nix path-info -rsSh .#myPackage | sort -k2 -h

# Count dependencies
nix path-info -r .#myPackage | wc -l
```

## Flake Debugging

### Inspect Flake

```bash
# Show flake outputs
nix flake show

# Show metadata
nix flake metadata

# Show inputs
nix flake metadata --json | jq '.locks.nodes'

# Evaluate specific output
nix eval .#packages.x86_64-linux.default.name
```

### Check Flake

```bash
# Validate flake
nix flake check

# With verbose output
nix flake check -L

# Check specific system
nix flake check --system x86_64-linux
```

## NixOS Debugging

### Test Configuration

```bash
# Build without switching
sudo nixos-rebuild build

# Test in VM
sudo nixos-rebuild build-vm
./result/bin/run-*-vm

# Dry run (show what would change)
sudo nixos-rebuild dry-activate
```

### Boot Issues

```bash
# Boot to previous generation
# Select from bootloader menu

# List generations
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system

# Rollback
sudo nixos-rebuild switch --rollback
```

### Service Issues

```bash
# Check service status
systemctl status myservice

# View logs
journalctl -u myservice -f

# Check configuration
systemctl cat myservice
```

## Store Debugging

### Verify Store

```bash
# Check store integrity
nix-store --verify --check-contents

# Repair corrupted paths
nix-store --verify --check-contents --repair
```

### Query Store

```bash
# Find path by hash
nix-store -q --hash /nix/store/xxx

# Find references (dependencies)
nix-store -q --references /nix/store/xxx

# Find referrers (what depends on this)
nix-store -q --referrers /nix/store/xxx

# Find derivation
nix-store -q --deriver /nix/store/xxx
```

## Performance Profiling

```bash
# Measure evaluation time
time nix eval .#packages.x86_64-linux.default

# Profile evaluation (requires nix with profiling)
nix eval --profile-file profile.html .#something

# Measure build time
time nix build .#myPackage

# Show store path build times
nix-store --query --requisites --include-outputs /nix/store/xxx | \
  xargs -I{} sh -c 'echo "$(nix-store --query --deriver {}) $(du -sh {})"'
```

## Tips

1. **Start simple**: Minimize the example that reproduces the error
2. **Check inputs**: Ensure all inputs are what you expect
3. **Use REPL**: Interactive exploration is faster
4. **Read error messages**: Nix errors are usually informative
5. **Check nixpkgs issues**: Someone may have hit the same problem
6. **Ask for --show-trace**: First thing to try with errors

