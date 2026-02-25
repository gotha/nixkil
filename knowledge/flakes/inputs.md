# Flake Inputs Reference

## Input URL Syntax

```nix
inputs = {
  # GitHub repository (most common)
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  
  # GitLab
  myrepo.url = "gitlab:owner/repo/branch";
  
  # Sourcehut
  myrepo.url = "sourcehut:~owner/repo";
  
  # Git URL (any git host)
  myrepo.url = "git+https://example.com/repo.git?ref=main";
  myrepo.url = "git+ssh://git@example.com/repo.git";
  
  # Local path (for development)
  myrepo.url = "path:/absolute/path/to/repo";
  myrepo.url = "path:./relative/path";
  
  # Tarball URL
  myrepo.url = "https://example.com/repo.tar.gz";
  
  # Specific commit
  nixpkgs.url = "github:NixOS/nixpkgs/abc123def456";
};
```

## Common Inputs

### nixpkgs (Package Collection)

```nix
inputs = {
  # Stable releases (recommended for production)
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  
  # Unstable (latest packages, less tested)
  nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  
  # NixOS unstable (includes NixOS modules)
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
};
```

### flake-utils (Multi-System Helper)

```nix
inputs = {
  flake-utils.url = "github:numtide/flake-utils";
};

outputs = { self, nixpkgs, flake-utils }:
  flake-utils.lib.eachDefaultSystem (system:
    let pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.default = pkgs.hello;
    }
  );
```

### home-manager (User Configuration)

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  home-manager = {
    url = "github:nix-community/home-manager/release-24.11";
    inputs.nixpkgs.follows = "nixpkgs";  # Use same nixpkgs
  };
};
```

### nix-darwin (macOS Configuration)

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  darwin = {
    url = "github:LnL7/nix-darwin";
    inputs.nixpkgs.follows = "nixpkgs";
  };
};
```

### devenv (Development Environments)

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  devenv.url = "github:cachix/devenv";
};
```

### flake-parts (Modular Flakes)

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  flake-parts.url = "github:hercules-ci/flake-parts";
};

outputs = inputs@{ flake-parts, ... }:
  flake-parts.lib.mkFlake { inherit inputs; } {
    systems = [ "x86_64-linux" "aarch64-darwin" ];
    perSystem = { pkgs, ... }: {
      packages.default = pkgs.hello;
    };
  };
```

## Input Options

```nix
inputs = {
  # Basic URL
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  
  # Follow another input's nixpkgs (avoid duplicate nixpkgs)
  home-manager = {
    url = "github:nix-community/home-manager";
    inputs.nixpkgs.follows = "nixpkgs";
  };
  
  # Non-flake input (legacy Nix code)
  vim-plugin = {
    url = "github:owner/vim-plugin";
    flake = false;  # Don't treat as flake
  };
  
  # Multiple follows
  my-flake = {
    url = "github:owner/repo";
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.flake-utils.follows = "flake-utils";
  };
};
```

## Accessing Inputs in Outputs

```nix
outputs = { self, nixpkgs, home-manager, ... }@inputs: {
  # Access specific input
  packages.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.hello;
  
  # Pass all inputs to modules
  nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
    modules = [
      home-manager.nixosModules.home-manager
      {
        # Access inputs in module
        _module.args.inputs = inputs;
      }
    ];
  };
};
```

## Using Non-Flake Inputs

```nix
inputs = {
  # Vim plugin (not a flake)
  vim-surround = {
    url = "github:tpope/vim-surround";
    flake = false;
  };
};

outputs = { self, nixpkgs, vim-surround, ... }:
  let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  in {
    packages.x86_64-linux.myVim = pkgs.vim_configurable.customize {
      vimrcConfig.packages.myPlugins = {
        start = [
          (pkgs.vimUtils.buildVimPlugin {
            name = "vim-surround";
            src = vim-surround;  # Use input directly as source
          })
        ];
      };
    };
  };
```

## Version Pinning Strategy

```nix
inputs = {
  # Pin to stable branch (auto-updates within branch)
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  
  # Pin to exact commit (never changes)
  nixpkgs.url = "github:NixOS/nixpkgs/abc123def456";
  
  # Pin to tag
  nixpkgs.url = "github:NixOS/nixpkgs?ref=refs/tags/24.11";
};

# Update strategy:
# - nix flake update           # Update all inputs
# - nix flake lock --update-input nixpkgs  # Update specific input
```

