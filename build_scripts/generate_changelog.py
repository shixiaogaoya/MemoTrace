import subprocess
import re
from pathlib import Path
from datetime import datetime
from memotrace_version import __version__, __app_name__

root = Path(__file__).parent.parent
changelog = root / 'CHANGELOG.md'

# 获取 git tag 与提交日志
try:
    log = subprocess.check_output([
        'git', 'log', '--pretty=format:%H||%ad||%s', '--date=short'
    ], cwd=root, encoding='utf-8', errors='ignore')
except Exception as e:
    print(f'[WARN] 读取 git 日志失败: {e}')
    log = ''

lines = log.splitlines()
entries = []
for line in lines[:400]:  # 限制长度
    parts = line.split('||', 2)
    if len(parts) != 3:
        continue
    commit, date, subject = parts
    if subject.startswith('Merge pull request'):
        continue
    entries.append((date, commit[:7], subject))

section_lines = [
    f"## v{__version__} - {datetime.utcnow().strftime('%Y-%m-%d')}\n",
    '\n',
]
if not entries:
    section_lines.append('- 更新日志自动生成：无可用提交或未检索到 git 历史\n')
else:
    for date, short, subject in entries[:50]:
        section_lines.append(f"- {subject} ({short}, {date})\n")
section = ''.join(section_lines)

if changelog.exists():
    old = changelog.read_text(encoding='utf-8')
    if section.splitlines()[0] in old:
        print('[信息] 当前版本条目已存在，跳过追加')
    else:
        changelog.write_text(section + '\n' + old, encoding='utf-8')
        print('[生成] 已追加新版本 CHANGELOG 条目')
else:
    header = f"# {__app_name__} 更新日志\n\n" + section
    changelog.write_text(header, encoding='utf-8')
    print('[生成] 创建新的 CHANGELOG.md')
