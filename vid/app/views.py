from asyncio import streams
from fileinput import filename
from multiprocessing import context
from django.shortcuts import redirect, render
# Import mimetypes module
import mimetypes
from os import startfile
# import os module
import os
from django.http.response import HttpResponse
from wsgiref.util import FileWrapper
from pytube import YouTube
from moviepy.editor import *

import time
from django.views.generic import View
# Create your views here.

def index(request):
    context = {"title":"" , "audio":[] , 'video':[] ,"url":""}
    if request.method == "POST":
        if request.POST['down'] != "download":
            url_name =request.POST['urlname']
            context['url'] = url_name
            yt = YouTube(url_name)
            for x in yt.streams.filter(mime_type="video/mp4" ,progressive=False):
                print(x)
                # print(str(x).split(" ")[3].split('res="')[1].split('"')[0])
                context['video'].append(str(x).split(" ")[3].split('res="')[1].split('"')[0])
            for y in yt.streams.filter(type="audio" , mime_type="audio/mp4"):
                audiokb = str(y).split(" ")[3].split('abr="')[1].split('"')[0]
                context['audio'].append(audiokb)
            context['title'] = yt._title
            context['video'] = [*set(context['video'])]
            print(request.POST['urlname'])
            print(context['video'])
            return render(request , 'app/home.html' , context)
        # else:
        #     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        #     url_name =request.POST['url']
        #     yt = YouTube(url_name)
        #     download_yt = yt.streams.filter(res = f"{request.POST['quality']}" ,mime_type="video/mp4")
        #     # for x in download_yt:
        #         # print(x)
        #     download_yt.first().download(BASE_DIR+R"\app\files")
        #     print("QUALITY VIDEO:   " , f"{request.POST['quality']}")
            
        #     time.sleep(4)

        #     path = FileWrapper(open(BASE_DIR+fR"\app\files\{yt._title}.mp4" , 'rb'))
        #     response = HttpResponse(path, content_type='application/vnd.mp4')
        #     response['Content-Disposition'] = f"attachment; filename={yt._title}.mp4"
        #     return response

    return render(request , 'app/home.html' ,context)

class home(View):
    def __init__(self,url=None):
        self.url = url
    def get(self,request):
        return render(request,'app/home.html') 

    def post(self,request):
        # for fetching the video
        if request.POST.get('fetch-vid'):
            self.url = request.POST.get('given_url')
            video = YouTube(self.url)
            vidTitle,vidThumbnail = video.title,video.thumbnail_url
            qual,stream = [],[]
            for vid in video.streams.filter(progressive=True):
                qual.append(vid.resolution)
                stream.append(vid)
            context = {'vidTitle':vidTitle,'vidThumbnail':vidThumbnail,
                        'qual':qual,'stream':stream,
                        'url':self.url}
            return render(request,'app/home.html',context)

        # for downloading the video
        elif request.POST.get('download-vid'):
            self.url = request.POST.get('given_url')
            video = YouTube(self.url)
            stream = [x for x in video.streams.filter(progressive=True)]
            video_qual = video.streams[int(request.POST.get('download-vid')) - 1]
            video_qual.download(output_path='../../Downloads')
            return redirect('home')

        return render(request,'app/home.html')

