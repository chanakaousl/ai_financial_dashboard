#!/usr/bin/env python
"""
Command-line interface entry point for the JKH Financial Dashboard.

Usage:
    python -m backend.cli [command]
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.commands import cli

if __name__ == '__main__':
    cli() 