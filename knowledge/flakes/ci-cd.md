# CI/CD with Nix Flakes

## GitHub Actions

### Basic Build and Check

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: DeterminateSystems/nix-installer-action@main
      
      - uses: DeterminateSystems/magic-nix-cache-action@main
      
      - name: Check flake
        run: nix flake check
      
      - name: Build package
        run: nix build
      
      - name: Run tests
        run: nix develop --command make test
```

### Multi-Platform Build

```yaml
name: Multi-Platform CI

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: DeterminateSystems/nix-installer-action@main
      - uses: DeterminateSystems/magic-nix-cache-action@main
      - run: nix build
```

### Formatting Check

```yaml
name: Format Check

on: [push, pull_request]

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DeterminateSystems/nix-installer-action@main
      - name: Check formatting
        run: nix fmt -- --check .
```

## GitLab CI

```yaml
# .gitlab-ci.yml
image: nixos/nix:latest

variables:
  NIX_CONFIG: "experimental-features = nix-command flakes"

before_script:
  - nix-channel --update

build:
  script:
    - nix build
  artifacts:
    paths:
      - result

check:
  script:
    - nix flake check

test:
  script:
    - nix develop --command make test
```

## Cachix (Binary Cache)

### Setup Cachix

```bash
# Install cachix
nix-env -iA cachix -f https://cachix.org/api/v1/install

# Authenticate
cachix authtoken YOUR_TOKEN

# Use a cache
cachix use mycache
```

### GitHub Actions with Cachix

```yaml
name: CI with Cachix

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DeterminateSystems/nix-installer-action@main
      
      - uses: cachix/cachix-action@v14
        with:
          name: mycache
          authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
      
      - run: nix build
```

## Flake Checks

Define checks in your flake:

```nix
{
  outputs = { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      checks.x86_64-linux = {
        # Build the package as a check
        package = self.packages.x86_64-linux.default;
        
        # Formatting check
        formatting = pkgs.runCommand "check-format" { } ''
          ${pkgs.nixfmt-rfc-style}/bin/nixfmt --check ${self}/*.nix
          touch $out
        '';
        
        # Lint check
        lint = pkgs.runCommand "lint" { } ''
          cd ${self}
          ${pkgs.statix}/bin/statix check .
          touch $out
        '';
        
        # Run tests
        tests = pkgs.runCommand "tests" {
          buildInputs = [ pkgs.go ];
        } ''
          cd ${self}
          go test ./...
          touch $out
        '';
      };
    };
}
```

Run checks:
```bash
nix flake check  # Runs all checks
```

## NixOS Tests in CI

```nix
checks.x86_64-linux = {
  integration = pkgs.nixosTest {
    name = "my-integration-test";
    
    nodes.server = { pkgs, ... }: {
      services.myservice.enable = true;
    };
    
    testScript = ''
      server.start()
      server.wait_for_unit("myservice.service")
      server.succeed("curl localhost:8080")
    '';
  };
};
```

## Docker Image Build in CI

```yaml
name: Build Docker Image

on:
  push:
    tags: ['v*']

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DeterminateSystems/nix-installer-action@main
      
      - name: Build image
        run: nix build .#dockerImage
      
      - name: Load and push
        run: |
          docker load < result
          docker tag myimage:latest ghcr.io/${{ github.repository }}:${{ github.ref_name }}
          docker push ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

## Flake for Docker Image

```nix
{
  outputs = { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      packages.x86_64-linux = {
        default = pkgs.hello;
        
        dockerImage = pkgs.dockerTools.buildLayeredImage {
          name = "myimage";
          tag = "latest";
          contents = [ self.packages.x86_64-linux.default ];
          config.Cmd = [ "/bin/hello" ];
        };
      };
    };
}
```

## Best Practices

1. **Use Determinate Systems installer** for faster CI setup
2. **Enable magic-nix-cache** for GitHub Actions caching
3. **Use Cachix** for sharing builds across CI runs
4. **Define checks** in flake for `nix flake check`
5. **Pin Nix version** in CI for reproducibility
6. **Run `nix flake check`** on every PR

