import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const job=path.resolve(process.argv[2]);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
// Resolve dependencies from this installation, never from a previous local project.
const serveUrl=await bundle({entryPoint:path.join(job,'src/index.tsx'),publicDir:path.join(job,'public'),webpackOverride:c=>({...c,resolve:{...c.resolve,modules:[path.join(root,'node_modules'),'node_modules']}})});
const chrome=process.env.CHROME_PATH;
const browserExecutable=chrome||['C:/Program Files/Google/Chrome/Application/chrome.exe','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/usr/bin/google-chrome','/usr/bin/chromium'].find(p=>fs.existsSync(p));
const opts={serveUrl,id:'DeepSmile',browserExecutable};
const composition=await selectComposition(opts);
const clinic=JSON.parse(fs.readFileSync(path.join(job,'src/clinic.json'),'utf8')).clinicName;
const data=JSON.parse(fs.readFileSync(path.join(job,'src/data.json'),'utf8'));
for(const s of data.shots){const frame=s.from+Math.min(s.duration-1,Math.max(60,Math.floor(s.duration*.7)));await renderStill({serveUrl,composition,browserExecutable,frame,output:path.join(job,'qa',s.id+'.png')});}
await renderStill({serveUrl,composition,browserExecutable,frame:60,output:path.join(job,'renders','封面.png')});
const srt=data.captions.map((c,i)=>{const stamp=f=>{const ms=Math.round(f/30*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`};return `${i+1}\n${stamp(c.from)} --> ${stamp(c.from+c.duration)}\n${c.text}\n`}).join('\n');
fs.writeFileSync(path.join(job,'renders','字幕.srt'),srt);
if(!process.argv.includes('--stills')){
 for(const bgm of [true,false]){let last=-1;await renderMedia({serveUrl,composition,browserExecutable,inputProps:{bgm},codec:'h264',crf:17,concurrency:2,outputLocation:path.join(job,bgm?'renders':'master',`DeepSmile-合作视频-${clinic}${bgm?'':'-无BGM母版'}.mp4`),onProgress:p=>{let n=Math.floor(p.progress*100);if(n>=last+10){last=n;console.log(`${bgm?'final':'master'} ${n}%`)}}});}
}
fs.writeFileSync(path.join(job,'renders','制作记录.json'),JSON.stringify({clinicName:clinic,width:1920,height:1080,fps:30,duration:composition.durationInFrames/30,templateVersion:'1.0.0',voice:'zh-CN-XiaoxiaoNeural',rate:'+29%',pitch:'+2Hz'},null,2));
