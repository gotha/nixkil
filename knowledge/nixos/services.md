# NixOS Service Configuration

## Systemd Services

NixOS uses systemd for service management. Configure services via `systemd.services`.

### Basic Service

```nix
{
  systemd.services.myapp = {
    description = "My Application";
    
    # When to start
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];  # Start at boot
    
    serviceConfig = {
      ExecStart = "${pkgs.myapp}/bin/myapp";
      Restart = "always";
      RestartSec = 5;
    };
  };
}
```

### Service with User/Environment

```nix
{
  systemd.services.myapp = {
    description = "My Application";
    after = [ "network.target" "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];
    
    environment = {
      DATABASE_URL = "postgres://localhost/mydb";
      NODE_ENV = "production";
    };
    
    serviceConfig = {
      Type = "simple";
      User = "myapp";
      Group = "myapp";
      WorkingDirectory = "/var/lib/myapp";
      ExecStart = "${pkgs.myapp}/bin/myapp";
      ExecReload = "${pkgs.coreutils}/bin/kill -HUP $MAINPID";
      
      # Security hardening
      NoNewPrivileges = true;
      ProtectSystem = "strict";
      ProtectHome = true;
      PrivateTmp = true;
      
      # Resource limits
      MemoryMax = "512M";
      CPUQuota = "50%";
      
      Restart = "on-failure";
      RestartSec = 10;
    };
  };
  
  # Create the user
  users.users.myapp = {
    isSystemUser = true;
    group = "myapp";
    home = "/var/lib/myapp";
    createHome = true;
  };
  users.groups.myapp = {};
}
```

## Common NixOS Services

### Web Server (Nginx)

```nix
{
  services.nginx = {
    enable = true;
    
    virtualHosts."example.com" = {
      forceSSL = true;
      enableACME = true;
      
      locations."/" = {
        proxyPass = "http://127.0.0.1:3000";
        proxyWebsockets = true;
      };
      
      locations."/static/" = {
        root = "/var/www/myapp";
      };
    };
  };
  
  # ACME (Let's Encrypt)
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@example.com";
  };
}
```

### Database (PostgreSQL)

```nix
{
  services.postgresql = {
    enable = true;
    package = pkgs.postgresql_15;
    
    ensureDatabases = [ "myapp" ];
    ensureUsers = [
      {
        name = "myapp";
        ensureDBOwnership = true;
      }
    ];
    
    authentication = ''
      local myapp myapp trust
      host myapp myapp 127.0.0.1/32 md5
    '';
    
    settings = {
      max_connections = 100;
      shared_buffers = "256MB";
    };
  };
}
```

### Cache (Redis)

```nix
{
  services.redis.servers."myapp" = {
    enable = true;
    port = 6379;
    bind = "127.0.0.1";
    
    settings = {
      maxmemory = "256mb";
      maxmemory-policy = "allkeys-lru";
    };
  };
}
```

### Docker

```nix
{
  virtualisation.docker = {
    enable = true;
    autoPrune.enable = true;
    
    # Rootless Docker
    rootless = {
      enable = true;
      setSocketVariable = true;
    };
  };
  
  # Add users to docker group
  users.users.myuser.extraGroups = [ "docker" ];
}
```

### SSH

```nix
{
  services.openssh = {
    enable = true;
    
    settings = {
      PermitRootLogin = "no";
      PasswordAuthentication = false;
      KbdInteractiveAuthentication = false;
    };
    
    # Only allow specific users
    allowUsers = [ "admin" "deploy" ];
  };
  
  # Authorized keys
  users.users.admin.openssh.authorizedKeys.keys = [
    "ssh-ed25519 AAAA... admin@example.com"
  ];
}
```

### Cron Jobs / Timers

```nix
{
  # Using systemd timers (preferred)
  systemd.timers.backup = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnCalendar = "daily";
      Persistent = true;
    };
  };
  
  systemd.services.backup = {
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${pkgs.bash}/bin/bash /path/to/backup.sh";
    };
  };
  
  # Or using services.cron
  services.cron = {
    enable = true;
    systemCronJobs = [
      "0 2 * * * root /path/to/backup.sh"
    ];
  };
}
```

### Firewall

```nix
{
  networking.firewall = {
    enable = true;
    
    allowedTCPPorts = [ 22 80 443 ];
    allowedUDPPorts = [ ];
    
    # Allow specific ranges
    allowedTCPPortRanges = [
      { from = 8000; to = 8010; }
    ];
    
    # Rich rules
    extraCommands = ''
      iptables -A INPUT -s 10.0.0.0/8 -j ACCEPT
    '';
  };
}
```

## Managing Services

```bash
# Service status
systemctl status myapp

# Start/stop/restart
sudo systemctl start myapp
sudo systemctl stop myapp
sudo systemctl restart myapp

# Enable/disable at boot
sudo systemctl enable myapp
sudo systemctl disable myapp

# View logs
journalctl -u myapp
journalctl -u myapp -f  # Follow
journalctl -u myapp --since "1 hour ago"
```

