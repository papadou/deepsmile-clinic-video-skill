import React from 'react';
import {Img,staticFile} from 'remotion';
export const ShotcraftMark:React.FC<{size?:number;tone?:string}>=({size=34})=><Img src={staticFile('images/deepsmile-logo-crop.png')} style={{width:size*2.6,height:'auto',objectFit:'contain'}}/>;
