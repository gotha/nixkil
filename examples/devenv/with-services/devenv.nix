# Devenv configuration with services
# Documentation: https://devenv.sh/services/
{ pkgs, lib, config, inputs, ... }:

{
  name = "app-with-services";

  # Environment variables
  env = {
    # Database connection
    DATABASE_URL = "postgresql://devenv@localhost:5432/myapp?host=${config.env.PGHOST}";
    REDIS_URL = "redis://localhost:6379";

    # Application settings
    APP_ENV = "development";
    DEBUG = "true";
  };

  # Packages
  packages = with pkgs; [
    git
    jq
    curl
    postgresql # For psql CLI
    redis # For redis-cli
  ];

  # Shell hook
  enterShell = ''
    echo "🚀 Development environment with services"
    echo ""
    echo "Services:"
    echo "  PostgreSQL: localhost:5432 (user: devenv, db: myapp)"
    echo "  Redis:      localhost:6379"
    echo ""
    echo "Commands:"
    echo "  devenv up      - Start all services"
    echo "  devenv down    - Stop all services"
    echo "  psql myapp     - Connect to PostgreSQL"
    echo "  redis-cli      - Connect to Redis"
    echo ""
    echo "Database URL: $DATABASE_URL"
  '';

  # Scripts
  scripts = {
    db-reset.exec = ''
      echo "Resetting database..."
      dropdb --if-exists myapp
      createdb myapp
      echo "Database reset complete!"
    '';

    db-seed.exec = ''
      echo "Seeding database..."
      psql myapp -c "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT);"
      psql myapp -c "INSERT INTO users (name) VALUES ('Alice'), ('Bob');"
      echo "Database seeded!"
    '';
  };

  # PostgreSQL service
  services.postgres = {
    enable = true;
    package = pkgs.postgresql_16;
    initialDatabases = [{ name = "myapp"; }];
    initialScript = ''
      CREATE USER devenv WITH SUPERUSER;
    '';
    listen_addresses = "127.0.0.1";
    port = 5432;
  };

  # Redis service
  services.redis = {
    enable = true;
    port = 6379;
  };

  # MySQL (alternative to PostgreSQL)
  # services.mysql = {
  #   enable = true;
  #   package = pkgs.mysql80;
  #   initialDatabases = [{ name = "myapp"; }];
  # };

  # MongoDB
  # services.mongodb = {
  #   enable = true;
  # };

  # Elasticsearch
  # services.elasticsearch = {
  #   enable = true;
  # };

  # RabbitMQ
  # services.rabbitmq = {
  #   enable = true;
  # };

  # MinIO (S3-compatible storage)
  # services.minio = {
  #   enable = true;
  # };

  # Mailhog (email testing)
  # services.mailhog = {
  #   enable = true;
  # };

  # Process management (run multiple processes)
  # processes = {
  #   web.exec = "python -m http.server 8000";
  #   worker.exec = "python worker.py";
  # };
}

