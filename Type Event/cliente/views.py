from django.shortcuts import render, redirect
from eventos.models import Certificado, Evento
from django.contrib.auth.decorators import login_required


@login_required(login_url='/auth/login')
def meus_certificados(request):
    certificados = Certificado.objects.filter(participante__username = request.user)
    return render(request,'meus_certificados.html',{'certificados':certificados})