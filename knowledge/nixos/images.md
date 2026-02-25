# NixOS Image Generation

## Overview

NixOS can generate various image formats for deployment:
- VM images (QEMU, VirtualBox, VMware)
- Cloud images (AWS AMI, Azure, GCP)
- Container images (Docker/OCI)
- ISO installation media
- SD card images (Raspberry Pi)

## Using nixos-generators

```bash
# Install nixos-generators
nix-env -iA nixpkgs.nixos-generators

# Or use directly with flakes
nix run github:nix-community/nixos-generators -- --help
```

### Generate VM Images

```bash
# QEMU image
nixos-generate -f qcow -c ./configuration.nix

# VirtualBox (VDI)
nixos-generate -f virtualbox -c ./configuration.nix

# VMware
nixos-generate -f vmware -c ./configuration.nix
```

### Generate Cloud Images

```bash
# AWS AMI
nixos-generate -f amazon -c ./configuration.nix

# Azure
nixos-generate -f azure -c ./configuration.nix

# Google Cloud
nixos-generate -f gce -c ./configuration.nix
```

## Flake-Based Image Generation

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    nixos-generators = {
      url = "github:nix-community/nixos-generators";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, nixos-generators, ... }: {
    # VM image
    packages.x86_64-linux.qcow = nixos-generators.nixosGenerate {
      system = "x86_64-linux";
      modules = [ ./configuration.nix ];
      format = "qcow";
    };

    # AWS AMI
    packages.x86_64-linux.amazon = nixos-generators.nixosGenerate {
      system = "x86_64-linux";
      modules = [ ./configuration.nix ];
      format = "amazon";
    };

    # Docker image
    packages.x86_64-linux.docker = nixos-generators.nixosGenerate {
      system = "x86_64-linux";
      modules = [ ./configuration.nix ];
      format = "docker";
    };
  };
}
```

Build:
```bash
nix build .#qcow
nix build .#amazon
nix build .#docker
```

## Docker Images with dockerTools

### Basic Image

```nix
{ pkgs }:

pkgs.dockerTools.buildImage {
  name = "my-app";
  tag = "latest";
  
  copyToRoot = pkgs.buildEnv {
    name = "image-root";
    paths = [ pkgs.hello pkgs.bash pkgs.coreutils ];
    pathsToLink = [ "/bin" ];
  };
  
  config = {
    Cmd = [ "/bin/hello" ];
    Env = [ "PATH=/bin" ];
  };
}
```

### Layered Image (Better for caching)

```nix
{ pkgs }:

pkgs.dockerTools.buildLayeredImage {
  name = "my-app";
  tag = "latest";
  
  contents = [
    pkgs.hello
    pkgs.bash
  ];
  
  config = {
    Cmd = [ "${pkgs.hello}/bin/hello" ];
    ExposedPorts = { "8080/tcp" = {}; };
    Env = [
      "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    ];
  };
}
```

### Minimal Image

```nix
{ pkgs }:

pkgs.dockerTools.buildImage {
  name = "minimal-app";
  tag = "latest";
  
  # Only include the binary
  copyToRoot = [ pkgs.hello ];
  
  config = {
    Entrypoint = [ "${pkgs.hello}/bin/hello" ];
  };
}
```

### Build and Load

```bash
# Build the image
nix build .#dockerImage

# Load into Docker
docker load < result

# Run
docker run my-app:latest
```

## ISO Generation

```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

  outputs = { self, nixpkgs, ... }: {
    nixosConfigurations.iso = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
        ({ pkgs, ... }: {
          # Custom ISO configuration
          environment.systemPackages = [ pkgs.vim pkgs.git ];
          
          # Auto-login
          services.getty.autologinUser = "nixos";
        })
      ];
    };
  };
}
```

Build ISO:
```bash
nix build .#nixosConfigurations.iso.config.system.build.isoImage
```

## Raspberry Pi / ARM Images

```nix
{
  outputs = { self, nixpkgs, ... }: {
    nixosConfigurations.rpi4 = nixpkgs.lib.nixosSystem {
      system = "aarch64-linux";
      modules = [
        "${nixpkgs}/nixos/modules/installer/sd-card/sd-image-aarch64.nix"
        ({ pkgs, ... }: {
          # Raspberry Pi 4 specific
          boot.kernelPackages = pkgs.linuxPackages_rpi4;
          hardware.raspberry-pi."4".fkms-3d.enable = true;
          
          # Your configuration
          networking.hostName = "rpi4";
          services.openssh.enable = true;
        })
      ];
    };
  };
}
```

Build SD image (requires aarch64 builder):
```bash
nix build .#nixosConfigurations.rpi4.config.system.build.sdImage
```

## nixos-anywhere (Remote Deployment)

```bash
# Install a machine remotely
nix run github:nix-community/nixos-anywhere -- \
  --flake .#myhost \
  root@192.168.1.100

# With disk formatting (disko)
nix run github:nix-community/nixos-anywhere -- \
  --flake .#myhost \
  --disk-encryption-keys /tmp/secret.key \
  root@192.168.1.100
```

Flake for nixos-anywhere:
```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    disko.url = "github:nix-community/disko";
  };

  outputs = { self, nixpkgs, disko, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        disko.nixosModules.disko
        ./configuration.nix
        ./disk-config.nix
      ];
    };
  };
}
```

