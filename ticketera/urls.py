from django.urls import path
from ticketera import views

urlpatterns = [
    #INICIO Y CIERRE DE SESION
    path('', views.pagLogin, name="pagLogin"),
    path('pagLogin/', views.pagLogin, name="pagLogin"),
    path('pagLogout/', views.pagLogout, name='pagLogout'),
    #ARCHIVO BASE, PARA HEADER Y FOOTER
    path('base/', views.base, name="base"),
    path('base2/', views.base2, name="base2"),
    #ADMINISTRACION DE USUARIOS
    path('pagCrud/', views.pagCrud, name="pagCrud"),
    path('ListarUsuarios/', views.ListarUsuarios.as_view(), name='ListarUsuarios'),
    path('CrearUsuario/', views.CrearUsuario.as_view(), name='CrearUsuario'), 
    path('EditarUsuario/<int:pk>/', views.EditarUsuario.as_view(), name='EditarUsuario'),  
    path('EliminarUsuario/<int:pk>/', views.EliminarUsuario.as_view(), name='EliminarUsuario'),
    #URL RESTABLECER CONTRASEÑA
    path('pagPass/', views.pagPass, name="pagPass"),
    #CONFIGURACION SLA
    path('lista_sla/', views.lista_slaView.as_view(), name='lista_sla'),
    path('crear_sla/', views.crear_slaView.as_view(), name='crear_sla'),
    path('editar_sla/<int:pk>/', views.editar_slaView.as_view(), name='editar_sla'),
    path('eliminar_sla/<int:pk>/', views.eliminar_slaView.as_view(), name='eliminar_sla'),
    path('configuracion_sla/<int:sla_id>/', views.configuracion_sla, name='configuracion_sla'),
    #ADMINISTRACION DE TICKETS
    path('lista_ticket/', views.lista_ticketView.as_view(), name='lista_ticket'),
    path('CrearTicketView', views.CrearTicketView.as_view(), name="CrearTicketView"),
    path('editar_ticket/<int:pk>/', views.editar_ticketView.as_view(), name='editar_ticket'),
    path('lista_ticketUser/', views.lista_ticketUserView.as_view(), name='lista_ticketUser'),
]
