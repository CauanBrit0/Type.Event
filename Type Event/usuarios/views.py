from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth

def login(request):
    if request.method == "GET":
         return render(request, 'login.html')
    
    if request.method =="POST":
         username = request.POST.get('username')
         senha = request.POST.get('senha')

         if len(username.strip()) == 0 or len(senha.strip()) == 0:
            messages.add_message(request,constants.ERROR,'Preencha todos os campos em branco.')
            return redirect('/auth/login')
         
         usuario = auth.authenticate(request, username=username, password = senha)
         if not usuario:
              messages.add_message(request,constants.ERROR,'Credenciais Inválidas')
              return redirect('/auth/login')
         
         auth.login(request,usuario)
         return redirect('/eventos/novo_evento/')
    

    
def cadastro(request):
    if request.method == "GET":
        return render(request,'cadastro.html')
    
    if request.method == "POST":
            username = request.POST.get('username')
            email = request.POST.get('email')
            senha = request.POST.get('senha')
            confirmar_senha = request.POST.get('confirmar_senha')


            if len(username.strip()) == 0 or len(email.strip()) == 0 or len(senha.strip()) == 0 or len(confirmar_senha.strip()) == 0:
                 messages.add_message(request,constants.ERROR,'Preencha todos os campos em branco.')
                 return redirect('/auth/cadastro')
            
            if User.objects.filter(username = username).exists():
                 messages.add_message(request,constants.ERROR,'Nome de Usuário já existente.')
                 return redirect('/auth/cadastro')
            

            if User.objects.filter(email = email).exists():
                 messages.add_message(request,constants.ERROR,'Email já existente.')
                 return redirect('/auth/cadastro')
            
            if len(senha.strip()) < 6:
                 messages.add_message(request,constants.ERROR,'Digite uma senha com mais de 6 caracteres.')
                 return redirect('/auth/cadastro')
                


            if senha != confirmar_senha:
                 messages.add_message(request,constants.ERROR,'As senhas preenchidas não coincidem.')
                 return redirect('/auth/cadastro')
            
            try:
                usuario = User.objects.create_user(username=username, email=email, password=senha)
                usuario.save()
                messages.add_message(request,constants.SUCCESS,'Cadastro realizado com sucesso!')
                return redirect('/auth/login/')
            
            except:
                 
                 messages.add_message(request,constants.ERROR,'Erro interno do sistema.')
                 return redirect('/auth/cadastro')
                 



def sair(request):
     auth.logout(request)
     return redirect('/auth/login/')

