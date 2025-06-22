from django.shortcuts import render, get_object_or_404
from .models import Academy, Offering


def academy_list(request):
    academies = Academy.objects.all()
    return render(request, 'academies/academy_list.html', {'academies': academies})


def academy_detail(request, pk):
    academy = get_object_or_404(Academy, pk=pk)
    offerings = academy.offerings.all()
    return render(request, 'academies/academy_detail.html', {
        'academy': academy,
        'offerings': offerings
    })


def offering_list(request):
    offerings = Offering.objects.select_related('academy').all()
    return render(request, 'academies/offering_list.html', {'offerings': offerings})
