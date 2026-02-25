# Nix Built-in Functions

Built-in functions are available via the `builtins` attrset or directly in scope.

## Type Checking

```nix
builtins.isString "hello"     # true
builtins.isInt 42             # true
builtins.isBool true          # true
builtins.isList [ 1 2 ]       # true
builtins.isAttrs { a = 1; }   # true
builtins.isFunction (x: x)    # true
builtins.isPath ./file        # true
builtins.isNull null          # true

builtins.typeOf "hello"       # "string"
builtins.typeOf 42            # "int"
```

## String Functions

```nix
# String manipulation
builtins.stringLength "hello"                    # 5
builtins.substring 0 3 "hello"                   # "hel"
builtins.replaceStrings ["o"] ["0"] "hello"      # "hell0"

# String splitting/joining
builtins.split ":" "a:b:c"                       # ["a" ":" "b" ":" "c"]
builtins.concatStringsSep ", " ["a" "b" "c"]     # "a, b, c"

# Conversion
builtins.toString 42                              # "42"
builtins.toJSON { a = 1; }                       # "{\"a\":1}"
builtins.fromJSON "{\"a\":1}"                    # { a = 1; }
```

## List Functions

```nix
builtins.length [ 1 2 3 ]                        # 3
builtins.head [ 1 2 3 ]                          # 1
builtins.tail [ 1 2 3 ]                          # [ 2 3 ]
builtins.elemAt [ 1 2 3 ] 1                      # 2

builtins.elem 2 [ 1 2 3 ]                        # true
builtins.filter (x: x > 1) [ 1 2 3 ]             # [ 2 3 ]
builtins.map (x: x * 2) [ 1 2 3 ]                # [ 2 4 6 ]
builtins.foldl' (acc: x: acc + x) 0 [ 1 2 3 ]    # 6

builtins.sort builtins.lessThan [ 3 1 2 ]        # [ 1 2 3 ]
builtins.concatLists [ [ 1 ] [ 2 3 ] ]           # [ 1 2 3 ]
builtins.genList (i: i * 2) 3                    # [ 0 2 4 ]
```

## Attribute Set Functions

```nix
builtins.attrNames { b = 2; a = 1; }             # [ "a" "b" ] (sorted)
builtins.attrValues { a = 1; b = 2; }            # [ 1 2 ]

builtins.hasAttr "a" { a = 1; }                  # true
builtins.getAttr "a" { a = 1; }                  # 1

builtins.intersectAttrs { a = 1; b = 2; } { b = 3; c = 4; }  # { b = 3; }
builtins.removeAttrs { a = 1; b = 2; } [ "a" ]   # { b = 2; }

builtins.listToAttrs [ { name = "a"; value = 1; } ]  # { a = 1; }
builtins.mapAttrs (n: v: v * 2) { a = 1; b = 2; }    # { a = 2; b = 4; }

builtins.catAttrs "a" [ { a = 1; } { b = 2; } { a = 3; } ]  # [ 1 3 ]
```

## Path and File Functions

```nix
builtins.pathExists ./file.nix                   # true/false
builtins.readFile ./file.txt                     # "contents..."
builtins.readDir ./dir                           # { file = "regular"; subdir = "directory"; }

builtins.baseNameOf ./path/to/file               # "file"
builtins.dirOf ./path/to/file                    # ./path/to

# Store paths
builtins.path { path = ./src; name = "source"; } # /nix/store/...-source
builtins.toPath "/some/path"                     # /some/path (as path type)
```

## Fetching (Impure without hash)

```nix
# Fetch from URL (use hash for purity)
builtins.fetchurl {
  url = "https://example.com/file.tar.gz";
  sha256 = "0abc123...";
}

# Fetch git repository
builtins.fetchGit {
  url = "https://github.com/owner/repo";
  rev = "abc123...";
}

# Fetch tarball
builtins.fetchTarball {
  url = "https://github.com/owner/repo/archive/main.tar.gz";
  sha256 = "0abc123...";
}
```

## Derivation

```nix
# Low-level derivation (prefer pkgs.stdenv.mkDerivation)
builtins.derivation {
  name = "my-derivation";
  system = "x86_64-linux";
  builder = "/bin/sh";
  args = [ "-c" "echo hello > $out" ];
}
```

## Debugging

```nix
builtins.trace "debug message" value             # Prints message, returns value
builtins.traceVerbose "verbose" value            # Only with --trace-verbose
builtins.abort "error message"                   # Abort evaluation
builtins.throw "error message"                   # Throw catchable error

builtins.seq a b                                 # Evaluate a, return b
builtins.deepSeq a b                             # Deep evaluate a, return b
```

## Miscellaneous

```nix
builtins.currentSystem                           # "x86_64-linux" or similar
builtins.nixVersion                              # "2.18.1" or similar

builtins.import ./file.nix                       # Import and evaluate
builtins.scopedImport { x = 1; } ./file.nix      # Import with custom scope

builtins.tryEval (throw "err")                   # { success = false; value = false; }
builtins.tryEval 42                              # { success = true; value = 42; }

builtins.hashString "sha256" "hello"             # Hash a string
builtins.hashFile "sha256" ./file                # Hash a file
```

