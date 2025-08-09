#!/usr/bin/env python3
"""
Build script for yt-dlp-proxy binary
Creates a standalone executable using PyInstaller
Cross-platform support for Windows and Linux
"""

import os
import sys
import subprocess
import shutil
import platform
import venv
from pathlib import Path

def run_command(command, description, shell=True, check=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Error: {description}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            sys.exit(1)
        print(f"✅ {description} completed")
        return result.stdout
    except Exception as e:
        print(f"❌ Exception: {description} - {e}")
        if check:
            sys.exit(1)
        return None

def get_platform_info():
    """Get platform-specific information"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        python_exe = "python"
        pip_exe = "pip"
        venv_python = "Scripts\\python.exe"
        venv_pip = "Scripts\\pip.exe"
        binary_name = "yt-dlp-proxy.exe"
        upx_available = False  # UPX may not be available on Windows
    else:  # Linux/Unix
        python_exe = "python3"
        pip_exe = "pip3"
        venv_python = "bin/python"
        venv_pip = "bin/pip"
        binary_name = "yt-dlp-proxy"
        upx_available = True
    
    return {
        "system": system,
        "machine": machine,
        "python_exe": python_exe,
        "pip_exe": pip_exe,
        "venv_python": venv_python,
        "venv_pip": venv_pip,
        "binary_name": binary_name,
        "upx_available": upx_available
    }

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    dirs_to_clean = ['build', 'dist', '__pycache__', 'venv', '.venv']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            file_path.unlink()
            print(f"  Removed {file_path}")

def create_venv():
    """Create a virtual environment"""
    print("🐍 Creating virtual environment...")
    venv_path = "venv"
    
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
    
    venv.create(venv_path, with_pip=True)
    print(f"✅ Virtual environment created at {venv_path}")

def get_venv_python_path(platform_info):
    """Get the path to Python executable in virtual environment"""
    return os.path.join("venv", platform_info["venv_python"])

def get_venv_pip_path(platform_info):
    """Get the path to pip executable in virtual environment"""
    return os.path.join("venv", platform_info["venv_pip"])

def install_dependencies(platform_info):
    """Install required dependencies in virtual environment"""
    print("📦 Installing dependencies...")
    
    venv_python = get_venv_python_path(platform_info)
    venv_pip = get_venv_pip_path(platform_info)
    
    # Upgrade pip
    run_command(f'"{venv_python}" -m pip install --upgrade pip', "Upgrading pip")
    
    # Install PyInstaller
    run_command(f'"{venv_pip}" install pyinstaller', "Installing PyInstaller")
    
    # Install project dependencies
    run_command(f'"{venv_pip}" install -r requirements.txt', "Installing project dependencies")

def create_spec_file(platform_info):
    """Create PyInstaller spec file"""
    print("📝 Creating PyInstaller spec file...")
    
    # Platform-specific settings
    if platform_info["system"] == "windows":
        console_setting = "console=True"
        upx_setting = "upx=False"  # Disable UPX on Windows
    else:
        console_setting = "console=True"
        upx_setting = "upx=True" if platform_info["upx_available"] else "upx=False"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('proxy_providers', 'proxy_providers'),
        ('proxy_provider.py', '.'),
    ],
    hiddenimports=[
        'proxy_providers.onworks_provider',
        'proxy_providers.sandvpn_provider', 
        'proxy_providers.vnnet_provider',
        'proxy_provider',
        'requests',
        'tqdm',
        'concurrent.futures',
        'importlib',
        'inspect',
        'json',
        'os',
        'sys',
        'subprocess',
        'time',
        'io',
        'random'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{platform_info["binary_name"]}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    {upx_setting},
    upx_exclude=[],
    runtime_tmpdir=None,
    {console_setting},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('yt-dlp-proxy.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Spec file created")

def build_binary(platform_info):
    """Build the binary using PyInstaller"""
    print("🔨 Building binary...")
    
    venv_python = get_venv_python_path(platform_info)
    
    # Build using the spec file
    run_command(f'"{venv_python}" -m PyInstaller yt-dlp-proxy.spec', "Building binary with PyInstaller")
    
    # Make the binary executable (Linux only)
    if platform_info["system"] != "windows":
        binary_path = f"dist/{platform_info['binary_name']}"
        if os.path.exists(binary_path):
            os.chmod(binary_path, 0o755)
            print(f"✅ Binary created: {binary_path}")
            print(f"📏 Binary size: {os.path.getsize(binary_path) / (1024*1024):.2f} MB")
        else:
            print("❌ Binary not found after build")
    else:
        binary_path = f"dist/{platform_info['binary_name']}"
        if os.path.exists(binary_path):
            print(f"✅ Binary created: {binary_path}")
            print(f"📏 Binary size: {os.path.getsize(binary_path) / (1024*1024):.2f} MB")
        else:
            print("❌ Binary not found after build")

def main():
    """Main build process"""
    print("🏗️  Starting yt-dlp-proxy build process...")
    print("=" * 50)
    
    # Get platform information
    platform_info = get_platform_info()
    print(f"🖥️  Platform: {platform_info['system']} ({platform_info['machine']})")
    
    # Clean previous builds
    clean_build()
    
    # Create virtual environment
    create_venv()
    
    # Install dependencies
    install_dependencies(platform_info)
    
    # Create spec file
    create_spec_file(platform_info)
    
    # Build binary
    build_binary(platform_info)
    
    print("=" * 50)
    print("🎉 Build completed successfully!")
    print("")
    print("📁 Files created:")
    print(f"  - dist/{platform_info['binary_name']} (executable binary)")
    print("")
    print("📋 Next steps:")
    print(f"  1. Test the binary: ./dist/{platform_info['binary_name']} --help")
    if platform_info["system"] == "windows":
        print("  2. Install system-wide: Run 'make install' as Administrator")
    else:
        print("  2. Install system-wide: sudo make install")
    print("  3. Or manually copy the binary to a directory in your PATH")

if __name__ == "__main__":
    main() 