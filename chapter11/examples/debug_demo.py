"""Interactive only: python -m pdb examples/debug_demo.py."""
def retained(quantity, price, returned):
    return quantity * price - returned

def main():
    result = retained(3, 100, 1)
    print("actual", result)
    print("expected", 200)

if __name__ == "__main__":
    main()
