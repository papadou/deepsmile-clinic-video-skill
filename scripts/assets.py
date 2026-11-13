"""Fetch large font files with pinned hashes; music is fetched per local job."""
from pathlib import Path
import json,hashlib,urllib.request
def ensure_assets(root):
 manifest=json.loads((root/'scripts/downloads.json').read_text(encoding='utf8'))
 for item in manifest:
  p=root/item['path']
  if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']:continue
  p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.partial')
  with urllib.request.urlopen(item['url'],timeout=120) as response:tmp.write_bytes(response.read())
  if hashlib.sha256(tmp.read_bytes()).hexdigest()!=item['sha256']:
   tmp.unlink(missing_ok=True);raise RuntimeError('Downloaded asset changed: '+item['path'])
  tmp.replace(p)
if __name__=='__main__':ensure_assets(Path(__file__).resolve().parents[1])
