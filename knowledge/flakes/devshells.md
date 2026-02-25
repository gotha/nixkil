# DevShell Patterns

## Basic DevShell

```nix
{
  outputs = { nixpkgs, ... }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = [
          pkgs.nodejs
          pkgs.yarn
          pkgs.git
        ];
      };
    };
}
```

## DevShell with Environment Variables

```nix
devShells.default = pkgs.mkShell {
  packages = [ pkgs.postgresql ];
  
  # Environment variables
  DATABASE_URL = "postgres://localhost/mydb";
  NODE_ENV = "development";
  
  # Or use env attribute
  env = {
    MY_VAR = "value";
    RUST_BACKTRACE = "1";
  };
  
  shellHook = ''
    echo "Development environment loaded"
    export PATH="$PWD/node_modules/.bin:$PATH"
  '';
};
```

## DevShell from Package Inputs

```nix
let
  myPackage = pkgs.callPackage ./package.nix { };
in {
  devShells.default = pkgs.mkShell {
    # Include all build inputs from the package
    inputsFrom = [ myPackage ];
    
    # Add development-only tools
    packages = [
      pkgs.nixfmt-rfc-style
      pkgs.nil  # Nix LSP
    ];
  };
}
```

## Multiple DevShells

```nix
devShells = {
  default = pkgs.mkShell {
    packages = [ pkgs.nodejs pkgs.yarn ];
  };
  
  ci = pkgs.mkShell {
    packages = [ pkgs.nodejs pkgs.yarn pkgs.playwright ];
  };
  
  docs = pkgs.mkShell {
    packages = [ pkgs.mdbook pkgs.vale ];
  };
};

# Usage:
# nix develop        # default shell
# nix develop .#ci   # CI shell
# nix develop .#docs # docs shell
```

## Language-Specific Patterns

### Node.js

```nix
devShells.default = pkgs.mkShell {
  packages = [
    pkgs.nodejs_20
    pkgs.yarn
    pkgs.nodePackages.typescript
    pkgs.nodePackages.typescript-language-server
  ];
  
  shellHook = ''
    export PATH="$PWD/node_modules/.bin:$PATH"
  '';
};
```

### Python

```nix
devShells.default = pkgs.mkShell {
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
    pkgs.pyright  # LSP
    pkgs.ruff     # Linter
  ];
  
  shellHook = ''
    if [ ! -d .venv ]; then
      python -m venv .venv
    fi
    source .venv/bin/activate
  '';
};
```

### Go

```nix
devShells.default = pkgs.mkShell {
  packages = [
    pkgs.go_1_22
    pkgs.gopls
    pkgs.golangci-lint
    pkgs.delve  # Debugger
  ];
  
  env = {
    GOPATH = "$HOME/go";
    CGO_ENABLED = "0";
  };
};
```

### Rust

```nix
devShells.default = pkgs.mkShell {
  packages = [
    pkgs.rustc
    pkgs.cargo
    pkgs.rust-analyzer
    pkgs.clippy
    pkgs.rustfmt
  ];
  
  # For native dependencies
  nativeBuildInputs = [ pkgs.pkg-config ];
  buildInputs = [ pkgs.openssl ];
  
  env = {
    RUST_BACKTRACE = "1";
  };
};
```

## Cross-Platform DevShell

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.nodejs
          ] ++ pkgs.lib.optionals pkgs.stdenv.isDarwin [
            # macOS-specific packages
            pkgs.darwin.apple_sdk.frameworks.Security
          ] ++ pkgs.lib.optionals pkgs.stdenv.isLinux [
            # Linux-specific packages
            pkgs.inotify-tools
          ];
        };
      }
    );
}
```

## DevShell with Services (Simple)

```nix
devShells.default = pkgs.mkShell {
  packages = [
    pkgs.postgresql
    pkgs.redis
  ];
  
  shellHook = ''
    export PGDATA=$PWD/.postgres
    export REDIS_DIR=$PWD/.redis
    
    if [ ! -d "$PGDATA" ]; then
      initdb -D "$PGDATA"
    fi
    
    # Start services in background
    pg_ctl -D "$PGDATA" -l "$PGDATA/log" start
    redis-server --daemonize yes --dir "$REDIS_DIR"
    
    # Cleanup on exit
    trap "pg_ctl -D $PGDATA stop; redis-cli shutdown" EXIT
  '';
};
```

> **Note**: For complex service setups, consider using `devenv` instead.

## direnv Integration

Create `.envrc` in your project:
```bash
use flake
```

Then:
```bash
direnv allow
# Shell activates automatically when entering directory
```

## Best Practices

1. **Pin nixpkgs** to a stable branch for reproducibility
2. **Include LSP tools** for IDE support
3. **Use inputsFrom** to inherit package dependencies
4. **Add shellHook** for environment setup messages
5. **Consider devenv** for services (databases, etc.)
6. **Use direnv** for automatic shell activation

