'''
PRACTICA 01 OAC

This version subtracts consecutive odd numbers:
1 + 3 + 5 + ... + (2n - 1) = n^2

By:
- Ayala Hernández María Fernanda
- Salazar Islas Luis Daniel
- Tepal Briseño Hansel Yael
- Ugartechea González Luis Antonio

'''

# --------------- ARM Assembly function ---------------

@micropython.asm_thumb
def odd_sqrt(r0):
    mov(r4, r0) # Remaining value
    mov(r1, 1) # Current odd number
    mov(r2, 0) # Integer square root

    label(LOOP)
    cmp(r1, r4) # Check if the current odd number is greater than the remaining value
    bhi(DONE)

    sub(r4, r4, r1) # Subtract the current odd number from the remaining value
    add(r1, r1, 2) # Increment the current odd number by 2
    add(r2, r2, 1) # Counts one successful subtraction, which corresponds to the integer square root
    b(LOOP)

    label(DONE)
    mov(r0, r2)

# --------------- MicroPython function ---------------

def py_odd_sqrt(x):
    remainder = x
    odd_number = 1
    root = 0

    while remainder >= odd_number:
        remainder -= odd_number
        odd_number += 2
        root += 1

    return root


tests = [
    (0, 0),
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 2),
    (5, 2),
    (8, 2),
    (9, 3),
    (10, 3),
    (24, 4),
    (25, 5),
    (35, 5),
    (36, 6),
    (50, 7),
    (99, 9),
    (100, 10),
    (1000, 31),
]

print("=" * 42)
print("  INTEGER SQUARE ROOT - ODD NUMBERS")
print("=" * 42)
print("\n[ARM Assembly]")

for x, expected in tests:
    result = odd_sqrt(x)
    if result == expected:
        print("  PASS | input: {:>6} | sqrt: {:>4}".format(x, result))
    else:
        print("  FAIL | input: {:>6} | expected: {:>4} | got: {:>4}".format(x, expected, result))

print("\n[MicroPython]")

for x, expected in tests:
    result = py_odd_sqrt(x)
    if result == expected:
        print("  PASS | input: {:>6} | sqrt: {:>4}".format(x, result))
    else:
        print("  FAIL | input: {:>6} | expected: {:>4} | got: {:>4}".format(x, expected, result))

print("\n" + "=" * 42)
print("                 DONE")
print("=" * 42)
