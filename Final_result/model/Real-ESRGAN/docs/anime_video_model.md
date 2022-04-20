# Anime Video Models

:white_check_mark: We add small models that are optimized for anime videos :-)

| Models                                                                                                                             | Scale | Description                    |
| ---------------------------------------------------------------------------------------------------------------------------------- | :---- | :----------------------------- |
| [RealESRGANv2-animevideo-xsx2](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.3.0/RealESRGANv2-animevideo-xsx2.pth) | X2    | Anime video model with XS size |
| [RealESRGANv2-animevideo-xsx4](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.3.0/RealESRGANv2-animevideo-xsx4.pth) | X4    | Anime video model with XS size |

- [Anime Video Models](#anime-video-models)
  - [How to Use](#how-to-use)
    - [PyTorch Inference](#pytorch-inference)
    - [ncnn Executable File](#ncnn-executable-file)
      - [Step 1: Use ffmpeg to extract frames from video](#step-1-use-ffmpeg-to-extract-frames-from-video)
      - [Step 2: Inference with Real-ESRGAN executable file](#step-2-inference-with-real-esrgan-executable-file)
      - [Step 3: Merge the enhanced frames back into a video](#step-3-merge-the-enhanced-frames-back-into-a-video)
  - [More Demos](#more-demos)

---

The following are some demos (best view in the full screen mode).

https://user-images.githubusercontent.com/17445847/145706977-98bc64a4-af27-481c-8abe-c475e15db7ff.MP4

https://user-images.githubusercontent.com/17445847/145707055-6a4b79cb-3d9d-477f-8610-c6be43797133.MP4

https://user-images.githubusercontent.com/17445847/145783523-f4553729-9f03-44a8-a7cc-782aadf67b50.MP4

## How to Use

### PyTorch Inference

```bash
# download model
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.3.0/RealESRGANv2-animevideo-xsx2.pth -P experiments/pretrained_models
# inference
python inference_realesrgan_video.py -i inputs/video/onepiece_demo.mp4 -n RealESRGANv2-animevideo-xsx2 -s 2 -v -a --half --suffix outx2
```

### ncnn Executable File

#### Step 1: Use ffmpeg to extract frames from video

```bash
ffmpeg -i onepiece_demo.mp4 -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 tmp_frames/frame%08d.png
```

- Remember to create the folder `tmp_frames` ahead

#### Step 2: Inference with Real-ESRGAN executable file

1. Download the latest portable [Windows](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.3.0/realesrgan-ncnn-vulkan-20211212-windows.zip) / [Linux](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.3.0/realesrgan-ncnn-vulkan-20211212-ubuntu.zip) / [MacOS](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.3.0/realesrgan-ncnn-vulkan-20211212-macos.zip) **executable files for Intel/AMD/Nvidia GPU**

1. Taking the Windows as example, run:

    ```bash
    ./realesrgan-ncnn-vulkan.exe -i tmp_frames -o out_frames -n RealESRGANv2-animevideo-xsx2 -s 2 -f jpg
    ```

    - Remember to create the folder `out_frames` ahead

#### Step 3: Merge the enhanced frames back into a video

1. First obtain fps from input videos by

    ```bash
    ffmpeg -i onepiece_demo.mp4
    ```

    ```console
    Usage:
    -i                   input video path
    ```

    You will get the output similar to the following screenshot.

    <p align="center">
        <img src="https://user-images.githubusercontent.com/17445847/145710145-c4f3accf-b82f-4307-9f20-3803a2c73f57.png">
    </p>

2. Merge frames

    ```bash
    ffmpeg -r 23.98 -i out_frames/frame%08d.jpg -c:v libx264 -r 23.98 -pix_fmt yuv420p output.mp4
    ```

    ```console
    Usage:
    -i                   input video path
    -c:v                 video encoder (usually we use libx264)
    -r                   fps, remember to modify it to meet your needs
    -pix_fmt             pixel format in video
    ```

    If you also want to copy audio from the input videos, run:

     ```bash
    ffmpeg -r 23.98 -i out_frames/frame%08d.jpg -i onepiece_demo.mp4 -map 0:v:0 -map 1:a:0 -c:a copy -c:v libx264 -r 23.98 -pix_fmt yuv420p output_w_audio.mp4
    ```

    ```console
    Usage:
    -i                   input video path, here we use two input streams
    -c:v                 video encoder (usually we use libx264)
    -r                   fps, remember to modify it to meet your needs
    -pix_fmt             pixel format in video
    ```

## More Demos

- Input video for One Piece:

    https://user-images.githubusercontent.com/17445847/145706822-0e83d9c4-78ef-40ee-b2a4-d8b8c3692d17.mp4

- Out video for One Piece

    https://user-images.githubusercontent.com/17445847/145706827-384108c0-78f6-4aa7-9621-99d1aaf65682.mp4

**More comparisons**

https://user-images.githubusercontent.com/17445847/145707458-04a5e9b9-2edd-4d1f-b400-380a72e5f5e6.MP4
