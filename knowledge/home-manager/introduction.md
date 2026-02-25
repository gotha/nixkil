# Home-Manager Introduction

## What is home-manager?

Home-manager is a Nix-based tool for managing user environments and dotfiles. It allows you to:
- Install user-specific packages
- Manage configuration files (dotfiles)
- Configure programs declaratively
- Share configurations across machines

## Installation Methods

### 1. Standalone (Recommended for Non-NixOS)

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    home-manager = {
      url = "github:nix-community/home-manager/release-24.11";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, ... }:
    let
      system = "x86_64-linux";  # or aarch64-darwin, etc.
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      homeConfigurations."myuser" = home-manager.lib.homeManagerConfiguration {
        inherit pkgs;
        modules = [ ./home.nix ];
      };
    };
}
```

Apply:
```bash
home-manager switch --flake .#myuser
```

### 2. As NixOS Module

```nix
# configuration.nix or flake
{
  imports = [ home-manager.nixosModules.home-manager ];
  
  home-manager.useGlobalPkgs = true;
  home-manager.useUserPackages = true;
  home-manager.users.myuser = import ./home.nix;
}
```

### 3. As nix-darwin Module

```nix
{
  imports = [ home-manager.darwinModules.home-manager ];
  
  home-manager.useGlobalPkgs = true;
  home-manager.useUserPackages = true;
  home-manager.users.myuser = import ./home.nix;
}
```

## Basic home.nix

```nix
{ config, pkgs, ... }:

{
  # Home Manager version
  home.stateVersion = "25.11";

  # Let Home Manager manage itself
  programs.home-manager.enable = true;

  # User info
  home.username = "myuser";
  home.homeDirectory = "/home/myuser";  # or /Users/myuser on macOS

  # Packages
  home.packages = with pkgs; [
    ripgrep
    fd
    jq
    htop
    tree
  ];

  # Environment variables
  home.sessionVariables = {
    EDITOR = "nvim";
    PAGER = "less";
  };

  # Shell aliases
  home.shellAliases = {
    ll = "ls -la";
    ".." = "cd ..";
    g = "git";
  };
}
```

## Program Modules

### Git

```nix
{
  programs.git = {
    enable = true;
    userName = "My Name";
    userEmail = "me@example.com";
    
    extraConfig = {
      init.defaultBranch = "main";
      pull.rebase = true;
      push.autoSetupRemote = true;
    };
    
    aliases = {
      st = "status";
      co = "checkout";
      br = "branch";
    };
    
    delta.enable = true;  # Better diffs
  };
}
```

### Zsh

```nix
{
  programs.zsh = {
    enable = true;
    
    enableCompletion = true;
    autosuggestion.enable = true;
    syntaxHighlighting.enable = true;
    
    history = {
      size = 10000;
      save = 10000;
      ignoreDups = true;
      ignoreSpace = true;
    };
    
    oh-my-zsh = {
      enable = true;
      theme = "robbyrussell";
      plugins = [ "git" "docker" "kubectl" ];
    };
    
    initExtra = ''
      # Custom zsh config
      bindkey -e  # Emacs keybindings
    '';
  };
}
```

### Neovim

```nix
{
  programs.neovim = {
    enable = true;
    defaultEditor = true;
    viAlias = true;
    vimAlias = true;
    
    plugins = with pkgs.vimPlugins; [
      vim-nix
      telescope-nvim
      nvim-treesitter.withAllGrammars
      lualine-nvim
    ];
    
    extraLuaConfig = ''
      vim.opt.number = true
      vim.opt.relativenumber = true
      vim.opt.expandtab = true
      vim.opt.tabstop = 2
      vim.opt.shiftwidth = 2
    '';
  };
}
```

### Starship Prompt

```nix
{
  programs.starship = {
    enable = true;
    
    settings = {
      add_newline = false;
      
      character = {
        success_symbol = "[➜](bold green)";
        error_symbol = "[✗](bold red)";
      };
      
      directory = {
        truncation_length = 3;
        truncate_to_repo = true;
      };
      
      git_branch.symbol = " ";
      
      nix_shell = {
        symbol = " ";
        format = "[$symbol$state]($style) ";
      };
    };
  };
}
```

### Tmux

```nix
{
  programs.tmux = {
    enable = true;
    
    terminal = "screen-256color";
    baseIndex = 1;
    escapeTime = 0;
    historyLimit = 10000;
    mouse = true;
    
    prefix = "C-a";  # Change prefix to Ctrl+a
    
    extraConfig = ''
      # Split panes with | and -
      bind | split-window -h
      bind - split-window -v
    '';
    
    plugins = with pkgs.tmuxPlugins; [
      sensible
      yank
      resurrect
    ];
  };
}
```

## File Management

```nix
{
  # Raw file content
  home.file.".config/myapp/config.toml".text = ''
    [settings]
    theme = "dark"
  '';
  
  # Copy from source
  home.file.".config/myapp/other.conf".source = ./files/other.conf;
  
  # Symlink
  home.file.".local/bin/myscript" = {
    source = ./scripts/myscript.sh;
    executable = true;
  };
  
  # XDG config
  xdg.configFile."myapp/config.yaml".text = ''
    key: value
  '';
}
```

