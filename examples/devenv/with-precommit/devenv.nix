# Devenv configuration with pre-commit hooks
# Documentation: https://devenv.sh/pre-commit-hooks/
{ pkgs, lib, config, inputs, ... }:

{
  name = "project-with-precommit";

  # Environment variables
  env = {
    PROJECT_ROOT = config.env.DEVENV_ROOT;
  };

  # Packages
  packages = with pkgs; [
    git
    jq
    nixfmt-rfc-style
    shellcheck
    shfmt
  ];

  # Languages
  languages = {
    python = {
      enable = true;
      version = "3.11";
    };

    javascript = {
      enable = true;
      npm.enable = true;
    };

    go.enable = true;

    nix.enable = true;
  };

  # Shell hook
  enterShell = ''
    echo "🪝 Development environment with pre-commit hooks"
    echo ""
    echo "Pre-commit hooks are automatically installed!"
    echo ""
    echo "Manual commands:"
    echo "  pre-commit run --all-files  # Run all hooks"
    echo "  pre-commit run <hook-id>    # Run specific hook"
    echo ""
    echo "Configured hooks:"
    echo "  - nixfmt (Nix formatting)"
    echo "  - ruff (Python linting)"
    echo "  - ruff-format (Python formatting)"
    echo "  - prettier (JS/JSON/YAML formatting)"
    echo "  - gofmt (Go formatting)"
    echo "  - shellcheck (Shell linting)"
    echo "  - trailing-whitespace"
    echo "  - end-of-file-fixer"
  '';

  # Pre-commit hooks configuration
  pre-commit.hooks = {
    # Nix
    nixfmt-rfc-style = {
      enable = true;
      # Alternatively use nixfmt or nixpkgs-fmt
    };

    # Python
    ruff = {
      enable = true;
      # args = [ "--fix" ];  # Auto-fix issues
    };

    ruff-format = {
      enable = true;
    };

    # JavaScript/TypeScript
    prettier = {
      enable = true;
      types_or = [ "javascript" "typescript" "json" "yaml" "markdown" ];
    };

    eslint = {
      enable = true;
      types = [ "javascript" "typescript" ];
      # Requires eslint config in project
    };

    # Go
    gofmt.enable = true;

    govet = {
      enable = true;
    };

    # Shell
    shellcheck = {
      enable = true;
    };

    shfmt = {
      enable = true;
      args = [ "-i" "2" "-ci" ];  # 2-space indent, case indent
    };

    # Generic
    trailing-whitespace = {
      enable = true;
      # Exclude binary files
      excludes = [ ".*\\.(png|jpg|gif|ico|pdf)$" ];
    };

    end-of-file-fixer = {
      enable = true;
      excludes = [ ".*\\.(png|jpg|gif|ico|pdf)$" ];
    };

    check-merge-conflict.enable = true;

    check-added-large-files = {
      enable = true;
      args = [ "--maxkb=500" ];  # Fail if file > 500KB
    };

    # YAML
    check-yaml.enable = true;

    # JSON
    check-json.enable = true;

    # Secrets detection
    detect-private-key.enable = true;

    # Custom hook example
    # custom-lint = {
    #   enable = true;
    #   entry = "${pkgs.writeShellScript "custom-lint" ''
    #     echo "Running custom lint..."
    #     # Add your custom linting logic here
    #   ''}";
    #   files = "\\.py$";
    #   pass_filenames = true;
    # };
  };
}

