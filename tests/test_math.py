def add(a, b):
    return a + b  # Intentional bug

def test_add():
    assert add(2, 2) == 4