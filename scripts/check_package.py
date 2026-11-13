from pathlib import Path
import hashlib,json,sys
from PIL import Image
R=Path(__file__).resolve().parents[1]
def main():
 for name,box in [('profile-report-redacted.png',(42,60,400,170)),('profile-detail-redacted.png',(7,30,365,140))]:
  im=Image.open(R/'public/images'/name).convert('RGB')
  assert im.crop(box).getcolors(maxcolors=2)==[((box[2]-box[0])*(box[3]-box[1]),(24,43,64))],name
 for p in (R/'public').rglob('*'):
  if p.is_file():assert p.suffix.lower()!='.svg','Do not publish editable patient overlays'
 for relative,digest in json.loads((R/'scripts/asset-manifest.json').read_text(encoding='utf8')).items():
  p=R/relative
  if not p.exists() and p.suffix=='.otf':continue
  assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,relative
 assert '{clinic}' in (R/'scripts/voice.py').read_text(encoding='utf8')
 print('Package assets and flattened patient masks verified.')
if __name__=='__main__':main()
