# nix-darwin: macOS Configuration with Nix

## What is nix-darwin?

nix-darwin brings NixOS-style declarative system configuration to macOS. It allows you to:
- Manage system settings (defaults, keyboard, etc.)
- Install system-wide packages
- Configure services (launchd)
- Manage Homebrew declaratively
- Integrate with home-manager

## Installation

### With Flakes (Recommended)

```bash
# Install Nix first (if not already)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh

# Create initial configuration
mkdir -p ~/.config/nix-darwin
cd ~/.config/nix-darwin
```

Create `flake.nix`:
```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    darwin = {
      url = "github:LnL7/nix-darwin";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, darwin, ... }: {
    darwinConfigurations."mymac" = darwin.lib.darwinSystem {
      system = "aarch64-darwin";  # or "x86_64-darwin"
      modules = [ ./configuration.nix ];
    };
  };
}
```

Create `configuration.nix`:
```nix
{ pkgs, ... }:

{
  # System packages
  environment.systemPackages = with pkgs; [
    vim
    git
  ];

  # Enable nix-daemon
  services.nix-daemon.enable = true;

  # Nix settings
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  # System version
  system.stateVersion = 4;
}
```

First build:
```bash
nix run nix-darwin -- switch --flake .#mymac
```

After initial install:
```bash
darwin-rebuild switch --flake .#mymac
```

## Basic Configuration

### System Packages

```nix
{
  environment.systemPackages = with pkgs; [
    vim
    git
    htop
    ripgrep
    fd
  ];
}
```

### Shells

```nix
{
  # Enable zsh
  programs.zsh.enable = true;
  
  # Set default shell
  users.users.myuser.shell = pkgs.zsh;
  
  # Or use fish
  programs.fish.enable = true;
}
```

### macOS System Defaults

```nix
{
  system.defaults = {
    # Dock
    dock = {
      autohide = true;
      orientation = "bottom";
      show-recents = false;
      tilesize = 48;
      # Hot corners
      wvous-bl-corner = 1;  # Disabled
      wvous-br-corner = 1;  # Disabled
    };
    
    # Finder
    finder = {
      AppleShowAllExtensions = true;
      AppleShowAllFiles = true;
      ShowPathbar = true;
      ShowStatusBar = true;
      FXPreferredViewStyle = "Nlsv";  # List view
      FXDefaultSearchScope = "SCcf";  # Current folder
    };
    
    # Global settings
    NSGlobalDomain = {
      AppleShowAllExtensions = true;
      AppleShowAllFiles = true;
      InitialKeyRepeat = 15;
      KeyRepeat = 2;
      NSAutomaticCapitalizationEnabled = false;
      NSAutomaticSpellingCorrectionEnabled = false;
      "com.apple.swipescrolldirection" = true;  # Natural scrolling
    };
    
    # Trackpad
    trackpad = {
      Clicking = true;  # Tap to click
      TrackpadRightClick = true;
      TrackpadThreeFingerDrag = true;
    };
    
    # Login window
    loginwindow = {
      GuestEnabled = false;
    };
  };
}
```

### Keyboard Settings

```nix
{
  system.keyboard = {
    enableKeyMapping = true;
    remapCapsLockToControl = true;
    # Or remap to escape
    # remapCapsLockToEscape = true;
  };
}
```

### Security

```nix
{
  security.pam.enableSudoTouchIdAuth = true;  # Touch ID for sudo
}
```

## Homebrew Integration

```nix
{
  homebrew = {
    enable = true;
    
    onActivation = {
      autoUpdate = true;
      cleanup = "zap";  # Remove unlisted packages
      upgrade = true;
    };
    
    # Homebrew taps
    taps = [
      "homebrew/cask-fonts"
    ];
    
    # Homebrew formulae
    brews = [
      "mas"  # Mac App Store CLI
    ];
    
    # Homebrew casks (GUI apps)
    casks = [
      "1password"
      "firefox"
      "visual-studio-code"
      "slack"
      "docker"
    ];
    
    # Mac App Store apps (requires `mas`)
    masApps = {
      "Xcode" = 497799835;
      "Keynote" = 409183694;
    };
  };
}
```

## Services (launchd)

```nix
{
  # Built-in services
  services.yabai.enable = true;  # Tiling window manager
  services.skhd.enable = true;   # Hotkey daemon
  
  # Custom launchd service
  launchd.user.agents.myservice = {
    command = "/path/to/myservice";
    serviceConfig = {
      KeepAlive = true;
      RunAtLoad = true;
      StandardOutPath = "/tmp/myservice.log";
      StandardErrorPath = "/tmp/myservice.err";
    };
  };
}
```

## Applying Changes

```bash
# Rebuild and switch
darwin-rebuild switch --flake .#mymac

# Test without switching
darwin-rebuild check --flake .#mymac

# Show changes before applying
darwin-rebuild build --flake .#mymac
nvd diff /run/current-system result
```

