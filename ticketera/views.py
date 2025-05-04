from datetime import timedelta
from urllib import request
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from ticketera.forms import UserForm, TicketForm
from .models import SLA
from .models import TICKET
from django.views.generic import ListView
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView
from django.utils.timezone import now

#VISTAS PARA PAGINAS DE SOLO VISUALIZACION

def base(request):

    return render (request, 'app/base.html')

def base2(request):

    return render (request, 'app/base2.html')

def pagCrud(request):

    return render (request, 'app/pagCrud.html')

def pagPass(request):

    return render (request, 'app/pagPass.html')

#--------------------------------------
def actualizar_estado_sla(ticket):
    print(f"Evaluando ticket {ticket.id} - {ticket.titulo}")
    if not ticket.sla_aplicado:
        return

    sla = ticket.sla_aplicado
    ahora = timezone.now()

    vencido = False

    if ticket.fecha_primera_respuesta:
        minutos = (ticket.fecha_primera_respuesta - ticket.fecha_creacion).total_seconds() / 60
        if minutos > sla.tiempo_respuesta:
            vencido = True
    else:
        minutos = (ahora - ticket.fecha_creacion).total_seconds() / 60
        if minutos > sla.tiempo_respuesta:
            vencido = True

    # Verificar tiempo de resolución
    if ticket.fecha_resolucion:
        minutos = (ticket.fecha_resolucion - ticket.fecha_creacion).total_seconds() / 60
        if minutos > sla.tiempo_resolucion:
            vencido = True
    else:
        minutos = (ahora - ticket.fecha_creacion).total_seconds() / 60
        if minutos > sla.tiempo_resolucion:
            vencido = True

    nuevo_estado = 'Sla vencido' if vencido else 'Sla en regla'
    print(f"Ticket {ticket.id} - estado actual: '{ticket.sla_estado}' | estado calculado: '{nuevo_estado}'")
    if ticket.sla_estado != nuevo_estado:
        print(f"Ticket {ticket.id}: estado SLA cambia de {ticket.sla_estado} a {nuevo_estado}")
        ticket.sla_estado = nuevo_estado
        ticket.save()
        print(f"Ticket {ticket.id}: SLA actualizado a {nuevo_estado}")


def tickets_vencidos(request):
    tickets = TICKET.objects.all()

    for ticket in tickets:
        actualizar_estado_sla(ticket)

    tickets_vencidos = TICKET.objects.filter(sla_estado='Sla vencido')

    return render(request, 'app/tickets_vencidos.html', {'tickets_vencidos': tickets_vencidos})
    
#--------------------------------------

#DASHBOARD O LISTA DE TICKETS

class lista_ticketUserView(ListView):
    model = TICKET
    template_name = 'app/lista_ticketUser.html'
    context_object_name = 'tickets'
    ordering = ['-fecha_creacion']

class editar_ticketView(UpdateView):
    model = TICKET
    form_class = TicketForm
    template_name = 'app/editar_ticket.html'
    success_url = reverse_lazy('lista_ticket')

    def form_valid(self, form):
        ticket = form.save(commit=False)

        if ticket.estado != 'Abierto' and not ticket.fecha_primera_respuesta:
            ticket.fecha_primera_respuesta = timezone.now()

        if ticket.estado == 'Resuelto' and not ticket.fecha_resolucion:
            ticket.fecha_resolucion = timezone.now()

        if ticket.estado == 'Resuelto' and ticket.fecha_resolucion and ticket.sla_aplicado:
            limite = ticket.fecha_creacion + timedelta(hours=ticket.sla_aplicado.tiempo_resolucion)
            if ticket.fecha_resolucion > limite:
                # Puedes usar un print o log, o definir una propiedad para detectar esto
                print("Ticket resuelto fuera de SLA")  # O puedes usar una propiedad en el modelo
                # Si decides persistir este estado, tendrías que crear un nuevo campo o estado

        ticket.save()
        return super().form_valid(form)
        
class lista_ticketView(LoginRequiredMixin, ListView):
    model = TICKET
    template_name = 'app/lista_ticket.html'
    context_object_name = 'tickets'
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        user = self.request.user

        if user.last_name in ['Administrador', 'Analista']:
            return TICKET.objects.all().order_by('-fecha_creacion')
        elif user.last_name == 'Usuario':
            return TICKET.objects.filter(id_usuario_solicitante=user).order_by('-fecha_creacion')
        else:
            return TICKET.objects.none()  

class CrearTicketView(CreateView):
    model = TICKET
    form_class = TicketForm
    template_name = 'app/pagCrearticket.html'
    success_url = reverse_lazy('lista_ticket')

    def form_valid(self, form):
        ticket = form.save(commit=False)
    
        sla_activo = SLA.objects.filter(activo=True).first()
        if sla_activo:
            ticket.sla_aplicado = sla_activo
    
        ticket.save()
        return super().form_valid(form)

#CONFIGURACION SLA

def configuracion_sla(request, sla_id):
    sla = get_object_or_404(SLA, id=sla_id)
    
    sla.activo = True
    sla.save()

    TICKET.objects.filter(sla_aplicado__isnull=True).update(sla_aplicado=sla)
    
    messages.success(request, f"El SLA '{sla.nombre_sla}' ha sido activado y aplicado a tickets existentes.")
    return redirect('lista_sla')

class lista_slaView(ListView):
    model = SLA
    template_name = 'app/lista_sla.html'
    context_object_name = 'slas'
    ordering = ['-activo', 'nombre_sla']

class crear_slaView(CreateView):
    model = SLA
    fields = ['nombre_sla', 'tiempo_respuesta', 'tiempo_resolucion', 'activo']
    template_name = 'app/crear_sla.html'
    success_url = reverse_lazy('lista_sla')

class editar_slaView(UpdateView):
    model = SLA
    fields = ['nombre_sla', 'tiempo_respuesta', 'tiempo_resolucion', 'activo']
    template_name = 'app/editar_sla.html'
    success_url = reverse_lazy('lista_sla')

class eliminar_slaView(DeleteView):
    model = SLA
    template_name = 'app/sla_confirm_delete.html'
    success_url = reverse_lazy('lista_sla')

#INICIO Y CIERRE DE SESION

def pagLogin(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('contrasena')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.last_name == 'Administrador'or username == 'admin':
                return redirect('lista_ticket')
            elif user.last_name == 'Analista':
                return redirect('lista_ticket')
            elif user.last_name == 'Usuario':
                return redirect('lista_ticket')      
            else:
                return redirect('pagLogin') 
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            return redirect('pagLogin')
    
    return render(request, 'app/pagLogin.html')

def pagLogout(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'¡Hasta pronto, {username}! Tu sesión se ha cerrado correctamente.')
    return redirect('pagLogin')


#ADMINISTRACION DE USUARIOS

class ListarUsuarios(ListView):
    model = User
    template_name = 'app/listar_usuarios.html'
    context_object_name = 'usuarios'


class CrearUsuario(CreateView):
    model = User
    form_class = UserForm
    template_name = 'app/crear_usuario.html'
    success_url = reverse_lazy('ListarUsuarios')

class EliminarUsuario(DeleteView):
    model = User
    template_name = 'app/eliminar_usuario.html'
    success_url = reverse_lazy('ListarUsuarios')

def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    try:
        return super().post(request, *args, **kwargs)
    except ProtectedError:
        messages.error(request, "¡No se puede eliminar el usuario porque tiene tickets asignados!")
        return render(request, self.template_name, {'object': self.object})

class EditarUsuario(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'app/editar_usuario.html'
    success_url = reverse_lazy('ListarUsuarios')