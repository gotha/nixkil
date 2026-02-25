# devenv.nix Configuration Guide

## Basic Structure

```nix
{ pkgs, lib, config, inputs, ... }:

{
  # Available configuration options
}
```

## Packages

```nix
{
  # Add packages to the environment
  packages = with pkgs; [
    git
    curl
    jq
    ripgrep
  ];
}
```

## Languages

devenv has built-in support for many languages:

### Python

```nix
{
  languages.python = {
    enable = true;
    version = "3.11";
    
    # Use poetry for dependency management
    poetry = {
      enable = true;
      activate.enable = true;
    };
    
    # Or use pip with venv
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };
}
```

### Node.js

```nix
{
  languages.javascript = {
    enable = true;
    package = pkgs.nodejs_20;
    
    # Package managers
    npm.enable = true;
    yarn.enable = true;
    pnpm.enable = true;
    
    # Install dependencies on shell entry
    npm.install.enable = true;
  };
  
  languages.typescript.enable = true;
}
```

### Go

```nix
{
  languages.go = {
    enable = true;
    package = pkgs.go_1_22;
  };
}
```

### Rust

```nix
{
  languages.rust = {
    enable = true;
    channel = "stable";  # or "nightly", "beta"
    
    # Components
    components = [ "rustc" "cargo" "clippy" "rustfmt" "rust-analyzer" ];
  };
}
```

### Java

```nix
{
  languages.java = {
    enable = true;
    jdk.package = pkgs.jdk17;
    
    maven.enable = true;
    gradle.enable = true;
  };
}
```

## Environment Variables

```nix
{
  # Simple variables
  env.MY_VAR = "value";
  env.DATABASE_URL = "postgres://localhost/mydb";
  
  # From other config
  env.PROJECT_ROOT = config.devenv.root;
  
  # Conditional
  env.DEBUG = lib.mkIf config.devenv.debug "1";
}
```

## Shell Hooks

```nix
{
  # Run when entering shell
  enterShell = ''
    echo "Welcome to $(basename $PWD)!"
    echo "Node version: $(node --version)"
  '';
  
  # Run specific commands
  scripts.hello.exec = ''
    echo "Hello from devenv!"
  '';
  
  scripts.build.exec = ''
    npm run build
  '';
  
  # Now you can run: devenv shell -- hello
}
```

## Services

```nix
{
  services.postgres = {
    enable = true;
    package = pkgs.postgresql_15;
    initialDatabases = [{ name = "mydb"; }];
    initialScript = ''
      CREATE USER myuser WITH PASSWORD 'mypass';
      GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
    '';
    listen_addresses = "127.0.0.1";
    port = 5432;
  };
  
  services.redis = {
    enable = true;
    port = 6379;
  };
  
  services.mysql = {
    enable = true;
    initialDatabases = [{ name = "mydb"; }];
  };
  
  services.elasticsearch.enable = true;
  services.minio.enable = true;
  services.mailhog.enable = true;
  services.rabbitmq.enable = true;
}
```

Start services:
```bash
devenv up
```

## Pre-commit Hooks

```nix
{
  pre-commit.hooks = {
    # Nix
    nixfmt.enable = true;
    statix.enable = true;
    
    # General
    prettier.enable = true;
    
    # Python
    black.enable = true;
    ruff.enable = true;
    mypy.enable = true;
    
    # JavaScript
    eslint.enable = true;
    
    # Rust
    rustfmt.enable = true;
    clippy.enable = true;
    
    # Go
    gofmt.enable = true;
    golangci-lint.enable = true;
    
    # Custom hook
    my-hook = {
      enable = true;
      name = "my-custom-hook";
      entry = "${pkgs.bash}/bin/bash -c 'echo checking...'";
      files = "\\.nix$";
      pass_filenames = false;
    };
  };
}
```

## Processes

```nix
{
  processes = {
    # Run a web server
    web.exec = "npm run dev";
    
    # Run a worker
    worker.exec = "python worker.py";
    
    # With specific working directory
    api = {
      exec = "go run ./cmd/api";
      process-compose = {
        working_dir = "./api";
        depends_on.postgres.condition = "process_healthy";
      };
    };
  };
}
```

Start all processes:
```bash
devenv up
```

## Containers

```nix
{
  containers.myapp = {
    name = "myapp";
    startupCommand = config.processes.web.exec;
    copyToRoot = [ pkgs.nodejs ];
  };
}
```

Build container:
```bash
devenv container myapp
```

