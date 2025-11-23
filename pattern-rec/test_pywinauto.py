"""
Test script to demonstrate pywinauto UI element detection capabilities
"""
from pattern_detector import PatternDetector
from datetime import datetime
import time

def test_basic_detection():
    """Test basic pattern detection without pywinauto"""
    print("=" * 60)
    print("Testing Basic Pattern Detection")
    print("=" * 60)
    
    detector = PatternDetector()
    
    # Simulate repeated Ctrl+C
    for i in range(4):
        detector.add_action({
            'type': 'keypress',
            'key': 'c',
            'modifiers': ['ctrl'],
            'timestamp': datetime.now()
        })
        time.sleep(0.5)
    
    patterns = detector.detect_patterns()
    
    if patterns:
        print("\n✅ Patterns detected:")
        for pattern in patterns:
            print(f"  - Type: {pattern['type']}")
            print(f"    Suggestion: {pattern['suggestion']}")
            print(f"    Severity: {pattern['severity']}")
    else:
        print("\n❌ No patterns detected")
    
    stats = detector.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total actions: {stats['total_actions']}")
    print(f"  Pywinauto enabled: {stats.get('pywinauto_enabled', False)}")

def test_pywinauto_detection():
    """Test pywinauto-enhanced detection"""
    print("\n" + "=" * 60)
    print("Testing Pywinauto-Enhanced Detection")
    print("=" * 60)
    
    detector = PatternDetector()
    
    if not detector.pywinauto_enabled:
        print("\n⚠️  Pywinauto not available. Install with:")
        print("   pip install pywinauto")
        return
    
    print("\n✅ Pywinauto is enabled!")
    print("\nEnhanced pattern detection capabilities:")
    print("  1. Dialog box navigation detection")
    print("  2. Ribbon/toolbar click analysis")
    print("  3. Form filling efficiency analysis")
    print("  4. UI element type detection (buttons, menus, etc.)")
    
    # Test UI element detection at current mouse position
    print("\n📍 Testing UI element detection...")
    print("   Move your mouse over a UI element and wait...")
    
    for i in range(5, 0, -1):
        print(f"   Checking in {i}...", end='\r')
        time.sleep(1)
    
    # Try to get element at a common location (center of screen)
    try:
        from pywinauto import Desktop
        desktop = Desktop(backend='uia')
        
        # Get screen dimensions
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Try center of screen
        x, y = screen_width // 2, screen_height // 2
        
        element = desktop.from_point(x, y)
        if element:
            print(f"\n\n✅ Found element at screen center ({x}, {y}):")
            print(f"   Control Type: {element.element_info.control_type}")
            print(f"   Class: {element.element_info.class_name}")
            print(f"   Name: {element.element_info.name or '(unnamed)'}")
        
    except Exception as e:
        print(f"\n\n⚠️  Could not detect element: {e}")
    
    # Simulate dialog navigation pattern
    print("\n\n🔍 Simulating dialog navigation pattern...")
    for i in range(4):
        detector.add_action({
            'type': 'click',
            'position': (500, 400),  # Typical dialog button position
            'button': 'left',
            'timestamp': datetime.now()
        })
        time.sleep(0.5)
    
    patterns = detector.detect_patterns()
    if patterns:
        print("\n✅ Enhanced patterns detected:")
        for pattern in patterns:
            print(f"  - Type: {pattern['type']}")
            print(f"    Suggestion: {pattern['suggestion']}")
            print(f"    Count: {pattern.get('count', 'N/A')}")

def test_form_filling_detection():
    """Test form filling pattern detection"""
    print("\n" + "=" * 60)
    print("Testing Form Filling Detection")
    print("=" * 60)
    
    detector = PatternDetector()
    
    if not detector.pywinauto_enabled:
        print("\n⚠️  Pywinauto required for this test")
        return
    
    # Simulate clicking on multiple form fields
    print("\n🔍 Simulating form field clicks (inefficient pattern)...")
    
    form_positions = [
        (300, 200), (300, 250), (300, 300), (300, 350)
    ]
    
    for pos in form_positions:
        # Click on field
        detector.add_action({
            'type': 'click',
            'position': pos,
            'button': 'left',
            'timestamp': datetime.now()
        })
        time.sleep(0.3)
        
        # Type something
        detector.add_action({
            'type': 'keypress',
            'key': 'a',
            'modifiers': [],
            'timestamp': datetime.now()
        })
        time.sleep(0.3)
    
    patterns = detector.detect_patterns()
    
    if patterns:
        print("\n✅ Form filling patterns detected:")
        for pattern in patterns:
            if pattern['type'] == 'form_navigation':
                print(f"  - {pattern['suggestion']}")
                print(f"  - Detected {pattern['count']} field clicks")
    else:
        print("\n⚠️  No form patterns detected (may need real form fields)")

def main():
    """Run all tests"""
    print("\n🚀 Pywinauto Pattern Detection Test Suite")
    print("=" * 60)
    
    ()
    test_pywinauto_detection()
    test_form_filling_detection()
    
    print("\n" + "=" * 60)
    print("✅ Test suite complete!")
    print("=" * 60)
    print("\nTo see these features in action, run: python main.py")
    print("Then interact with applications normally.")

if __name__ == "__main__":
    main()
