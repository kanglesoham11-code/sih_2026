"""
Quick Setup Test Script
Run this to check if everything is configured correctly
"""

import sys
import subprocess
from pathlib import Path

def test_python():
    """Test Python version"""
    print("🐍 Testing Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version OK")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def test_docker():
    """Test Docker"""
    print("\n🐳 Testing Docker...")
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            containers = result.stdout.count('orca-')
            print(f"   ✅ Docker running ({containers} ORCA containers)")
            return True
        else:
            print("   ❌ Docker not responding")
            return False
    except FileNotFoundError:
        print("   ❌ Docker not installed")
        return False

def test_env_file():
    """Test .env file"""
    print("\n📄 Testing .env file...")
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        content = env_path.read_text()
        has_groq = 'GROQ_API_KEY' in content
        has_copernicus = 'hershey' in content
        has_mosdac = 'godsplan' in content
        
        print(f"   ✅ .env file exists")
        print(f"   {'✅' if has_groq else '❌'} Groq API key configured")
        print(f"   {'✅' if has_copernicus else '❌'} Copernicus credentials")
        print(f"   {'✅' if has_mosdac else '❌'} MOSDAC credentials")
        return True
    else:
        print("   ❌ .env file not found")
        return False

def test_directories():
    """Test directory structure"""
    print("\n📁 Testing directory structure...")
    required = ['backend', 'frontend', 'docs', 'scripts']
    all_exist = True
    for dir_name in required:
        dir_path = Path(__file__).parent / dir_name
        exists = dir_path.exists()
        print(f"   {'✅' if exists else '❌'} {dir_name}/")
        all_exist = all_exist and exists
    return all_exist

def test_backend_files():
    """Test backend files"""
    print("\n📦 Testing backend files...")
    backend = Path(__file__).parent / 'backend'
    required = ['app', 'requirements.txt', 'alembic.ini']
    all_exist = True
    for name in required:
        path = backend / name
        exists = path.exists()
        print(f"   {'✅' if exists else '❌'} {name}")
        all_exist = all_exist and exists
    return all_exist

def main():
    print("=" * 50)
    print("   ORCA Setup Test")
    print("=" * 50)
    
    results = [
        test_python(),
        test_docker(),
        test_env_file(),
        test_directories(),
        test_backend_files(),
    ]
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("\nYou're ready to start ORCA!")
        print("\nNext steps:")
        print("1. cd backend")
        print("2. python -m venv venv")
        print("3. venv\\Scripts\\activate.bat")
        print("4. pip install -r requirements.txt")
        print("5. alembic upgrade head")
        print("6. python scripts\\init_database.py")
        print("7. uvicorn app.main:app --reload")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above and try again.")
    print("=" * 50)

if __name__ == '__main__':
    main()
