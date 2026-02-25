{
  description = "Java development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          name = "java-dev";

          packages = with pkgs; [
            # JDK (pick your version)
            jdk17
            # jdk21  # Alternative: Java 21

            # Build tools
            maven
            gradle

            # Language server (for IDE support)
            jdt-language-server

            # Code formatting
            google-java-format

            # Useful tools
            jq
            gnumake
          ];

          env = {
            # Set JAVA_HOME
            JAVA_HOME = "${pkgs.jdk17}";
            # Maven options
            MAVEN_OPTS = "-Xmx2g";
            # Gradle options
            GRADLE_OPTS = "-Xmx2g";
          };

          shellHook = ''
            echo "☕ Java development environment"
            echo "   Java version: $(java -version 2>&1 | head -1)"
            echo "   Maven version: $(mvn --version 2>&1 | head -1)"
            echo "   Gradle version: $(gradle --version 2>&1 | grep Gradle)"
            echo ""
            echo "JAVA_HOME: $JAVA_HOME"
            echo ""
            echo "Available tools:"
            echo "  java                - Java runtime"
            echo "  javac               - Java compiler"
            echo "  mvn                 - Maven build tool"
            echo "  gradle              - Gradle build tool"
            echo "  google-java-format  - Code formatter"
            echo ""
            echo "Quick start (Maven):"
            echo "  mvn archetype:generate  # Create new project"
            echo "  mvn compile             # Compile"
            echo "  mvn test                # Run tests"
            echo "  mvn package             # Build JAR"
            echo ""
            echo "Quick start (Gradle):"
            echo "  gradle init             # Create new project"
            echo "  gradle build            # Build"
            echo "  gradle test             # Run tests"
            echo ""
            echo "Format code:"
            echo "  google-java-format -i src/**/*.java"
          '';
        };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}

