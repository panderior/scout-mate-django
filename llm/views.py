from django.shortcuts import render
from django.http import JsonResponse
import json

from .solar import ChatWithSolar

def hello(request):
    return render(request, "home.html")

def scout(request):
    return render(request, "scout.html")

def chat_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        answer = ChatWithSolar(user_message)

        return JsonResponse({"response": answer})

    return JsonResponse({"error": "Invalid request"}, status=400)