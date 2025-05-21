from django.http import JsonResponse

def baseinfo(request):
    data = {
        'app': 'Meine App',
        'version': '1.0',
        'status': 'OK',
    }
    return JsonResponse(data)