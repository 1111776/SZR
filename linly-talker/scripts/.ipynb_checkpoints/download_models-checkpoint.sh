#!/bin/bash

# 提示用户选择下载方式
echo "Please select a model download method:"
echo "请选择模型下载方式："
echo "1. Download from ModelScope (No resuming capability)"
echo "1. 从 ModelScope 下载（有断点续传功能）推荐"
# 记得先下载modelscope, pip install modelscope
echo "记得先下载modelscope, pip install modelsope"
echo "2. Download from Huggingface (With resuming capability)"
echo "2. 从 Huggingface 下载（有断点续传功能）"
echo "3. Download from Huggingface mirror site (Possibly faster)"
echo "3. 从 Huggingface 镜像站点下载（镜像可能快一点）"
read -p "Enter 1, 2, or 3 to choose a download method: " download_option



# 9. CosyVoice模型
# CosyVoice model
# Check if the CosyVoice checkpoints directory exists
if [ -d "checkpoints/CosyVoice_ckpt" ]; then
  # Create the CosyVoice/pretrained_models directory if it doesn't exist
  mkdir -p CosyVoice/pretrained_models
  
  # Move the CosyVoice-ttsfrd directory to the CosyVoice/pretrained_models directory
  mv checkpoints/CosyVoice_ckpt/CosyVoice-ttsfrd CosyVoice/pretrained_models
  
  # Check if the move operation was successful
  if [ $? -ne 0 ]; then
    echo "Failed to move CosyVoice-ttsfrd directory."
    echo "移动 CosyVoice-ttsfrd 目录失败。"
    exit 1
  fi

  # Unzip the resource.zip file inside the CosyVoice-ttsfrd directory
  unzip CosyVoice/pretrained_models/CosyVoice-ttsfrd/resource.zip -d CosyVoice/pretrained_models/CosyVoice-ttsfrd
  pip install CosyVoice/pretrained_models/CosyVoice-ttsfrd/ttsfrd-0.3.6-cp38-cp38-linux_x86_64.whl
  
  # Check if the unzip operation was successful
  if [ $? -ne 0 ]; then
    echo "Failed to unzip resource.zip."
    echo "解压 resource.zip 失败。"
    exit 1
    
  fi
else
  echo "Directory Kedreamix/Linly-Talker/checkpoints/CosyVoice_ckpt does not exist, cannot move CosyVoice model."
  echo "目录 Kedreamix/Linly-Talker/checkpoints/CosyVoice_ckpt 不存在，无法移动 CosyVoice 模型。"
  exit 1
fi

echo "All models have been successfully moved and are ready."
echo "所有模型已成功移动并准备就绪。"
