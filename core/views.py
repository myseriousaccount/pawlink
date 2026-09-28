from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html',context={
        'title': 'Головна',
        'page': 'home',
        'app': 'core'
    })

def about(request):
    return render(request, 'core/about.html',context={
        'title': 'Про нас',
        'page': 'about',
        'app': 'core'
    })


def contacts(request):
    return render(request, 'core/contacts.html',context={
        'title': 'Контакти',
        'page': 'contacts',
        'app': 'core'
    })
