# NixOS Module System

## What is a NixOS Module?

A NixOS module is a file that declares configuration options and implements them. The module system allows:
- Defining configuration options with types and defaults
- Implementing behavior based on option values
- Composing multiple modules together
- Overriding and merging configurations

## Basic Module Structure

```nix
{ config, lib, pkgs, ... }:

{
  # Declare options this module provides
  options = {
    # Option declarations
  };

  # Implement behavior based on options
  config = {
    # Configuration based on options
  };
}
```

## Module Arguments

```nix
{ config, lib, pkgs, options, modulesPath, ... }:

# config    - The final merged configuration
# lib       - Nixpkgs library functions
# pkgs      - The package set
# options   - All declared options
# modulesPath - Path to NixOS modules directory
```

## Declaring Options

```nix
{ config, lib, pkgs, ... }:

{
  options.services.myservice = {
    enable = lib.mkEnableOption "my service";
    
    port = lib.mkOption {
      type = lib.types.port;
      default = 8080;
      description = "Port to listen on";
    };
    
    user = lib.mkOption {
      type = lib.types.str;
      default = "myservice";
      description = "User to run the service as";
    };
    
    dataDir = lib.mkOption {
      type = lib.types.path;
      default = "/var/lib/myservice";
      description = "Data directory";
    };
    
    settings = lib.mkOption {
      type = lib.types.attrsOf lib.types.str;
      default = {};
      description = "Additional settings";
    };
    
    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.myservice;
      description = "Package to use";
    };
  };
}
```

## Common Option Types

```nix
lib.types.bool                    # true/false
lib.types.int                     # Integer
lib.types.str                     # String
lib.types.path                    # Path
lib.types.port                    # 1-65535
lib.types.package                 # Nix package

lib.types.listOf lib.types.str    # List of strings
lib.types.attrsOf lib.types.int   # Attrset with int values
lib.types.nullOr lib.types.str    # String or null

lib.types.enum [ "a" "b" "c" ]    # One of specific values
lib.types.oneOf [ types.str types.int ]  # Multiple types

lib.types.submodule {             # Nested module
  options = { /* ... */ };
}
```

## Implementing Configuration

```nix
{ config, lib, pkgs, ... }:

let
  cfg = config.services.myservice;
in {
  options.services.myservice = { /* ... */ };

  config = lib.mkIf cfg.enable {
    # Create user
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.user;
      home = cfg.dataDir;
    };
    users.groups.${cfg.user} = {};

    # Create systemd service
    systemd.services.myservice = {
      description = "My Service";
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      
      serviceConfig = {
        User = cfg.user;
        ExecStart = "${cfg.package}/bin/myservice --port ${toString cfg.port}";
        Restart = "always";
        StateDirectory = "myservice";
      };
    };

    # Open firewall port
    networking.firewall.allowedTCPPorts = [ cfg.port ];
  };
}
```

## Using lib.mkIf and lib.mkMerge

```nix
config = lib.mkMerge [
  # Always applied
  {
    environment.systemPackages = [ pkgs.htop ];
  }
  
  # Conditionally applied
  (lib.mkIf cfg.enable {
    systemd.services.myservice = { /* ... */ };
  })
  
  # Another condition
  (lib.mkIf cfg.enableMetrics {
    services.prometheus.scrapeConfigs = [ /* ... */ ];
  })
];
```

## Priority with mkDefault, mkForce, mkOverride

```nix
{
  # Normal priority (100)
  services.nginx.enable = true;
  
  # Low priority (1000) - easily overridden
  services.nginx.enable = lib.mkDefault true;
  
  # High priority (50) - overrides most things
  services.nginx.enable = lib.mkForce false;
  
  # Custom priority
  services.nginx.enable = lib.mkOverride 75 true;
}
```

## Importing Modules

```nix
# configuration.nix
{ config, lib, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
    ./services/myservice.nix
    ./users.nix
  ];
  
  # Rest of configuration
}
```

## Example: Complete Service Module

```nix
# myservice.nix
{ config, lib, pkgs, ... }:

let
  cfg = config.services.myservice;
  configFile = pkgs.writeText "myservice.conf" ''
    port = ${toString cfg.port}
    ${lib.concatStringsSep "\n" (lib.mapAttrsToList (k: v: "${k} = ${v}") cfg.settings)}
  '';
in {
  options.services.myservice = {
    enable = lib.mkEnableOption "myservice";
    port = lib.mkOption { type = lib.types.port; default = 8080; };
    settings = lib.mkOption { type = lib.types.attrsOf lib.types.str; default = {}; };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.myservice = {
      wantedBy = [ "multi-user.target" ];
      serviceConfig.ExecStart = "${pkgs.myservice}/bin/myservice -c ${configFile}";
    };
  };
}
```

