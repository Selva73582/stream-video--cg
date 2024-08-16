import os
import subprocess
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .forms import VideoForm
from .models import Video

def handle_hls_conversion(file):
    # Paths
    video_path = os.path.join(settings.MEDIA_ROOT, file.name)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', os.path.splitext(file.name)[0])
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'index.m3u8')

    # Corrected ffmpeg command to convert video to HLS
    command = [
        'ffmpeg', '-i', video_path, '-c:v', 'copy', '-c:a', 'copy', 
        '-start_number', '0', '-hls_time', '10', '-hls_list_size', '0', 
        '-f', 'hls', output_file
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting video to HLS: {e}')
        return None

    # Correct the HLS URL by replacing backslashes with forward slashes
    hls_url = os.path.join(settings.MEDIA_URL, 'hls', os.path.splitext(file.name)[0], 'index.m3u8')
    hls_url = hls_url.replace('\\', '/')
    
    print(f'HLS URL: {hls_url}')  # Debugging line
    return hls_url

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.save()  # Save to generate file path

            # HLS conversion logic
            hls_url = handle_hls_conversion(video.file)
            if hls_url is None:
                # Handle error appropriately, e.g., show an error message
                return render(request, 'videoapp/upload.html', {'form': form, 'error': 'Error processing video'})

            # Update `hls_url` and save
            video.hls_url = hls_url
            video.save()

            return redirect('video_list')  # Redirect to the video list page or another page
    else:
        form = VideoForm()

    return render(request, 'videoapp/upload.html', {'form': form})

def video_list(request):
    videos = Video.objects.filter(is_active=True)
    return render(request, 'videoapp/video_list.html', {'videos': videos})

def play_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, is_active=True)
    print(f"Video HLS URL: {video.hls_url}")  # Debugging line
    return render(request, 'videoapp/video_play.html', {'video': video})
