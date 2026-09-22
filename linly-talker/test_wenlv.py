# -*- coding: utf-8 -*-
"""
文旅数字人 全流程离线测试
链路: 讲解员LLM回答 -> EdgeTTS合成语音 -> SadTalker生成数字人视频
用法: python test_wenlv.py [游客问题] [讲解员形象图片路径]
"""
import sys, os, time
sys.path.append('/root/autodl-tmp/Linly-Talker')
os.chdir('/root/autodl-tmp/Linly-Talker')
import warnings
warnings.filterwarnings('ignore')

QUESTION = sys.argv[1] if len(sys.argv) > 1 else "故宫的开放时间是几点?门票怎么预约?"
IMAGE = sys.argv[2] if len(sys.argv) > 2 else 'inputs/girl.png'

print("=" * 60)
print(f"[1/3] 讲解员思考: {QUESTION}")
from LLM.DeepSeek import DeepSeek
llm = DeepSeek()
t0 = time.time()
answer = llm.generate(QUESTION)
print(f"      讲解员回答({time.time()-t0:.1f}s): {answer}")

print("[2/3] 合成讲解语音 (EdgeTTS 晓晓)")
from TTS import EdgeTTS
edgetts = EdgeTTS()
wav_path = 'wenlv_answer.wav'
edgetts.predict(answer, 'zh-CN-XiaoxiaoNeural', 0, 100, 0, wav_path, 'answer.vtt')
print(f"      语音已生成: {wav_path} ({os.path.getsize(wav_path)/1024:.0f} KB)")

print("[3/3] SadTalker 生成数字人讲解视频 (首次加载较慢)")
from TFG import SadTalker
talker = SadTalker(lazy_load=True)
t0 = time.time()
video = talker.test2(IMAGE, wav_path, 'crop', False, False, 2, 256, 0,
                     'facevid2vid', 1, False, None, False, 5, True, fps=25)
print(f"      视频生成完成({time.time()-t0:.0f}s): {video}")
print("=" * 60)
print("测试通过! 文旅数字人链路正常。")
