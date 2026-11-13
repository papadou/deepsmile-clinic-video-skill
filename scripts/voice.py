import asyncio, json, math, re, subprocess, sys, wave
from pathlib import Path
R=Path(sys.argv[1]).resolve()
S=R/'source'
S.mkdir(exist_ok=True)
T=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(T))
import imageio_ffmpeg
CLINIC=json.loads((R/'src/clinic.json').read_text(encoding='utf8'))['clinicName']
from shared.edge_tts_compat import stream_to_file
FF=Path(imageio_ffmpeg.get_ffmpeg_exe())
VOICE={'name':'zh-CN-XiaoxiaoNeural','rate':'+29%','pitch':'+2Hz'}
LINES=[
 ('opening',['矫正前，你想知道的，不只是牙齿能不能排齐。','更是：我的问题在哪里？矫正难不难？为什么推荐这个方案？']),
 ('intro',['在{clinic}，医生借助DeepSmile数智化诊断报告，带你把自己的情况看清楚。']),
 ('profile',['从侧貌分析，理解面部比例和唇齿关系；']),
 ('imaging',['结合全景片、侧位片的影像与指标，了解牙齿和颌骨的情况；']),
 ('dental',['再通过牙列分析，把拥挤、排列和咬合问题逐项呈现。']),
 ('connect',['这些发现放在一起，医生就能向你解释：你最在意的问题，和哪些因素有关。']),
 ('difficulty',['那我的情况，矫正起来难不难？','报告参考国家标准，标注病例难度、列出复杂因素。','让你听到的不只是“简单”或“复杂”，还能知道，具体难在哪里。']),
 ('plan',['理解了这些，再来听方案，就更容易明白。','医生会结合检查分析和你的改善期望，讲清楚：这个方案重点解决什么，为什么适合你，以及哪些地方需要提前沟通。']),
 ('decision',['从“医生建议我这样做”，到“我明白为什么这样做”。']),
 ('closing',['{clinic}，携手DeepSmile。','让理解，走在矫正之前。']),
]
def spoken(t): return t.replace('DeepSmile','Deep Smile').replace('正畸','正基').replace('数智化','数质化')
def clean(t): return re.sub(r'[^\w]','',t).lower()
async def main():
    for _,ls in LINES:
        for i,t in enumerate(ls): ls[i]=t.replace('{clinic}',CLINIC)
    (R/'audio').mkdir(exist_ok=True)
    parts=[spoken(p) for _,ls in LINES for p in ls]
    text='\n'.join(parts)
    p=R/'audio/晓晓-全新旁白.mp3'
    j=R/'audio/晓晓-词边界.json'
    if not (p.is_file() and j.is_file()):
        tmp=p.with_suffix('.partial')
        b=await stream_to_file(text,VOICE,tmp)
        assert tmp.stat().st_size>1000 and b
        tmp.replace(p)
        j.write_text(json.dumps({'voice':VOICE,'input':text,'words':b},ensure_ascii=False,indent=2),encoding='utf8')
    meta=json.loads(j.read_text(encoding='utf8'))
    assert meta['input']==text and meta['voice']==VOICE
    b=meta['words']
    expected=''.join(map(clean,parts))
    actual=''.join(clean(w['text']) for w in b)
    assert expected==actual,(expected,actual)
    marks=[]; k=0
    for w in b:
        nw=len(clean(w['text']))
        if nw: marks.append((k,k+nw,w['offset']/1e7,(w['offset']+w['duration'])/1e7))
        k+=nw
    raw=subprocess.check_output([str(FF),'-v','error','-i',str(p),'-f','s16le','-ar','48000','-ac','1','-'])
    # Keep the same voice, with only a small tempo adjustment if needed for a one-minute cut.
    tempo=1.0
    if abs(tempo-1)>.005:
        raw=subprocess.check_output([str(FF),'-v','error','-i',str(p),'-af',f'atempo={tempo},volume=1.1','-f','s16le','-ar','48000','-ac','1','-'])
    else: tempo=1
    idx=0; table=[]
    for key,ls in LINES:
        offsets=[]
        for ptext in ls:
            n=len(clean(spoken(ptext)))
            in_line=[w for w in marks if idx<=w[0]<idx+n]
            assert in_line and in_line[-1][1]==idx+n
            offsets.append((in_line[0][2]/tempo,in_line[-1][3]/tempo,ptext))
            idx+=n
        a=max(0,offsets[0][0]-.12)
        z=min(len(raw)/96000,offsets[-1][1]+.16)
        pre=.12; seconds=math.ceil((pre+z-a+.22)*5)/5
        pcm=b'\0'*int(pre*48000)*2+raw[round(a*48000)*2:round(z*48000)*2]
        with wave.open(str(R/'audio'/f'{key}.wav'),'wb') as f:
            f.setparams((1,2,48000,0,'NONE','not compressed'))
            f.writeframes(pcm.ljust(round(seconds*48000)*2,b'\0'))
        cue=[[max(0,b-a+pre-.045), min(seconds,e-a+pre+.12),s] for b,e,s in offsets]
        for left,right in zip(cue,cue[1:]): left[1]=min(left[1],right[0])
        table.append({'id':key,'seconds':seconds,'text':''.join(ls),'cues':cue})
    (S/'story.json').write_text(json.dumps(table,ensure_ascii=False,indent=2),encoding='utf8')
    print('VOICE READY',round(sum(s['seconds'] for s in table),2),tempo,flush=True)
asyncio.run(main())
