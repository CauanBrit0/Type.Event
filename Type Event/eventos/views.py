from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Evento, Certificado
from django.urls import reverse
import csv
from secrets import token_urlsafe
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


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
    if not evento.criador == request.user:
            raise Http404('Esse evento não é seu')
    if request.method =="GET":
        participantes = evento.participantes.all()[::3]
        return render(request, 'participantes_evento.html',{'participantes': participantes,'evento':evento})
    


def gerar_csv(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não é seu')
    
    participantes = evento.participantes.all()
    token = f'{token_urlsafe(6)}.csv'
    
    path = os.path.join(settings.MEDIA_ROOT, token)

    with open(path,'w') as arq:
        writer = csv.writer(arq, delimiter=',')
        for participante in participantes:
            x = (participante.username, participante.email)
            writer.writerow(x)
    
    return redirect(f'/media/{token}')




def certificados_evento(request, id):
    evento = get_object_or_404(Evento, id = id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não pertence a você.')
    
    if request.method == "GET":
        qtd_certificados = evento.participantes.all().count() - Certificado.objects.filter(evento = evento).count()
        return render(request, 'certificados_evento.html',{'evento':evento,'qtd_certificados':qtd_certificados})


    

def gerar_certificado(request ,id):
    evento = get_object_or_404(Evento, id = id)
    if not evento.criador == request.user:
        raise Http404('Esse evento não pertence a você.')
    
    path_template = os.path.join(settings.BASE_DIR,'templates/static/evento/img/template_cerficado.png')
    path_fonte = os.path.join(settings.BASE_DIR,'templates/static/fontes/arimo.ttf')
    
    for participante in evento.participantes.all():
        #TODO VALIDAR SE O CERTIFICADO JÁ FOI GERADO.
        img = Image.open(path_template)
        draw = ImageDraw.Draw(img)

        font_nome = ImageFont.truetype(path_fonte, 80)
        font_info = ImageFont.truetype(path_fonte, 30)

        draw.text((230, 651), f"{participante.username}", font=font_nome, fill=(0,0,0))
        draw.text((761, 782), f"{evento.nome}", font=font_info, fill=(0,0,0))
        draw.text((816, 849), f"{evento.carga_horaria}", font=font_info, fill=(0,0,0))
        
        output = BytesIO()
        img.save(output, format='PNG', quality=100)
        output.seek(0)

        img_final = InMemoryUploadedFile(output,
                                        'ImageField',
                                        f'{token_urlsafe(8)}.png',
                                        'image/jpeg',
                                        sys.getsizeof(output),
                                        None)
        certificado_gerado = Certificado(
            certificado=img_final,
            participante=participante,
            evento=evento,
        )
        certificado_gerado.save()
    
    messages.add_message(request, constants.SUCCESS, 'Certificados gerados')
    return redirect(reverse('certificados_evento', kwargs={'id': evento.id}))
