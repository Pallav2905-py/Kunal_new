#!/usr/bin/env python3
"""
LeadFlow — Quick launch script.
Run from project root: python run.py
"""
import sys
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import main

if __name__ == "__main__":
    main()
