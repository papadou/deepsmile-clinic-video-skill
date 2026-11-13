import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {Main,TOTAL} from './Main';
const Root=()=> <Composition id="DeepSmile" component={Main} width={1920} height={1080} fps={30} durationInFrames={TOTAL} defaultProps={{bgm:true}}/>;
registerRoot(Root);
