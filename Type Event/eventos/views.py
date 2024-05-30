from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Evento
from django.urls import reverse

@login_required(login_url='/auth/login/')
def novo_evento(request):
    if request.method == "GET":
        return render(request, 'novo_evento.html')
    
    if request.method == "POST":
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_termino = request.POST.get('data_termino')
        carga_horaria = request.POST.get('carga_horaria')
        logo = request.FILES.get('logo')

        cor_principal = request.POST.get('cor_principal')
        cor_secundaria = request.POST.get('cor_secundaria')
        cor_fundo = request.POST.get('cor_fundo')


        if len(nome.strip()) == 0 or len(descricao.strip()) == 0 or len(data_inicio.strip()) == 0 or  len(data_termino.strip()) == 0 or  len(carga_horaria.strip()) == 0:
            messages.add_message(request,constants.ERROR,'Preencha todos os campos em branco.')
            return redirect('/eventos/novo_evento')
        
        if not logo:
            messages.add_message(request,constants.ERROR,'Coloque a logo do seu evento!')
            return redirect('/eventos/novo_evento')

        evento = Evento( criador = request.user ,nome = nome, descricao = descricao, data_inicio = data_inicio, data_termino = data_termino, carga_horaria = carga_horaria, logo = logo, cor_fundo = cor_fundo, cor_principal = cor_principal, cor_secundaria = cor_secundaria)
        

        evento.save()
        messages.add_message(request, constants.SUCCESS, 'Evento cadastrado com sucesso')
        return redirect(reverse('novo_evento'))
    




@login_required(login_url='/auth/login/')
def gerenciar_evento(request):
    if request.method == 'GET':
        eventos = Evento.objects.filter(criador = request.user)
        nome = request.GET.get('nome')
        if nome:
            eventos = Evento.objects.filter(nome = nome)
        
        return render(request, 'gerenciar_evento.html',{'eventos':eventos})
        
    


@login_required(login_url='/auth/login/')
def inscrever_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if request.method == "GET":
        return render(request, 'inscrever_evento.html', {'evento':evento})
    
    if request.method == "POST":
        participante = Evento.objects.filter(id = id).filter(participantes = request.user)
        if not participante:
            evento.participantes.add(request.user)
            evento.save()
            messages.add_message(request,constants.SUCCESS,'Inscrição realizada com sucesso!')
            return redirect(f'/eventos/inscrever_evento/{id}')




@login_required(login_url='/auth/login/')
def participantes_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if request.method =="GET":
        if not evento.criador == request.user:
            raise Http404('Esse evento não é seu')
        participantes = evento.participantes.all()[::3]
        return render(request, 'participantes_evento.html',{'participantes': participantes,'evento':evento})