def viddownload(request):
    if request.method == "POST":
        if request.POST['format'] == "video":
                
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            url_name =request.POST['url']
            yt = YouTube(url_name)
            download_yt = yt.streams.filter(res = f"{request.POST['quality']}" ,mime_type="video/mp4")
                    # for x in download_yt:
                        # print(x)
            new_title = str(yt._title).replace('"' ,'')
            print("DOWNLOADING")
            down = download_yt.first().download(output_path = BASE_DIR+R"\app\files" , filename = f"{new_title}.mp4")
            print("QUALITY VIDEO:   " , f"{request.POST['quality']}")
            print("title:   " , yt._title)
            print("DOWNLOADED")
            if request.POST['quality'] in ['720p' ,'360p' ,'480p' ,'240p', '144p']:
            # time.sleep(4)
                path = FileWrapper(open(down , 'rb'))
                # path = FileWrapper(open(BASE_DIR+fR"\app\files\{new_title}.mp4" , 'rb'))
                response = HttpResponse(path, content_type='application/vnd.mp4')
                response['Content-Disposition'] = f"attachment; filename={yt._title}.mp4"
                return response
            else:
                print("MERGING")
                # new_title = str(yt._title).replace('"' ,'')
                download_at = yt.streams.filter(type="audio").order_by("abr").desc()
                audio_down = download_at.first().download(output_path = BASE_DIR+R"\app\files" , filename = f"{new_title}.mp3" )


                audioclip = AudioFileClip(BASE_DIR+fR"\app\files\{new_title}.mp3")
                videoclip = VideoFileClip(BASE_DIR+fR"\app\files\{new_title}.mp4")

                mergeclip = videoclip.set_audio(audioclip)
                mergeclip.write_videofile(BASE_DIR+fR"\app\files\{new_title}merge.mp4")
                print("MERGED")

                path = FileWrapper(open(BASE_DIR+fR"\app\files\{new_title}merge.mp4" , 'rb'))
                # path = FileWrapper(open(BASE_DIR+fR"\app\files\{new_title}.mp4" , 'rb'))
                response = HttpResponse(path, content_type='application/vnd.mp4')
                response['Content-Disposition'] = f"attachment; filename={yt._title}.mp4"
                return response

        else:
            print("DOWNLOADING AUDIO")
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            url_name =request.POST['url']
            yt = YouTube(url_name)
            download_yt = yt.streams.filter(abr = f"{request.POST['quality']}" ,mime_type="audio/mp4")
                    # for x in download_yt:
                        # print(x)
            new_title = str(yt._title).replace('"' ,'')
            down = download_yt.first().download(output_path = BASE_DIR+R"\app\files" , filename = f"{new_title}.mp3")
            # print("QUALITY VIDEO:   " , f"{request.POST['quality']}")
            # print("title:   " , yt._title)
            print("AUDIO DOWNLOADED")
            # time.sleep(4)
            path = FileWrapper(open(down , 'rb'))
            # path = FileWrapper(open(BASE_DIR+fR"\app\files\{new_title}.mp4" , 'rb'))
            response = HttpResponse(path, content_type='application/audio.mp3')
            response['Content-Disposition'] = f"attachment; filename={yt._title}.mp3"
            return response


def download(request):
    
 
    # Define Django project base directory
    # Define text file name

    # video = YouTube('https://www.youtube.com/watch?v=jNQXAC9IVRw')
    # stream = [x for x in video.streams.filter(progressive=True)]
    # video_qual = video.streams[int(request.POST.get('download-vid')) - 1]
    # video.streams.filter(progressive=True , file_extension='mp4').order_by('resolution').desc().first().download()
    # download_path = download_yt.download(BASE_DIR+R"\app\files")
    # print("file name:  " , yt._title)
    # filename = 'test.txt'
    # Define the full file path
    # filepath = BASE_DIR + '/app/files/' + filename
    # Open the file for reading content
    # path = open(BASE_DIR+R"\app\files\""+yt._title+".mp4", 'rb')

    # path = FileWrapper(open(BASE_DIR+fR"\app\files\Me at the zoo.mp4" , 'rb'))

    # print(BASE_DIR+R"\app\files"+yt._title)






    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yt = YouTube('https://www.youtube.com/watch?v=jNQXAC9IVRw')
    download_yt = yt.streams.filter(progressive=True , file_extension='mp4').order_by('resolution').desc().first()
    time.sleep(4)
    path_str = BASE_DIR+fR"\app\files\{yt._title}.mp4"
    path = FileWrapper(open(BASE_DIR+fR"\app\files\{yt._title}.mp4" , 'rb'))
    print("PATHHHH:   " ,path_str)
    mime_type, _ = mimetypes.guess_type(path_str)
    print("EXTENSION:  " ,_)
    response = HttpResponse(path, content_type='application/vnd.mp4')
    response['Content-Disposition'] = f"attachment; filename={yt._title}.mp4"
    return response





    # path = startfile(download_path)
    # Set the mime type
    # Set the return value of the HttpResponse
    # Set the HTTP header for sending to browser
    # Return the response value


