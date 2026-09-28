from django.shortcuts import render

def shelters_list(request):
    return render(request, 'shelters/shelters.html',context={
        'title': 'Притулки',
        'page': 'shelters',
        'app': 'shelters'
    })
