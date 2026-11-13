from pathlib import Path
import json,wave,math,re
from PIL import Image
import sys
r=Path(sys.argv[1]).resolve(); j=json.loads((r/'source/story.json').read_text(encoding='utf-8'));start=0;shots=[];caps=[];raw=b''
for part in j:
 n=round(part['seconds']*30);shots.append({'id':part['id'],'from':start,'duration':n})
 with wave.open(str(r/'audio'/f"{part['id']}.wav"),'rb') as w: raw+=w.readframes(w.getnframes())
 for a,b,t in part['cues']:
  units=[];buf=''
  for c in t:
   buf+=c
   if (c in '，。？；：' and len(buf)>=7) or len(buf)>=22: units.append(buf);buf=''
  if buf:
   if units and len(buf)<5 and len(units[-1])+len(buf)<=23:units[-1]+=buf
   else:units.append(buf)
  total=sum(map(len,units));pos=a
  for u in units:
   z=pos+(b-a)*len(u)/total;caps.append({'from':start+round(pos*30),'duration':max(1,round((z-pos)*30)),'text':u});pos=z
 start+=n
with wave.open(str(r/'public/audio/voice.wav'),'wb') as w:w.setparams((1,2,48000,0,'NONE','not compressed'));w.writeframes(raw)
(r/'src/data.json').write_text(json.dumps({'total':start,'shots':shots,'captions':caps},ensure_ascii=False,indent=2),encoding='utf-8')
print('Frames',start,'Seconds',start/30)
