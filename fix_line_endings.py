#!/usr/bin/env python3
"""
Fix line endings in Python files to resolve Windows import issues
"""

from pathlib import Path

def fix_line_endings(directory):
    """Convert CRLF to LF in all Python files"""
    directory = Path(directory)
    fixed_count = 0
    
    print(f"Fixing line endings in {directory}")
    
    for py_file in directory.rglob("*.py"):
        try:
            # Read file content
            with open(py_file, 'rb') as f:
                content = f.read()
            
            # Check if file has CRLF line endings
            if b'\r\n' in content:
                print(f"Fixing line endings: {py_file}")
                
                # Convert CRLF to LF
                fixed_content = content.replace(b'\r\n', b'\n')
                
                # Write back the fixed content
                with open(py_file, 'wb') as f:
                    f.write(fixed_content)
                
                fixed_count += 1
        
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    print(f"Fixed line endings in {fixed_count} files")
    return fixed_count

if __name__ == "__main__":
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    root_files = [current_dir / f for f in ["main.py", "run_web_server.py"] if (current_dir / f).exists()]
    
    # Fix src directory
    fixed_src = fix_line_endings(src_dir)
    
    # Fix root Python files
    fixed_root = 0
    for py_file in root_files:
        try:
            with open(py_file, 'rb') as f:
                content = f.read()
            
            if b'\r\n' in content:
                print(f"Fixing line endings: {py_file}")
                fixed_content = content.replace(b'\r\n', b'\n')
                
                with open(py_file, 'wb') as f:
                    f.write(fixed_content)
                
                fixed_root += 1
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    total_fixed = fixed_src + fixed_root
    print(f"✅ Total files fixed: {total_fixed}")
    
    if total_fixed > 0:
        print("Line ending fixes complete! This should resolve Windows import issues.")