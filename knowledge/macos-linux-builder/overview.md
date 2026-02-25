# Linux Builder on macOS

## Why Do You Need a Linux Builder?

macOS cannot natively build Linux packages. When you try to build a Linux derivation on macOS, you'll get:

```
error: a]'x86_64-linux' is required to build '...' but I am a 'aarch64-darwin'
```

Use cases requiring Linux builds on macOS:
- Building Docker images
- Cross-compiling for Linux servers
- Testing NixOS configurations
- Building packages only available for Linux

## Options

| Option | Performance | Setup | Maintenance |
|--------|-------------|-------|-------------|
| nix-darwin linux-builder | Moderate | Simple | Automatic |
| Determinate Systems nixd | Native | Minimal | Automatic |
| Remote builder | Fastest | Complex | Manual |
| Docker Linux VM | Slowest | Simple | Manual |

## nix-darwin QEMU linux-builder

### Setup

```nix
# darwin-configuration.nix
{
  nix.linux-builder = {
    enable = true;
    
    # Builder VM resources
    config = {
      virtualisation = {
        cores = 4;
        memorySize = 8192;  # MB
        diskSize = 40000;   # MB
      };
    };
    
    # Max concurrent jobs
    maxJobs = 4;
    
    # Speed factor (relative to local builds)
    speedFactor = 1;
  };
}
```

### How It Works

1. nix-darwin creates a NixOS VM using QEMU
2. The VM runs as a launchd service
3. Nix automatically delegates Linux builds to the VM
4. Results are copied back to macOS

### Managing the Builder

```bash
# Check builder status
sudo launchctl list | grep linux-builder

# Restart builder
sudo launchctl stop org.nixos.linux-builder
sudo launchctl start org.nixos.linux-builder

# View builder logs
sudo tail -f /var/log/linux-builder.log
```

### Advanced Configuration

```nix
{
  nix.linux-builder = {
    enable = true;
    
    config = ({ pkgs, ... }: {
      virtualisation = {
        cores = 8;
        memorySize = 16384;
        diskSize = 100000;
      };
      
      # Custom packages in the builder
      environment.systemPackages = [ pkgs.htop ];
      
      # Enable SSH for debugging
      services.openssh.enable = true;
    });
  };
}
```

## Determinate Systems nixd

Determinate Systems provides a native Linux builder that runs Linux binaries directly using macOS virtualization framework (Rosetta 2 for x86_64).

### Installation

```bash
# Install Determinate Nix (includes nixd)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh
```

### Features

- **Native performance**: Uses Apple's Virtualization framework
- **Automatic**: No configuration needed
- **Seamless**: Works transparently with Nix
- **Resource efficient**: Lightweight compared to QEMU

### How It Works

1. nixd runs as a daemon on macOS
2. When Linux builds are needed, it creates lightweight VMs
3. Uses Rosetta 2 for x86_64 translation on Apple Silicon
4. Manages VM lifecycle automatically

### Checking Status

```bash
# Check if nixd is running
launchctl list | grep determinate

# View logs
log show --predicate 'subsystem == "systems.determinate.nix"' --last 1h
```

## Comparison

### QEMU linux-builder

**Pros:**
- Works with standard Nix installation
- Highly configurable
- Persistent VM state

**Cons:**
- Higher resource usage
- Slower than native
- Requires nix-darwin

### Determinate nixd

**Pros:**
- Native-like performance
- Zero configuration
- Lightweight
- Works on plain macOS

**Cons:**
- Requires Determinate Systems Nix installer
- Less configurable

## Remote Builders

For best performance, use a dedicated Linux machine:

```nix
# configuration.nix or darwin-configuration.nix
{
  nix.distributedBuilds = true;
  
  nix.buildMachines = [
    {
      hostName = "linux-builder.local";
      system = "x86_64-linux";
      maxJobs = 8;
      speedFactor = 2;
      supportedFeatures = [ "nixos-test" "big-parallel" "kvm" ];
      mandatoryFeatures = [];
      sshUser = "builder";
      sshKey = "/etc/nix/builder_ed25519";
    }
  ];
}
```

### SSH Setup

```bash
# Generate key
sudo ssh-keygen -t ed25519 -f /etc/nix/builder_ed25519 -N ""

# Add public key to builder machine
cat /etc/nix/builder_ed25519.pub | ssh builder@linux-builder.local 'cat >> ~/.ssh/authorized_keys'

# Test connection
sudo ssh -i /etc/nix/builder_ed25519 builder@linux-builder.local
```

## Troubleshooting

```bash
# Check if builder is being used
nix build --print-build-logs nixpkgs#hello --system x86_64-linux

# Test builder connection
nix store ping --store ssh://builder@linux-builder.local

# Force rebuild on specific machine
nix build --builders 'ssh://builder@linux-builder.local' ...
```

