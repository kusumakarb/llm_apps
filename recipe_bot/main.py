#!/usr/bin/env python3
"""
Recipe Bot - Generate recipes from ingredients using LLM with observability
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interface import main

if __name__ == "__main__":
    main()