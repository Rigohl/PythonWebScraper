#!/usr/bin/env python3
"""
Test script for CodeAutoModifier system
"""

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.intelligence.code_auto_modifier import CodeAutoModifier

def test_code_auto_modifier():
    """Test all CodeAutoModifier capabilities."""
    print("🧠 Testing CodeAutoModifier System")
    print("=" * 50)
    
    # Initialize
    print("1. Initializing CodeAutoModifier...")
    cam = CodeAutoModifier(os.getcwd())
    print("✅ CodeAutoModifier initialized successfully")
    
    # Test scraper generation
    print("\n2. Testing scraper module generation...")
    result = cam.create_scraper_module('test_example', 'test-example.com')
    print(f"✅ Generation result type: {type(result)}")
    
    if isinstance(result, dict):
        print(f"✅ Files to be created: {list(result.keys())}")
        print(f"✅ Total files: {len(result)}")
    else:
        print(f"📝 Result content length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
    
    # Test code analysis
    print("\n3. Testing code analysis...")
    test_code = '''
def test_function():
    """A test function."""
    x = 1
    y = 2
    return x + y
'''
    
    try:
        analysis = cam.analyze_code_quality(test_code)
        print(f"✅ Code analysis completed: {type(analysis)}")
        print(f"✅ Analysis contains: {list(analysis.keys()) if isinstance(analysis, dict) else 'Non-dict result'}")
    except Exception as e:
        print(f"❌ Code analysis error: {e}")
    
    # Test complexity calculation  
    print("\n4. Testing complexity calculation...")
    try:
        complexity = cam.calculate_complexity(test_code)
        print(f"✅ Complexity calculated: {complexity}")
    except Exception as e:
        print(f"❌ Complexity calculation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 CodeAutoModifier testing completed!")

if __name__ == "__main__":
    test_code_auto_modifier()