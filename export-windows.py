import os
import sys
import shutil
import subprocess
from pathlib import Path
import time

def install_requirements():
    """Install all required packages with proper error handling"""
    packages = [
        'pip --upgrade',
        'pillow',
        'pyinstaller',
        'pyqt6',
        'requests',
        'pygments',
        'pyperclip',
        'qt-material'  # Using qt-material instead of qdarktheme
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            time.sleep(1)  # Give some time between installations
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            if package == 'pip --upgrade':
                continue  # Continue even if pip upgrade fails
            return False
    return True

def create_icon():
    """Create a custom icon for the application"""
    try:
        # First verify Pillow is installed
        subprocess.run([sys.executable, '-c', 'from PIL import Image, ImageDraw'], check=True)
    except subprocess.CalledProcessError:
        print("Retrying Pillow installation...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'pillow'], check=True)

    icon_content = """
from PIL import Image, ImageDraw
import os

# Create a new image with a transparent background
size = (256, 256)
icon = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(icon)

# Draw a green cyber-style circle
draw.ellipse([(20, 20), (236, 236)], fill=(0, 40, 0, 255), outline=(0, 255, 0, 255), width=3)

# Draw some "matrix-style" lines
for i in range(40, 216, 20):
    draw.line([(i, 40), (i, 216)], fill=(0, 255, 0, 128), width=2)
    
# Add some "cyber" dots
for x in range(50, 206, 40):
    for y in range(50, 206, 40):
        draw.ellipse([(x-3, y-3), (x+3, y+3)], fill=(0, 255, 0, 255))

# Save the icon in different sizes
if not os.path.exists('temp'):
    os.makedirs('temp')

icon.save('temp/wormgpt.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
"""

    # Create and run the icon generation script
    with open('create_icon.py', 'w', encoding='utf-8') as f:
        f.write(icon_content)
    
    try:
        subprocess.run([sys.executable, 'create_icon.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating icon: {e}")
        return False
    finally:
        if os.path.exists('create_icon.py'):
            os.remove('create_icon.py')
    return True

def create_version_info():
    """Create version info for the executable"""
    version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'WormGPT'),
         StringStruct(u'FileDescription', u'WormGPT Neural Interface'),
         StringStruct(u'FileVersion', u'2.0.0'),
         StringStruct(u'InternalName', u'wormgpt'),
         StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
         StringStruct(u'OriginalFilename', u'WormGPT.exe'),
         StringStruct(u'ProductName', u'WormGPT'),
         StringStruct(u'ProductVersion', u'2.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    try:
        with open('version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_info)
        return True
    except Exception as e:
        print(f"Error creating version info: {e}")
        return False

def create_spec_file():
    """Create a custom spec file for PyInstaller"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['wormgpt_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pygments.lexers',
        'pygments.formatters',
        'pygments.styles',
        'requests',
        'pyperclip',
        'qt_material'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add additional data files
a.datas += [('temp/wormgpt.ico', 'temp/wormgpt.ico', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WormGPT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='temp/wormgpt.ico',
    version='version_info.txt',
    uac_admin=False,
)

# Create the collection
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WormGPT'
)
"""
    try:
        with open('wormgpt.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        return True
    except Exception as e:
        print(f"Error creating spec file: {e}")
        return False

def find_pyinstaller():
    """Find PyInstaller executable path"""
    if sys.platform == "win32":
        pyinstaller_paths = [
            os.path.join(sys.prefix, 'Scripts', 'pyinstaller.exe'),
            os.path.join(sys.prefix, 'Scripts', 'pyinstaller'),
            'pyinstaller.exe',
            'pyinstaller'
        ]
    else:
        pyinstaller_paths = [
            os.path.join(sys.prefix, 'bin', 'pyinstaller'),
            'pyinstaller'
        ]

    for path in pyinstaller_paths:
        if os.path.exists(path):
            return path
        
    # If not found in standard locations, try to get it from pip
    try:
        import pkg_resources
        pyinstaller_path = pkg_resources.resource_filename('PyInstaller', '__main__.py')
        return f"{sys.executable} {pyinstaller_path}"
    except:
        return None

def main():
    print("🚀 Starting WormGPT Export Process...")
    
    # Install required packages
    print("📦 Installing required packages...")
    if not install_requirements():
        print("❌ Failed to install required packages. Please check your internet connection and try again.")
        return
    
    # Create temporary directory
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    # Create icon
    print("🎨 Creating application icon...")
    if not create_icon():
        print("❌ Failed to create icon. Continuing without custom icon...")
    
    # Create version info
    print("📝 Creating version information...")
    if not create_version_info():
        print("❌ Failed to create version information. Continuing without version info...")
    
    # Create spec file
    print("📋 Creating PyInstaller spec file...")
    if not create_spec_file():
        print("❌ Failed to create spec file. Aborting...")
        return
    
    # Find PyInstaller
    pyinstaller_path = find_pyinstaller()
    if not pyinstaller_path:
        print("❌ PyInstaller not found. Please make sure it's installed correctly.")
        return
    
    # Run PyInstaller
    print("🔨 Building executable...")
    try:
        if isinstance(pyinstaller_path, str) and ' ' in pyinstaller_path:
            # If it's a path with spaces, split into python and script
            python_exe, script_path = pyinstaller_path.split(' ', 1)
            subprocess.run([python_exe, script_path, 'wormgpt.spec', '--clean'], check=True)
        else:
            subprocess.run([pyinstaller_path, 'wormgpt.spec', '--clean'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build executable: {e}")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # Move the dist folder to output
    try:
        if os.path.exists('output/WormGPT'):
            shutil.rmtree('output/WormGPT')
        shutil.move('dist/WormGPT', 'output/WormGPT')
    except Exception as e:
        print(f"❌ Failed to move output files: {e}")
        return
    
    # Cleanup
    print("🧹 Cleaning up temporary files...")
    cleanup_paths = ['build', 'dist', 'temp', '__pycache__', 'version_info.txt', 'wormgpt.spec']
    for path in cleanup_paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            print(f"Warning: Could not remove {path}: {e}")
    
    print("""
✨ Export completed successfully! ✨

📁 The executable and required files are in the 'output/WormGPT' folder.
🎮 To run the application:
   1. Go to the 'output/WormGPT' folder
   2. Run 'WormGPT.exe'

⚠️ Important Notes:
- Keep all files in the WormGPT folder together
- Do not move the .exe file alone
- The application requires all supporting files to run

🔧 If you encounter any issues:
1. Make sure all required packages are installed
2. Check if antivirus is blocking the execution
3. Run the application as administrator if needed
""")

if __name__ == '__main__':
    main()
