"""Install dependencies locally; no global Python/site-package changes."""
from pathlib import Path
import subprocess,sys,shutil,venv
R=Path(__file__).resolve().parent
def main():
 if sys.version_info<(3,10): raise SystemExit('Python 3.10+ required')
 node=shutil.which('node');npm=shutil.which('npm.cmd' if sys.platform=='win32' else 'npm')
 if not node or not npm: raise SystemExit('Install Node.js 20.9+ and reopen terminal.')
 version=subprocess.check_output([node,'--version'],text=True).strip().lstrip('v')
 if tuple(map(int,version.split('.')[:2]))<(20,9):raise SystemExit('Node.js 20.9+ required')
 env=R/'.venv'
 if not env.exists():venv.EnvBuilder(with_pip=True).create(env)
 py=env/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
 subprocess.run([str(py),'-m','pip','install','-r',str(R/'requirements.txt')],check=True)
 subprocess.run([npm,'ci' if (R/'package-lock.json').exists() else 'install'],cwd=R,check=True)
 subprocess.run([str(py),str(R/'scripts/assets.py')],check=True)
 print('Environment ready. Run video.py with clinic name and logo.')
if __name__=='__main__':main()
