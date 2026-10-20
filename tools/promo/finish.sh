#!/bin/bash
# finish.sh <dir> <name>: master.mp4 + audio.f32 + overlay.png -> Etsy (silent 16:9) and social (9:16 with sound)
d=$1; n=$2; mkdir -p /home/claude/promo/out
ffmpeg -y -loglevel error -f f32le -ar 48000 -ac 2 -i $d/audio.f32 -c:a pcm_s16le $d/audio.wav
ffmpeg -y -loglevel error -i $d/master.mp4 -t 14.9 -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -an -movflags +faststart "/home/claude/promo/out/$n Etsy.mp4"
ffmpeg -y -loglevel error -i $d/master.mp4 -i $d/audio.wav -loop 1 -i $d/overlay.png -filter_complex "[0:v]split[a][b];[a]scale=3414:1920,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.08[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2[m];[m][2:v]overlay=0:0:shortest=1[v]" -map "[v]" -map 1:a -t 15 -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "/home/claude/promo/out/$n Reels and TikTok.mp4"
