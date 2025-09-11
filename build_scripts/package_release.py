import shutil
import hashlib
from pathlib import Path
from memotrace_version import __version__, __app_name__

root = Path(__file__).parent.parent
release_dir = root / 'release'
release_dir.mkdir(exist_ok=True)

artifacts = [
    ('pyinstaller', root / 'dist_local'),
    ('nuitka', root / 'dist_nuitka' / 'MemoTrace.exe'),
    ('cxfreeze', root / 'dist_cx_freeze' / 'MemoTrace'),
]

generated = []
for name, path in artifacts:
    if not path.exists():
        print(f'[跳过] {name} 未找到: {path}')
        continue
    if path.is_file():
        target = release_dir / f'{__app_name__}-{__version__}-{name}.exe'
        shutil.copy2(path, target)
        generated.append(target)
        print(f'[复制] {target}')
    else:
        zip_name = release_dir / f'{__app_name__}-{__version__}-{name}'
        if (zip_name.with_suffix('.zip')).exists():
            (zip_name.with_suffix('.zip')).unlink()
        shutil.make_archive(str(zip_name), 'zip', path)
        archive = zip_name.with_suffix('.zip')
        generated.append(archive)
        print(f'[压缩] {archive}')

# 生成 sha256 校验文件
hash_file = release_dir / f'SHA256SUMS-{__version__}.txt'
with hash_file.open('w', encoding='utf-8') as f:
    for file_path in generated:
        h = hashlib.sha256()
        with open(file_path, 'rb') as rf:
            for chunk in iter(lambda: rf.read(1024 * 1024), b''):
                h.update(chunk)
        f.write(f"{h.hexdigest()}  {file_path.name}\n")
print(f'[校验] 写入 {hash_file}')
print('完成归档')
