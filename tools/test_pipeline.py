#!/usr/bin/env python3
"""Test script to validate the HACKiOS F9 Pro MT6771 build pipeline tools and ADT product integration."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adt, mkadt_mt6771

def test_adt():
    data = mkadt_mt6771.build()
    root, off = adt.parse(data)
    product_found = any(c.name == 'product' for c in root.children)
    print(f"ADT parse test passed: root node name = '{root.name}', size parsed = {len(data)} bytes, product node included = {product_found}")
    return product_found

if __name__ == '__main__':
    success = test_adt()
    sys.exit(0 if success else 1)
