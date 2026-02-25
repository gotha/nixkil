# Combining nix-darwin with home-manager

## Overview

nix-darwin manages system-level configuration, while home-manager manages user-level configuration. They work well together.

## Flake Setup

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    darwin = {
      url = "github:LnL7/nix-darwin";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    home-manager = {
      url = "github:nix-community/home-manager/release-24.11";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, darwin, home-manager, ... }:
    let
      system = "aarch64-darwin";  # or "x86_64-darwin"
    in {
      darwinConfigurations."mymac" = darwin.lib.darwinSystem {
        inherit system;
        modules = [
          ./darwin-configuration.nix
          
          # home-manager module
          home-manager.darwinModules.home-manager
          {
            home-manager.useGlobalPkgs = true;
            home-manager.useUserPackages = true;
            home-manager.users.myuser = import ./home.nix;
          }
        ];
      };
    };
}
```

## darwin-configuration.nix (System Level)

```nix
{ pkgs, ... }:

{
  # System packages (available to all users)
  environment.systemPackages = with pkgs; [
    vim
    git
  ];

  # System settings
  system.defaults.dock.autohide = true;

  # Homebrew (system-level)
  homebrew = {
    enable = true;
    casks = [ "firefox" "docker" ];
  };

  # Enable services
  services.nix-daemon.enable = true;

  # Users
  users.users.myuser = {
    name = "myuser";
    home = "/Users/myuser";
  };

  # Nix settings
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  system.stateVersion = 4;
}
```

## home.nix (User Level)

```nix
{ pkgs, ... }:

{
  home.stateVersion = "25.11";
  
  # User packages
  home.packages = with pkgs; [
    ripgrep
    fd
    jq
    htop
  ];

  # Dotfiles
  programs.git = {
    enable = true;
    userName = "My Name";
    userEmail = "me@example.com";
  };

  programs.zsh = {
    enable = true;
    oh-my-zsh = {
      enable = true;
      theme = "robbyrussell";
      plugins = [ "git" "docker" ];
    };
  };

  programs.starship.enable = true;
  
  programs.neovim = {
    enable = true;
    defaultEditor = true;
  };
}
```

## What Goes Where?

| Configuration | nix-darwin | home-manager |
|--------------|------------|--------------|
| System packages | ✓ | |
| User packages | | ✓ |
| macOS defaults | ✓ | |
| Dock settings | ✓ | |
| Homebrew casks | ✓ | |
| Shell config | | ✓ |
| Git config | | ✓ |
| Neovim config | | ✓ |
| Dotfiles | | ✓ |
| launchd services | ✓ | |
| User launchd agents | | ✓ |

## Applying Changes

```bash
# Rebuild both darwin and home-manager
darwin-rebuild switch --flake .#mymac
```

## Modular Configuration

```
~/.config/nix-darwin/
├── flake.nix
├── flake.lock
├── darwin-configuration.nix
├── home.nix
├── darwin/
│   ├── defaults.nix      # macOS defaults
│   ├── homebrew.nix      # Homebrew config
│   └── services.nix      # System services
└── home/
    ├── shell.nix         # zsh/fish config
    ├── git.nix           # Git config
    ├── neovim.nix        # Neovim config
    └── tools.nix         # CLI tools
```

### darwin-configuration.nix

```nix
{ pkgs, ... }:

{
  imports = [
    ./darwin/defaults.nix
    ./darwin/homebrew.nix
    ./darwin/services.nix
  ];

  # Core darwin config
  services.nix-daemon.enable = true;
  system.stateVersion = 4;
}
```

### home.nix

```nix
{ pkgs, ... }:

{
  imports = [
    ./home/shell.nix
    ./home/git.nix
    ./home/neovim.nix
    ./home/tools.nix
  ];

  home.stateVersion = "25.11";
}
```

## Multiple Machines

```nix
{
  outputs = { self, nixpkgs, darwin, home-manager, ... }:
    let
      mkDarwinConfig = { system, hostname, user }: darwin.lib.darwinSystem {
        inherit system;
        modules = [
          ./darwin-configuration.nix
          ./hosts/${hostname}.nix  # Host-specific config
          home-manager.darwinModules.home-manager
          {
            home-manager.useGlobalPkgs = true;
            home-manager.useUserPackages = true;
            home-manager.users.${user} = import ./home.nix;
          }
        ];
      };
    in {
      darwinConfigurations = {
        "macbook-pro" = mkDarwinConfig {
          system = "aarch64-darwin";
          hostname = "macbook-pro";
          user = "myuser";
        };
        
        "mac-mini" = mkDarwinConfig {
          system = "aarch64-darwin";
          hostname = "mac-mini";
          user = "myuser";
        };
      };
    };
}
```

