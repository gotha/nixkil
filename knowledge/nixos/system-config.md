# NixOS System Configuration

## Basic System Configuration

```nix
# /etc/nixos/configuration.nix
{ config, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
  ];

  # Boot
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Hostname
  networking.hostName = "myhost";

  # Timezone
  time.timeZone = "America/New_York";

  # Locale
  i18n.defaultLocale = "en_US.UTF-8";

  # System packages
  environment.systemPackages = with pkgs; [
    vim
    git
    htop
    curl
  ];

  system.stateVersion = "25.11";
}
```

## Users and Groups

```nix
{
  # Define users
  users.users.alice = {
    isNormalUser = true;
    description = "Alice";
    extraGroups = [ "wheel" "networkmanager" "docker" ];
    
    # Set initial password (or use initialHashedPassword)
    initialPassword = "changeme";
    
    # SSH keys
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAA... alice@laptop"
    ];
    
    # User's shell
    shell = pkgs.zsh;
    
    # User packages
    packages = with pkgs; [
      firefox
      vscode
    ];
  };
  
  # System user (for services)
  users.users.myservice = {
    isSystemUser = true;
    group = "myservice";
    home = "/var/lib/myservice";
    createHome = true;
  };
  users.groups.myservice = {};
  
  # Allow wheel group to sudo
  security.sudo.wheelNeedsPassword = false;  # or true
}
```

## Networking

```nix
{
  networking = {
    hostName = "myhost";
    
    # Enable NetworkManager (for desktops)
    networkmanager.enable = true;
    
    # Or static configuration
    interfaces.eth0 = {
      useDHCP = false;
      ipv4.addresses = [{
        address = "192.168.1.100";
        prefixLength = 24;
      }];
    };
    defaultGateway = "192.168.1.1";
    nameservers = [ "8.8.8.8" "8.8.4.4" ];
    
    # Firewall
    firewall = {
      enable = true;
      allowedTCPPorts = [ 22 80 443 ];
    };
    
    # Hosts file entries
    hosts = {
      "127.0.0.1" = [ "myapp.local" ];
    };
  };
}
```

## Filesystems

```nix
{
  fileSystems."/" = {
    device = "/dev/disk/by-uuid/xxx";
    fsType = "ext4";
  };
  
  fileSystems."/boot" = {
    device = "/dev/disk/by-uuid/yyy";
    fsType = "vfat";
  };
  
  fileSystems."/data" = {
    device = "/dev/sdb1";
    fsType = "ext4";
    options = [ "noatime" ];
  };
  
  # NFS mount
  fileSystems."/mnt/nfs" = {
    device = "server:/export";
    fsType = "nfs";
    options = [ "x-systemd.automount" "noauto" ];
  };
  
  # Swap
  swapDevices = [
    { device = "/dev/disk/by-uuid/zzz"; }
  ];
}
```

## Desktop Environment

```nix
{
  # X11 with GNOME
  services.xserver = {
    enable = true;
    displayManager.gdm.enable = true;
    desktopManager.gnome.enable = true;
  };
  
  # Or KDE Plasma
  services.xserver = {
    enable = true;
    displayManager.sddm.enable = true;
    desktopManager.plasma5.enable = true;
  };
  
  # Or just a window manager
  services.xserver = {
    enable = true;
    displayManager.lightdm.enable = true;
    windowManager.i3.enable = true;
  };
  
  # Sound
  sound.enable = true;
  hardware.pulseaudio.enable = true;
  # Or PipeWire
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    pulse.enable = true;
  };
  
  # Fonts
  fonts.packages = with pkgs; [
    noto-fonts
    noto-fonts-cjk
    fira-code
    (nerdfonts.override { fonts = [ "FiraCode" ]; })
  ];
}
```

## Virtualization

```nix
{
  # Docker
  virtualisation.docker.enable = true;
  
  # Podman (Docker alternative)
  virtualisation.podman = {
    enable = true;
    dockerCompat = true;  # docker CLI compatibility
  };
  
  # libvirt/KVM
  virtualisation.libvirtd.enable = true;
  programs.virt-manager.enable = true;
}
```

## Programs and Shells

```nix
{
  # Enable programs (with configuration)
  programs.zsh.enable = true;
  programs.git.enable = true;
  
  programs.neovim = {
    enable = true;
    defaultEditor = true;
    viAlias = true;
    vimAlias = true;
  };
  
  programs.gnupg.agent = {
    enable = true;
    enableSSHSupport = true;
  };
  
  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;
}
```

## Secrets Management

```nix
{
  # Using agenix
  age.secrets.my-secret = {
    file = ./secrets/my-secret.age;
    owner = "myservice";
  };
  
  # Reference in services
  systemd.services.myapp.serviceConfig = {
    EnvironmentFile = config.age.secrets.my-secret.path;
  };
}
```

## Applying Configuration

```bash
# Test configuration (build without switching)
sudo nixos-rebuild test

# Switch to new configuration
sudo nixos-rebuild switch

# Build and add to bootloader
sudo nixos-rebuild boot

# Upgrade system
sudo nixos-rebuild switch --upgrade
```

