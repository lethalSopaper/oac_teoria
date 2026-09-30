'''

PRACTICA 01 OAC

- Jaramillo Rodriguez Leslie Citlali
- Jimenez Ayala Yordi Josue
- Salas Hernandez Camila Alexandra
- Sole Pi Arnau Roger
- Valenzuela Ascencio Gustavo

Implementar la raiz cuadrada de un entero

'''

# --------------- ARM Assembly function ---------------

@micropython.asm_thumb
def binsqrt(r0):
    mov(r4, r0)
    mov(r1, 0)
    add(r2, r0, 1)
    mov(r5, 0)

    label(LOOP)
    cmp(r1, r2)
    bhi(DONE)

    add(r3, r1, r2)
    lsr(r3, r3, 1)

    mov(r6, r3)
    mul(r6, r3)

    cmp(r6, r4)
    bhi(TOO_HIGH)

    mov(r5, r3)
    add(r1, r3, 1)
    b(LOOP)

    label(TOO_HIGH)
    sub(r2, r3, 1)
    b(LOOP)

    label(DONE)
    mov(r0, r5)

# --------------- Mycropython function ---------------

def py_binsqrt(x):
    l = 0
    r = x+1
    ans = -1
    while l<=r:
        mid = (l+r)//2
        if(mid*mid <= x):
            l = mid+1
            ans = mid
        else:
            r = mid-1

    return ans

tests = [
    (0,0),
    (1,1),
    (4,2),
    (9,3),
    (16,4),
    (121,11),
    (65536,256),
]

print("=" * 36)
print("     INTEGER SQUARE ROOT TESTS")
print("=" * 36)
print("\n[ARM Assembly]")

for x, expected in tests:
    result = binsqrt(x)
    if result == expected:
        print("  PASS | input: {:>6} | sqrt: {:>4}".format(x, result))
    else:
        print("  FAIL | input: {:>6} | expected: {:>4} | got: {:>4}".format(x, expected, result))

print("\n[MicroPython]")

for x, expected in tests:
    result = py_binsqrt(x)
    if result == expected:
        print("  PASS | input: {:>6} | sqrt: {:>4}".format(x, result))
    else:
        print("  FAIL | input: {:>6} | expected: {:>4} | got: {:>4}".format(x, expected, result))

print("\n" + "=" * 36)
print("              DONE")
print("=" * 36)