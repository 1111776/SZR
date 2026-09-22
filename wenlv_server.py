# -*- coding: utf-8 -*-
"""
文旅数字人讲解服务
游客自己选景点 -> 阿青讲解 -> 语音 -> SadTalker 全身口型视频。
模型和无变化的人脸只在首次加载，后续提问复用。
"""
import asyncio
import os
import sys
import uuid

os.environ["PATH"] = "/root/miniconda3/bin:" + os.environ.get("PATH", "")

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

from flask import Flask, jsonify, request, send_from_directory

from LLM.DeepSeek import DeepSeek
from wenlv_config import GUIDE_NAME, SCENIC_NAME

app = Flask(__name__, static_folder="wenlv_web", static_url_path="")
llm = DeepSeek()

AUDIO_DIR = os.path.join(BASE, "wenlv_audio")
VIDEO_DIR = os.path.join(BASE, "wenlv_video")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

VOICE = os.environ.get("WENLV_VOICE", "zh-CN-XiaoxiaoNeural")
PORTRAIT = os.environ.get(
    "WENLV_PORTRAIT",
    os.path.join(BASE, "examples", "source_image", "full_body_1.png"),
)
MAX_Q = 200
MAX_PLACE = 40
MAX_TTS = 70
FPS = 12
_talker = None
_video_ok = None


async def _tts(text, path):
    import edge_tts
    comm = edge_tts.Communicate(text, VOICE)
    await comm.save(path)


def video_available():
    global _video_ok
    if _video_ok is None:
        try:
            import torch
            _video_ok = bool(torch.cuda.is_available())
        except Exception:
            _video_ok = False
    return _video_ok


def get_talker():
    global _talker
    if _talker is None:
        from TFG import SadTalker
        _talker = SadTalker(lazy_load=True)
        print("SadTalker 已加载")
    return _talker


def warmup():
    if not video_available():
        print("无显卡，跳过视频预热")
        return
    try:
        get_talker()
    except Exception as e:
        print("视频预热失败:", e)


def render_video(audio_path):
    if not video_available() or not os.path.isfile(PORTRAIT):
        return None
    raw = get_talker().test2(
        PORTRAIT, audio_path, "full", True, False, 1, 256, 0,
        "facevid2vid", 1, False, None, None, False, 0, True, FPS,
        result_dir=VIDEO_DIR,
    )
    if not raw or not os.path.isfile(raw):
        return None
    name = uuid.uuid4().hex + ".mp4"
    dest = os.path.join(VIDEO_DIR, name)
    os.replace(raw, dest)
    files = sorted(
        (os.path.join(VIDEO_DIR, f) for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")),
        key=os.path.getmtime,
    )
    for old in files[:-8]:
        try:
            os.remove(old)
        except OSError:
            pass
    return "/video/" + name


def synthesize(text):
    name = uuid.uuid4().hex + ".mp3"
    path = os.path.join(AUDIO_DIR, name)
    asyncio.run(_tts(text, path))
    files = sorted(
        (os.path.join(AUDIO_DIR, f) for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")),
        key=os.path.getmtime,
    )
    for old in files[:-30]:
        try:
            os.remove(old)
        except OSError:
            pass
    return "/audio/" + name


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/info")
def info():
    return jsonify({
        "scenic": SCENIC_NAME,
        "guide": GUIDE_NAME,
        "mode": "api" if llm.client is not None else "knowledge",
        "voice": VOICE,
        "video": video_available(),
        "portrait": "/portrait.png",
    })


@app.get("/portrait.png")
def portrait():
    folder, name = os.path.split(PORTRAIT)
    return send_from_directory(folder, name)


@app.post("/api/ask")
def ask():
    data = request.get_json(silent=True) or {}
    place = (data.get("place") or "").strip()[:MAX_PLACE]
    question = (data.get("question") or "").strip()
    if not place:
        return jsonify({"error": "请先填写想去的景点"}), 400
    if not question:
        return jsonify({"error": "请先说出或输入想听的内容"}), 400
    question = question[:MAX_Q]
    prompt = f"我想去{place}。{question}"
    answer = llm.generate(prompt, place=place)
    spoken = answer if len(answer) <= MAX_TTS else answer[:MAX_TTS]
    audio = None
    video = None
    wav_path = None
    try:
        audio = synthesize(spoken)
        wav_path = os.path.join(AUDIO_DIR, os.path.basename(audio))
    except Exception as e:
        print("语音合成失败:", e)
    if wav_path:
        try:
            video = render_video(wav_path)
        except Exception as e:
            print("视频生成失败:", e)
    return jsonify({
        "place": place,
        "question": question,
        "answer": answer,
        "audio": audio,
        "video": video,
        "mode": "api" if llm.client is not None else "knowledge",
    })


@app.get("/audio/<name>")
def audio(name):
    if not name.endswith(".mp3") or "/" in name or ".." in name:
        return jsonify({"error": "bad file"}), 400
    return send_from_directory(AUDIO_DIR, name)


@app.get("/video/<name>")
def video(name):
    if not name.endswith(".mp4") or "/" in name or ".." in name:
        return jsonify({"error": "bad file"}), 400
    return send_from_directory(VIDEO_DIR, name)


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("WENLV_PORT", "6006"))
    print(f"文旅讲解员已启动: http://0.0.0.0:{port}  范围={SCENIC_NAME}")
    warmup()
    app.run(host="0.0.0.0", port=port, threaded=False)
