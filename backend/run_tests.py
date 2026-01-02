#!/usr/bin/env python3
"""
Test Runner Script
Palaiž visus testu moduļus un parāda rezultātus
"""
import pytest
import sys


def main():
    """Galvenā funkcija testu palaišanai"""
    print("=" * 70)
    print("MĀCĪBU MATERIĀLU ĢENERĒŠANAS SISTĒMAS TESTI")
    print("=" * 70)
    print()

    # Pytest argumenti
    args = [
        '-v',              # Verbose output
        '--tb=short',      # Short traceback format
        'tests/',          # Test directory
        '-p', 'no:warnings'  # Disable warnings
    ]

    # Palaiž testus
    exit_code = pytest.main(args)

    print()
    print("=" * 70)
    if exit_code == 0:
        print("✅ VISI TESTI IZPILDĀS (OK)")
        print("=" * 70)
    else:
        print("❌ DAŽI TESTI NEIZPILDĀS (N)")
        print("=" * 70)
        print()
        print("Detalizēta informācija par kļūdām ir redzama augstāk.")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
