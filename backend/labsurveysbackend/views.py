from django.http import HttpResponse


def index(request):
    return HttpResponse("The backend is running successfully.")
