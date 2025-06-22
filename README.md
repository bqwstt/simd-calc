# SIMD Calculator
ASM Transpiler for a simple programming language supporting basic math functions.

This is an educational project, aiming to gain a better understanding on how optimizing compilers work by implementing compiler optimizations from scratch, for different architectures, by emitting raw assembly code for each.

Supports operations such as:
- math functions (adds, subtracts, multiplies, divides, exponents) 
- for loops
- arrays 
- basic function support

## Example code
```
a := 42;
b := 24;
c := a + b + a * 0;
print(c);

d := [1, 2, 3, 4];
e := [1, 2, 3, 4];
f := dot(d, e);

g := 0;
for i := 0 .. 100 {
    g += 1;
}
```