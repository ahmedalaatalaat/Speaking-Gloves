from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators import gzip
from django.shortcuts import render
# from .utils2 import *
from .utils import *


def video_feed(request):
    return render(request, "live_detect/camera.html")
    # return StreamingHttpResponse(gen_frames(VideoCamera()), content_type='multipart/x-mixed-replace; boundary=frame')


def home(request):
    # try:
    #     return StreamingHttpResponse(gen_frames2(), content_type='multipart/x-mixed-replace; boundary=frame')
    # except:
    #     pass
    return HttpResponse("<h1>Error</h1>")

def index(request):
    return render(request, "live_detect/index.html")


def room(request, room_name):
    return render(request, "live_detect/room.html", {"room_name": room_name})