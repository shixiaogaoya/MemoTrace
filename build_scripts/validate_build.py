import sys
from pathlib import Path

TARGETS = {
    'pyinstaller': Path('dist_local') / 'MemoTrace.exe',
    'nuitka': Path('dist_nuitka') / 'MemoTrace.exe',
    'cxfreeze': Path('dist_cx_freeze') / 'MemoTrace' / 'MemoTrace.exe'
}


def check_file(path: Path):
    return path.exists() and path.stat().st_size > 0


def main():
    root = Path(__file__).parent.parent
    ok = True
    print('=== 构建产物校验 ===')
    for name, rel in TARGETS.items():
        p = root / rel
        if check_file(p):
            print(f'[OK] {name}: {p} ({p.stat().st_size/1024/1024:.1f} MB)')
        else:
            print(f'[FAIL] {name}: {p} 不存在或为空')
            ok = False
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
