from pathlib import Path
import argparse,subprocess,sys,shutil,json,re,datetime,urllib.request,hashlib
R=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name');p.add_argument('--logo');p.add_argument('--output');p.add_argument('--resume');p.add_argument('--allow-online-tts',action='store_true');p.add_argument('--stills',action='store_true');a=p.parse_args()
 py=R/'.venv'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
 if not py.exists():raise SystemExit('Run bootstrap.py first.')
 # Always use the project interpreter, including when started with system Python.
 if Path(sys.executable).resolve()!=py.resolve():
  raise SystemExit(subprocess.call([str(py),str(__file__),*sys.argv[1:]]))
 from PIL import Image,ImageChops
 if a.resume:
  job=Path(a.resume).resolve()
  if not (job/'src/clinic.json').is_file():raise SystemExit('Not a generated project directory.')
 else:
  if not a.name or not a.logo:raise SystemExit('--name and --logo are required.')
  name=a.name.strip()
  if not 1<=len(name)<=32 or re.search(r'[\x00-\x1f<>:"/\\|?*{}]',name) or name.endswith('.') or name.upper() in ['CON','PRN','AUX','NUL']:raise SystemExit('Invalid clinic name (1–32 characters; no path/control characters).')
  logo=Path(a.logo).resolve()
  im=Image.open(logo);im.load();im=im.convert('RGBA')
  # Preserve coloured marks; remove only surrounding transparent/near-white margins.
  white=Image.new('RGBA',im.size,'white');white.alpha_composite(im)
  mask=ImageChops.difference(white.convert('RGB'),Image.new('RGB',im.size,'white')).convert('L').point(lambda v:255 if v>12 else 0)
  box=mask.getbbox()
  if not box:raise SystemExit('Logo contains no visible pixels.')
  if not a.allow_online_tts:raise SystemExit('Online narration needs --allow-online-tts: sends clinic name and fixed public script to Microsoft, not images.')
  base=Path('D:/门诊品牌视频') if sys.platform=='win32' and Path('D:/').exists() else R/'outputs'
  job=Path(a.output).resolve() if a.output else base/(name+'-理解篇-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
  job.mkdir(parents=True,exist_ok=False)
  for folder in ['src','public']:shutil.copytree(R/folder,job/folder)
  for folder in ['renders','master','qa','audio','source','inputs']:(job/folder).mkdir()
  shutil.copy2(logo,job/'inputs'/logo.name)
  im.crop(box).save(job/'public/images/clinic-logo-original-crop.png')
  (job/'src/clinic.json').write_text(json.dumps({'clinicName':name},ensure_ascii=False),encoding='utf8')
 # Resume can reuse already prepared audio without network consent; regeneration still needs consent.
 if not (job/'public/audio/voice.wav').exists():
  if not a.allow_online_tts:raise SystemExit('Audio generation requires --allow-online-tts.')
  subprocess.run([str(py),str(R/'scripts/voice.py'),str(job)],check=True)
  subprocess.run([str(py),str(R/'scripts/prepare.py'),str(job)],check=True)
 bgm=job/'public/audio/bgm.mp3'
 if not bgm.exists():
  tmp=bgm.with_suffix('.partial')
  with urllib.request.urlopen('https://assets.mixkit.co/music/371/371.mp3',timeout=60) as response:tmp.write_bytes(response.read())
  if hashlib.sha256(tmp.read_bytes()).hexdigest()!='e241cba000ce12e52cadd4c9956274e391ef1f66d1e48a5dd40bfc21645aa489':raise RuntimeError('BGM changed; verify source and license before updating checksum.')
  tmp.replace(bgm)
 node=shutil.which('node')
 if not node:raise SystemExit('Node.js missing from PATH.')
 subprocess.run([node,str(R/'scripts/render.mjs'),str(job),*(['--stills'] if a.stills else [])],cwd=R,check=True)
 print(str(job))
if __name__=='__main__':main()
