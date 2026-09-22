# 文旅数字人

讲解员阿青。游客自己填写想去的全国景点，可以打字，也可以按住说话。服务会生成讲解文字、语音和全身口型视频。

## 运行

在已安装 Linly-Talker、PyTorch、FFmpeg 和 Edge TTS 的环境里：

```bash
export DEEPSEEK_API_KEY=你的密钥
python wenlv_server.py
```

浏览器打开 `http://127.0.0.1:6006`。没有显卡时只返回语音。

密钥不要写进代码，用环境变量 `DEEPSEEK_API_KEY` 传入。
