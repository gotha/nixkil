# Basic devenv configuration
# Documentation: https://devenv.sh/reference/options/
{ pkgs, lib, config, inputs, ... }:

{
  # Environment name (shown in shell prompt)
  name = "my-project";

  # Environment variables
  env = {
    GREETING = "Hello from devenv!";
    PROJECT_ROOT = config.env.DEVENV_ROOT;
  };

  # Packages available in the environment
  packages = with pkgs; [
    git
    jq
    curl
    httpie
    gnumake
  ];

  # Shell customization
  enterShell = ''
    echo "🚀 Welcome to the development environment!"
    echo ""
    echo "Project: $name"
    echo "Root: $PROJECT_ROOT"
    echo ""
    echo "Available commands:"
    echo "  devenv info     - Show environment info"
    echo "  devenv up       - Start services"
    echo "  devenv shell    - Enter the shell"
  '';

  # Scripts available as commands
  scripts = {
    hello.exec = ''
      echo "$GREETING"
    '';

    build.exec = ''
      echo "Building project..."
      # Add your build commands here
    '';

    test.exec = ''
      echo "Running tests..."
      # Add your test commands here
    '';
  };

  # Languages configuration
  languages = {
    # Enable the languages you need
    # python = {
    #   enable = true;
    #   version = "3.11";
    # };

    # go.enable = true;

    # javascript = {
    #   enable = true;
    #   npm.enable = true;
    # };
  };

  # Dotenv support - automatically load .env files
  dotenv.enable = true;

  # Enable starship prompt (optional)
  # starship.enable = true;

  # Diff against pure Nix environment (for debugging)
  # difftastic.enable = true;
}

