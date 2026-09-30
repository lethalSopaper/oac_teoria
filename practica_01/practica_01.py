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
    cmp(r1, r4)
    bhi(DONE)

    sub(r4, r4, r1)
    add(r1, r1, 2)
    add(r2, r2, 1)
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
    (4, 2),
    (8, 2),
    (9, 3),
    (15, 3),
    (16, 4),
    (26, 5),
    (121, 11),
    (65536, 256),
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
