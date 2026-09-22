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

## 算力云上的原始项目

`linly-talker/` 是算力云上 Linly-Talker 的代码，来源是 [Kedreamix/Linly-Talker](https://github.com/Kedreamix/Linly-Talker)，许可证是 MIT。

这里只放了代码。模型权重没有放进来，因为单个体积就超过 GitHub 的 100MB 限制，全部大约 20GB。没有放进来的目录包括 `checkpoints`、`Qwen`、`Musetalk`、`FunASR`、`GPT_SoVITS`、`CosyVoice`、`gfpgan`、`Whisper`、`NeRF`。密钥、证书和生成出来的语音视频也没有放进来。

这些代码要配上对应的模型权重才能在算力云上跑起来。文旅讲解实际使用的是仓库根目录的 `wenlv_server.py`。
