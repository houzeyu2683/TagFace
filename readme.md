TagFace

conda env create -f environment.yaml


#conda install -c conda-forge retina-face
#pip install tf-keras

conda install 1adrianb::face_alignment
conda install conda-forge::pytorch-ignite



https://www.youtube.com/watch?v=5gxjv9b7FWY&ab_channel=%E9%A2%A8%E5%82%B3%E5%AA%92TheStormMedia
https://www.youtube.com/watch?v=vnp9DyYgf1U&ab_channel=%E5%95%86%E6%A5%AD%E5%91%A8%E5%88%8A
https://www.youtube.com/watch?v=_V1NYVMWkiE&ab_channel=%E9%8F%A1%E6%96%B0%E8%81%9E
https://www.youtube.com/watch?v=0tNgi3YAbyE&ab_channel=%E4%B8%AD%E5%A4%A9%E6%96%B0%E8%81%9E
https://www.youtube.com/watch?v=kYEgOIHjWc0&ab_channel=%E9%8F%A1%E6%96%B0%E8%81%9E
https://www.youtube.com/watch?v=F2UEQqIvYtk&pp=0gcJCc0JAYcqIYzv

yt-dlp -f "bv[height=1080]+ba" --merge-output-format mp4 -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=5gxjv9b7FWY&ab_channel=%E9%A2%A8%E5%82%B3%E5%AA%92TheStormMedia"

yt-dlp -f "bv[height=1080]+ba" --merge-output-format mp4 -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=vnp9DyYgf1U&ab_channel=%E5%95%86%E6%A5%AD%E5%91%A8%E5%88%8A"

yt-dlp -f "bv[height=1080]+ba" --merge-output-format mp4 -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=_V1NYVMWkiE&ab_channel=%E9%8F%A1%E6%96%B0%E8%81%9E"

yt-dlp -f "bv[height=1080]+ba" --merge-output-format mp4 -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=0tNgi3YAbyE&ab_channel=%E4%B8%AD%E5%A4%A9%E6%96%B0%E8%81%9E"

yt-dlp -f "bv[height=1080]+ba" --merge-output-format mp4 -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=kYEgOIHjWc0&ab_channel=%E9%8F%A1%E6%96%B0%E8%81%9E"

yt-dlp -f "bv[height=1080]+ba" --merge-output-format mp4 -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=F2UEQqIvYtk&pp=0gcJCc0JAYcqIYzv"



yt-dlp -f "bv[height=1080]+ba" --merge-output-format mp4 -o "%(title)s.%(ext)s" ""

ffmpeg -i _V1NYVMWkiE.mp4 -t 00:01:00 -c copy _V1NYVMWkiE_1min.mp4

ffmpeg -i input.mp4 -r 25 output.mp4
