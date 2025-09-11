from email.header import Header
from django.shortcuts import render, redirect, get_object_or_404
from producto.models import Producto, Categoria, Pedido, DetallePedido, Direccion, Marca
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from .forms import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from carro.context_processor import importe_total_carro
from carro.carro import Carro
from django.utils.html import strip_tags
import csv
from django.http import HttpResponse
from django.db.models import Q
from django.urls import reverse
# Create your views here.


def home(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    

    queryset = request.GET.get('buscar')

    if queryset:
        productos = Producto.objects.filter(
            Q(nombre__icontains=queryset)
        ).distinct()

    data = {
        'productos': productos,
        'categorias': categorias,
        
    }

    return render(request, 'index.html', data)


def admin(request):

    if request.user.is_staff:
    
        productos = Producto.objects.all()
        categorias = Categoria.objects.all()
        marcas = Marca.objects.all()

        data = {
            'productos': productos,
            'categorias': categorias,
            'marcas':marcas
        }


        if request.method != 'POST':
            return render(request, 'administrador/admin.html', data)
        else:
            form_id = request.POST.get('form_id')
            if form_id == 'form-producto':
                imagen = request.FILES.get('imagen')
                if not imagen:
                    imagen = '/producto/default.jpg'
                nombre = request.POST['nombre']
                descipcion = request.POST['desc']
                seccion = request.POST['seccion']
                marca = request.POST['marca-list']
                precio = request.POST['precio']
                stock = request.POST['stock']

                categoria = Categoria.objects.get(nombre=seccion)
                marca = Marca.objects.get(nombre = marca )

                objProducto = Producto.objects.create(
                    imagen=imagen,
                    nombre=nombre,
                    descripcion=descipcion,
                    precio=precio,
                    categoria=categoria,
                    marca = marca,
                    stock = stock,
                )
                objProducto.save()
            elif form_id == 'form-categoria':

                categoria  = request.POST['nueva-categoria']
                objCategoria = Categoria.objects.create(
                    nombre = categoria 
                )

                objCategoria.save()

            elif form_id == 'form-marca':

                marca  = request.POST['nueva-marca']
                objmarca = Marca.objects.create(
                    nombre = marca 
                )

                objmarca.save()
                messages.success(request,'Producto creado correctamente')

            # return redirect(to='admin_page:productos')

            return render(request, 'administrador/admin.html', data)
        
    else:
        return redirect(to='home:home')
    
def admin_pedido(request):
    pedidos = Pedido.objects.all()
    detalles_pedidos = DetallePedido.objects.all()

    pedidos_con_detalles = []

    for p in pedidos:
        detalles = []
        for dp in detalles_pedidos:
            if p.id == dp.pedido_id:
                detalles.append(dp.producto)
            

        pedido = {
            'id': p.id,
            'user': p.user,
            'total': p.total,
            'fecha': p.created_at,
            'direccion':p.direccion,
            'productos': detalles
        }
        pedidos_con_detalles.append(pedido)

    data = {
        'pedidos': pedidos_con_detalles
    }

    return render(request, 'administrador/pedidos_admin.html', data)

def export_pedidos_csv(request):
    # Crear la respuesta con el tipo de contenido CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pedidos.csv"'

    # Crear un escritor CSV
    writer = csv.writer(response)
    # Escribir el encabezado del CSV
    writer.writerow(['ID', 'Fecha', 'Total','Cliente'])

    # Obtener todos los registros de pedidos y escribirlos en el CSV
    pedidos = Pedido.objects.all()
    for pedido in pedidos:
        writer.writerow([pedido.pk, pedido.created_at, pedido.total, pedido.user])

    return response

def admin_api(request):

    return render(request,'administrador/api_admin.html')


def eliminar(request, id):

    producto = get_object_or_404(Producto, id=id)
    producto.delete()

    return redirect(to='home:administrador')


# seccion de contacto
def contacto(request):

    if request.method =='POST':

        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        template = render_to_string('Contacto/email_cointacto.html', {
            'name':name,
            'email':email,
            'message':message
        })

        email = EmailMessage(
            subject,
            template,
            settings.EMAIL_HOST_USER,
            ['nicolas134b@gmail.com']
        )

        email.content_subtype = 'html'

        email.fail_silently = False
        email.send()

        messages.success(request,'Se ha enviado el correo')

        return redirect(to='home:contacto')

        


    return render(request, 'contacto/Contacto.html', )

def registro(request):

    data = {
        'form':CustomUser()
    }

    if request.method == 'POST':
        formulario = CustomUser(data = request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username = formulario.cleaned_data["username"], password = formulario.cleaned_data["password1"])
            login(request, user)
            messages.success(request,'Creado correctamente')
            return redirect(to='home:home')
        data["form"] = formulario

    return render(request,'registration/registro.html',data)

def vista_usuario(request):
    total = importe_total_carro(request)
    importe_total = total['importe_total_carro']

    status = request.GET.get('status')

    if status == 'approved':
        direccion_id = request.session.get('direccion_id')
        if direccion_id:
            direccion = Direccion.objects.get(id=direccion_id)
            pedido = Pedido.objects.create(user=request.user, total=importe_total,direccion=direccion)
            del request.session['direccion_id']
        else:
            pedido = Pedido.objects.create(user=request.user, total=importe_total,direccion_id=11)

        carro = Carro(request)
        compra = [
            DetallePedido(
                user=request.user,
                producto_id=key,
                pedido=pedido,
                cantidad=value['cantidad'],
            ) for key, value in carro.carro.items()
        ]

        DetallePedido.objects.bulk_create(compra)

        enviar_mail(
            pedido=pedido,
            detalle_pedido=compra,
            nombreusuario=request.user.username,
            emailusuario=request.user.email,
            total=importe_total_carro(request)
        )

        # Redirige a la misma página sin parámetros
        return redirect(reverse('home:mis_compras'))

    pedidos = Pedido.objects.filter(user=request.user)
    detalles = DetallePedido.objects.filter(user=request.user)

    data = {
        'pedidos': pedidos,
        'detalle_pedidos': detalles,
        'status': status if status else 'No existe ninguna pago'
    }

    return render(request, 'usuario/mis_compras.html', data)

def salir(request):
    logout(request)
    return redirect(to='home:home')

from django.core.mail import EmailMessage


"""
def enviar_mail(**kwargs):
    asunto = 'Gracias por el pedido'

    ctx = {
        'pedido': kwargs.get('pedido'),
        'detalle_pedido': kwargs.get('detalle_pedido'),
        'nombreusuario': kwargs.get('nombreusuario'),
        'total': kwargs.get('total'),
    }

    mensaje_html = render_to_string('usuario/pedido.html', ctx)
    mensaje_texto = strip_tags(mensaje_html)
    
    email = EmailMessage(
        asunto,
        mensaje_html,
        'antoniobarraza1133@gmail.com',
        [kwargs.get('emailusuario')],
    )
    email.content_subtype = 'html'
    email.encoding = 'utf-8'  # 🔐 evita UnicodeEncodeError con ñ, tildes, emojis
    email.send(fail_silently=False)
"""


def enviar_mail(**kwargs):
    print("🧪 Correo simulado: no se envió nada.")


    

def bodega(request):

    pedidos = Pedido.objects.all()

    detalle = DetallePedido.objects.all()

    queryset = request.GET.get('buscar-pedido')

    if queryset:
        pedidos = Pedido.objects.filter(
            Q(id__icontains=queryset),
        ).distinct()

    data = {
        'pedidos' : pedidos,
        'detalle' : detalle
    }

    return render(request,'bodega/bodega.html', data)

def cambiar_estado_pedido(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('select-estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.estado = nuevo_estado
        pedido.save()
    return redirect('home:bodega')