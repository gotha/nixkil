# Nix Expression Syntax

## Basic Types

### Strings
```nix
# Simple string
"hello world"

# Multi-line string (indentation is stripped)
''
  line 1
  line 2
''

# String interpolation
"Hello, ${name}!"

# Escape sequences in double-quoted strings
"tab:\t newline:\n"

# Escape ${} in multi-line strings
''
  literal: ''${not-interpolated}
''
```

### Numbers
```nix
42        # Integer
3.14      # Float (less common in Nix)
```

### Booleans and Null
```nix
true
false
null
```

### Paths
```nix
./relative/path
/absolute/path
~/home/path        # Expands to /home/user/path

# Path with interpolation (creates a store path)
./. + "/${filename}"
```

### Lists
```nix
[ 1 2 3 ]
[ "a" "b" "c" ]
[ 1 "mixed" true ]  # Can contain mixed types
```

### Attribute Sets (attrsets)
```nix
# Basic attrset
{ name = "value"; another = 123; }

# Nested attrsets
{ outer.inner = "value"; }  # Same as { outer = { inner = "value"; }; }

# Recursive attrset (attributes can reference each other)
rec { x = 1; y = x + 1; }
```

## Operators

### Arithmetic
```nix
1 + 2    # Addition
5 - 3    # Subtraction
2 * 3    # Multiplication
10 / 3   # Division (integer)
```

### Comparison
```nix
a == b   # Equality
a != b   # Inequality
a < b    # Less than
a <= b   # Less than or equal
a > b    # Greater than
a >= b   # Greater than or equal
```

### Logical
```nix
a && b   # AND
a || b   # OR
!a       # NOT
a -> b   # Implication (equivalent to !a || b)
```

### String/Path
```nix
"hello" + " world"   # String concatenation
./path + "/file"     # Path concatenation
```

### Attribute Set
```nix
set.attr             # Access attribute
set.attr or default  # Access with default
set ? attr           # Check if attribute exists
set1 // set2         # Merge sets (right takes precedence)
```

## Let Expressions
```nix
let
  x = 1;
  y = 2;
in
  x + y  # Returns 3
```

## Conditionals
```nix
if condition then
  valueIfTrue
else
  valueIfFalse
```

## Functions

### Lambda syntax
```nix
# Single argument
x: x + 1

# Multiple arguments (curried)
x: y: x + y

# Attrset argument with destructuring
{ name, version }: "${name}-${version}"

# With default values
{ name, version ? "1.0" }: "${name}-${version}"

# With additional attributes allowed
{ name, ... }: name

# Capture extra attributes
{ name, ...}@args: name + (builtins.toJSON args)
```

### Function application
```nix
# Apply function
f x

# Apply with attrset argument
f { name = "foo"; version = "1.0"; }

# Chained application
f x y  # Same as (f x) y
```

## With Expression
```nix
# Bring attrset attributes into scope
with pkgs; [ git vim curl ]

# Equivalent to
[ pkgs.git pkgs.vim pkgs.curl ]
```

## Inherit
```nix
# In attrsets
let x = 1; in { inherit x; }  # Same as { x = x; }

# From another attrset
{ inherit (pkgs) git vim; }   # Same as { git = pkgs.git; vim = pkgs.vim; }
```

## Assert
```nix
assert condition; expression

# Example
assert builtins.isString name; "Name is ${name}"
```

## Import
```nix
# Import another Nix file
import ./other.nix

# Import and call with arguments
import ./package.nix { inherit pkgs; }
```

