---
name: deepsmile-clinic-video
description: 使用“让理解，走在矫正之前”定稿模板，为 DeepSmile 合作门诊生成品牌宣传视频；输入门诊名称和 Logo，自动生成晓晓旁白、字幕、高清成片、封面和母版。
---

使用仓库根目录中的 bootstrap.py 和 video.py。本技能根目录即完整项目目录。安装时复制完整仓库到技能目录，不能只复制本文件。

从用户请求取得门诊全称和 Logo 路径；已有信息不重复索要。所有门诊名称字样使用同一个输入，保留 Logo 原色比例。不要重写叙事或替换患者形象。

首次执行 `python bootstrap.py`（Windows 可用 `py -3`），随后：
`python video.py --name "某某口腔" --logo "/完整路径/logo.png" --allow-online-tts`

在线配音会向微软发送门诊名和公开宣传旁白。仅在用户已允许时添加 --allow-online-tts；未允许时说明发送内容并取得许可。不得发送 Logo、患者照片、报告或登录信息。使用 zh-CN-XiaoxiaoNeural，保持模板语速音调。服务失败应保留项目并报告，不换声线冒充完成。

先用 --stills 检查 Logo、长名称和结尾，再去掉该参数渲染。完成后返回实际成片路径。保留原稿、无 BGM 母版、字幕和关键帧。对于新门诊，只验证生成结果，不必重新让用户批准已确定的模板。

关键限制见根目录 AGENTS.md 和 ASSETS.md。禁止解除患者遮挡；所有生成物留在用户本地。
