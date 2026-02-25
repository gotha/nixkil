# Managing Dotfiles with Home-Manager

## File Management Basics

### Direct File Content

```nix
{
  # Write content directly
  home.file.".vimrc".text = ''
    set number
    set relativenumber
    set expandtab
    set tabstop=2
    set shiftwidth=2
  '';

  # XDG-compliant location
  xdg.configFile."nvim/init.lua".text = ''
    vim.opt.number = true
    vim.opt.relativenumber = true
  '';
}
```

### Source from File

```nix
{
  # Copy file from Nix store
  home.file.".bashrc".source = ./dotfiles/bashrc;
  
  # Copy entire directory
  home.file.".config/alacritty" = {
    source = ./dotfiles/alacritty;
    recursive = true;
  };
  
  # Make executable
  home.file.".local/bin/myscript" = {
    source = ./scripts/myscript.sh;
    executable = true;
  };
}
```

### Using XDG Directories

```nix
{
  xdg.enable = true;
  
  # $XDG_CONFIG_HOME (~/.config)
  xdg.configFile = {
    "alacritty/alacritty.yml".source = ./alacritty.yml;
    "starship.toml".source = ./starship.toml;
  };
  
  # $XDG_DATA_HOME (~/.local/share)
  xdg.dataFile = {
    "fonts/MyFont.ttf".source = ./fonts/MyFont.ttf;
  };
}
```

## Modular Dotfile Organization

### Directory Structure

```
~/.config/home-manager/
├── flake.nix
├── home.nix
├── modules/
│   ├── shell/
│   │   ├── zsh.nix
│   │   ├── starship.nix
│   │   └── aliases.nix
│   ├── editors/
│   │   ├── neovim.nix
│   │   └── vscode.nix
│   ├── git.nix
│   ├── tmux.nix
│   └── tools.nix
└── dotfiles/
    ├── nvim/
    ├── alacritty/
    └── scripts/
```

### home.nix

```nix
{ config, pkgs, ... }:

{
  imports = [
    ./modules/shell/zsh.nix
    ./modules/shell/starship.nix
    ./modules/shell/aliases.nix
    ./modules/editors/neovim.nix
    ./modules/git.nix
    ./modules/tmux.nix
    ./modules/tools.nix
  ];

  home.stateVersion = "25.11";
  home.username = "myuser";
  home.homeDirectory = "/home/myuser";
  
  programs.home-manager.enable = true;
}
```

### modules/shell/aliases.nix

```nix
{ ... }:

{
  home.shellAliases = {
    # Navigation
    ".." = "cd ..";
    "..." = "cd ../..";
    
    # ls alternatives
    ll = "ls -la";
    la = "ls -a";
    
    # Git shortcuts
    g = "git";
    gs = "git status";
    gc = "git commit";
    gp = "git push";
    
    # Safety
    rm = "rm -i";
    cp = "cp -i";
    mv = "mv -i";
  };
}
```

## Migrating Existing Dotfiles

### Step 1: Identify Files

```bash
# Common dotfiles to migrate
ls -la ~/.*rc ~/.config/
```

### Step 2: Create Module Structure

```nix
# For .bashrc
{
  programs.bash = {
    enable = true;
    bashrcExtra = builtins.readFile ./dotfiles/bashrc;
  };
}

# Or import the whole file
{
  home.file.".bashrc".source = ./dotfiles/bashrc;
}
```

### Step 3: Use Program Modules When Possible

Instead of:
```nix
home.file.".gitconfig".text = ''
  [user]
  name = My Name
  email = me@example.com
'';
```

Use:
```nix
programs.git = {
  enable = true;
  userName = "My Name";
  userEmail = "me@example.com";
};
```

## Secrets in Dotfiles

### Using sops-nix

```nix
{
  inputs = {
    sops-nix.url = "github:Mic92/sops-nix";
  };
  
  outputs = { home-manager, sops-nix, ... }: {
    homeConfigurations."myuser" = home-manager.lib.homeManagerConfiguration {
      modules = [
        sops-nix.homeManagerModules.sops
        ./home.nix
      ];
    };
  };
}
```

```nix
# home.nix
{
  sops = {
    defaultSopsFile = ./secrets/secrets.yaml;
    age.keyFile = "/home/myuser/.config/sops/age/keys.txt";
    
    secrets.github_token = {};
  };
  
  # Use in config
  programs.git.extraConfig = {
    credential.helper = "!f() { echo password=$(cat ${config.sops.secrets.github_token.path}); }; f";
  };
}
```

### Using agenix

```nix
{
  age.secrets.my-secret = {
    file = ./secrets/my-secret.age;
  };
  
  home.file.".config/myapp/secret" = {
    source = config.age.secrets.my-secret.path;
  };
}
```

## Multi-Machine Configurations

```nix
# flake.nix
{
  outputs = { nixpkgs, home-manager, ... }:
    let
      commonModules = [
        ./modules/shell
        ./modules/git.nix
        ./modules/tools.nix
      ];
    in {
      homeConfigurations = {
        "user@laptop" = home-manager.lib.homeManagerConfiguration {
          pkgs = nixpkgs.legacyPackages.x86_64-linux;
          modules = commonModules ++ [
            ./hosts/laptop.nix
            { home.username = "user"; home.homeDirectory = "/home/user"; }
          ];
        };
        
        "user@desktop" = home-manager.lib.homeManagerConfiguration {
          pkgs = nixpkgs.legacyPackages.x86_64-linux;
          modules = commonModules ++ [
            ./hosts/desktop.nix
            ./modules/gaming.nix  # Desktop-specific
            { home.username = "user"; home.homeDirectory = "/home/user"; }
          ];
        };
        
        "user@macbook" = home-manager.lib.homeManagerConfiguration {
          pkgs = nixpkgs.legacyPackages.aarch64-darwin;
          modules = commonModules ++ [
            ./hosts/macbook.nix
            { home.username = "user"; home.homeDirectory = "/Users/user"; }
          ];
        };
      };
    };
}
```

