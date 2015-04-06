from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, render


# views for index page
def index(request):
    return render(request, 'pages/nc_tools.html')
