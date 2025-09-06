import sys
print(f"Python version: {sys.version}")

try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
    print("NumPy is available and working correctly.")
    
    # Teste básico do NumPy
    arr = np.array([1, 2, 3, 4, 5])
    print(f"NumPy array: {arr}")
    print(f"NumPy array mean: {arr.mean()}")
    print("NumPy test successful!")
    
except ImportError as e:
    print(f"Error importing NumPy: {e}")
except Exception as e:
    print(f"Error using NumPy: {e}")
