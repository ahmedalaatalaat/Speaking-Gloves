from django.shortcuts import render
from django.http import StreamingHttpResponse
from .utils import *


def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')