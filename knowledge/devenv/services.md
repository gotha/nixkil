# devenv Services Configuration

## Overview

devenv can manage background services like databases, caches, and message queues. Services run in the background and persist data between shell sessions.

## Starting and Managing Services

```bash
# Start all enabled services
devenv up

# Start in foreground (see logs)
devenv up --foreground

# Stop all services
# Ctrl+C in foreground, or:
devenv processes stop

# Check service status
devenv info
```

## PostgreSQL

```nix
{
  services.postgres = {
    enable = true;
    package = pkgs.postgresql_15;
    
    # Port (default: 5432)
    port = 5432;
    
    # Listen address
    listen_addresses = "127.0.0.1";
    
    # Create databases on init
    initialDatabases = [
      { name = "myapp_dev"; }
      { name = "myapp_test"; }
    ];
    
    # Run SQL on init
    initialScript = ''
      CREATE USER myuser WITH PASSWORD 'secret' CREATEDB;
      GRANT ALL PRIVILEGES ON DATABASE myapp_dev TO myuser;
    '';
    
    # PostgreSQL settings
    settings = {
      log_statement = "all";
      log_min_duration_statement = 100;
    };
  };
  
  # Set DATABASE_URL automatically
  env.DATABASE_URL = "postgres://myuser:secret@localhost:5432/myapp_dev";
}
```

## MySQL / MariaDB

```nix
{
  services.mysql = {
    enable = true;
    package = pkgs.mariadb;
    
    initialDatabases = [
      { name = "myapp"; }
    ];
    
    # Run SQL on init
    initialScript = ''
      CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'secret';
      GRANT ALL ON myapp.* TO 'myuser'@'localhost';
    '';
    
    settings = {
      mysqld = {
        port = 3306;
        bind-address = "127.0.0.1";
      };
    };
  };
}
```

## Redis

```nix
{
  services.redis = {
    enable = true;
    port = 6379;
    bind = "127.0.0.1";
    
    # Extra configuration
    extraConfig = ''
      maxmemory 256mb
      maxmemory-policy allkeys-lru
    '';
  };
  
  env.REDIS_URL = "redis://localhost:6379";
}
```

## MongoDB

```nix
{
  services.mongodb = {
    enable = true;
    package = pkgs.mongodb;
    
    # Additional arguments
    additionalArgs = [
      "--port" "27017"
      "--bind_ip" "127.0.0.1"
    ];
  };
}
```

## Elasticsearch

```nix
{
  services.elasticsearch = {
    enable = true;
    package = pkgs.elasticsearch7;
    
    # Cluster settings
    cluster_name = "devenv-cluster";
    single_node = true;
    
    # Extra configuration
    extraConf = ''
      http.port: 9200
      xpack.security.enabled: false
    '';
  };
}
```

## RabbitMQ

```nix
{
  services.rabbitmq = {
    enable = true;
    
    # Management UI
    managementPlugin.enable = true;
    
    # Port
    port = 5672;
    
    # Extra configuration
    configItems = {
      "default_user" = "guest";
      "default_pass" = "guest";
    };
  };
}
```

## MinIO (S3-compatible storage)

```nix
{
  services.minio = {
    enable = true;
    
    # Credentials
    accessKey = "minioadmin";
    secretKey = "minioadmin";
    
    # Create buckets on start
    buckets = [ "mybucket" "uploads" ];
  };
  
  env.AWS_ENDPOINT_URL = "http://localhost:9000";
  env.AWS_ACCESS_KEY_ID = "minioadmin";
  env.AWS_SECRET_ACCESS_KEY = "minioadmin";
}
```

## Mailhog (Email testing)

```nix
{
  services.mailhog = {
    enable = true;
    
    # SMTP port
    smtpPort = 1025;
    
    # Web UI port
    uiPort = 8025;
  };
  
  env.SMTP_HOST = "localhost";
  env.SMTP_PORT = "1025";
}
```

## Caddy (Web server/reverse proxy)

```nix
{
  services.caddy = {
    enable = true;
    
    config = ''
      localhost:8080 {
        reverse_proxy localhost:3000
      }
    '';
  };
}
```

## Combining Multiple Services

```nix
{
  services.postgres = {
    enable = true;
    initialDatabases = [{ name = "myapp"; }];
  };
  
  services.redis.enable = true;
  services.minio.enable = true;
  services.mailhog.enable = true;
  
  # Set all URLs
  env = {
    DATABASE_URL = "postgres://localhost/myapp";
    REDIS_URL = "redis://localhost:6379";
    S3_ENDPOINT = "http://localhost:9000";
    SMTP_URL = "smtp://localhost:1025";
  };
  
  # Ensure services start before processes
  processes.web = {
    exec = "npm run dev";
    process-compose = {
      depends_on = {
        postgres.condition = "process_healthy";
        redis.condition = "process_started";
      };
    };
  };
}
```

## Data Persistence

Service data is stored in `.devenv/state/`. To reset:

```bash
rm -rf .devenv/state/
devenv up
```

