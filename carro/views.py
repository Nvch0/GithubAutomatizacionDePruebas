from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .carro import Carro
from producto.models import Producto, Direccion, Categoria

from producto.models import Pedido, DetallePedido, Producto

@login_required
def mis_compras(request):
    pedidos = Pedido.objects.filter(user=request.user).order_by('-fecha')
    detalle_pedidos = DetallePedido.objects.filter(pedido__user=request.user)
    
    return render(request, 'mis_compras.html', {
        'pedidos': pedidos,
        'detalle_pedidos': detalle_pedidos
    })


@login_required
def vista_carro(request):
    carro = Carro(request)

    if not carro.carro:
        return render(request, 'carro.html')

    if request.method == 'POST':
        Direccion.objects.create(
            user=request.user,
            nombre=request.POST['nombre'],
            region=request.POST['region'],
            comuna=request.POST['comuna'],
            calle=request.POST['calle'],
            numero=request.POST['numero'],
            dep=request.POST['casa']
        )

    direccion_id = request.session.get('direccion_id')
    direccion_envio = Direccion.objects.filter(id=direccion_id)
    direcciones = Direccion.objects.all()
    categorias = Categoria.objects.all()

    token_ws = None
    url_transbank = None

    if direccion_id:
        total = sum(
            float(producto["precio"]) * producto["cantidad"]
            for producto in carro.carro.values()
        )
        buy_order = f"ORDER-{request.user.id}-{direccion_id}"
        session_id = f"SESSION-{request.user.id}"
        amount = total
        return_url = request.build_absolute_uri('/carro/retorno/')

        try:
            options = WebpayOptions(
                commerce_code=settings.TRANSBANK_COMMERCE_CODE,
                api_key=settings.TRANSBANK_API_KEY,
                integration_type=IntegrationType.TEST if settings.TRANSBANK_ENVIRONMENT == 'TEST' else IntegrationType.LIVE
            )

            tx = Transaction(options)
            response = tx.create(
                buy_order=buy_order,
                session_id=session_id,
                amount=amount,
                return_url=return_url
            )

            token_ws = response['token']
            url_transbank = response['url']
            print("✅ Transacción iniciada con token:", token_ws)
        except Exception as e:
            print("❌ Error al iniciar transacción Transbank:", str(e))

    return render(request, 'carro.html', {
        'token_ws': token_ws,
        'url_transbank': url_transbank,
        'direcciones': direcciones,
        'categorias': categorias,
        'direccion_id': direccion_id,
        'direccion_envio': direccion_envio,
    })



@login_required
def webpay_retorno(request):
    token = request.POST.get("token_ws") or request.GET.get("token_ws")
    if not token:
        return render(request, "pago_error.html", {"mensaje": "Token no proporcionado por Transbank."})

    try:
        options = WebpayOptions(
            commerce_code=settings.TRANSBANK_COMMERCE_CODE,
            api_key=settings.TRANSBANK_API_KEY,
            integration_type=IntegrationType.TEST if settings.TRANSBANK_ENVIRONMENT == 'TEST' else IntegrationType.LIVE
        )

        tx = Transaction(options)
        response = tx.commit(token)
        status = response.get("status")

        if status == "AUTHORIZED":
            carro = Carro(request)

            if not carro.carro:
                return render(request, "pago_error.html", {"mensaje": "Tu carrito está vacío."})

            direccion = Direccion.objects.get(id=request.session.get('direccion_id'))
            pedido = Pedido.objects.create(
                user=request.user,
                direccion=direccion,
                total=response['amount'],
                estado=2
            )

            for key, item in carro.carro.items():
                producto = Producto.objects.get(id=key)
                DetallePedido.objects.create(
                    user=request.user,
                    pedido=pedido,
                    producto=producto,
                    cantidad=item['cantidad']
                )

            carro.limpiar_carro()

            return render(request, "pago_exito.html", {"response": response})

        else:
            return render(request, "pago_error.html", {
                "mensaje": "Transacción rechazada",
                "response": response
            })

    except Exception as e:
        return render(request, "pago_error.html", {
            "mensaje": f"Error al confirmar transacción: {str(e)}"
        })

@login_required
def agregar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.agregar(producto=producto)
    return redirect("carro:carro")

def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    return redirect("carro:carro")

def calcular_total(carro):
    total = 0
    for value in carro.carro.values():
        total += int(value['precio']) * value['cantidad']
    return total

def sumar_producto(request, producto_id):
    try:
        carro = Carro(request)
        producto = Producto.objects.get(id=producto_id)
        carro.agregar(producto=producto)
        cantidad = carro.carro[str(producto.id)]['cantidad']
        total = calcular_total(carro)
        return JsonResponse({'message': 'Producto sumado', 'cantidad': cantidad, 'total': total})
    except Producto.DoesNotExist:
        return JsonResponse({'message': 'Producto no encontrado'}, status=404)

@login_required
def restar_producto(request, producto_id):
    try:
        carro = Carro(request)
        producto = Producto.objects.get(id=producto_id)
        carro.restar_producto(producto=producto)
        cantidad = carro.carro.get(str(producto.id), {}).get('cantidad', 0)
        total = calcular_total(carro)
        return JsonResponse({'message': 'Producto restado', 'cantidad': cantidad, 'total': total})
    except Producto.DoesNotExist:
        return JsonResponse({'message': 'Producto no encontrado'}, status=404)

@login_required
def eliminar_producto(request, producto_id):
    try:
        carro = Carro(request)
        producto = Producto.objects.get(id=producto_id)
        carro.eliminar(producto=producto)
        total = calcular_total(carro)
        return JsonResponse({'message': 'Producto eliminado', 'total': total})
    except Producto.DoesNotExist:
        return JsonResponse({'message': 'Producto no encontrado'}, status=404)

def confirmar_direccion(request):
    if request.method == 'POST':
        direccion_id = request.POST.get('direccion')
        if direccion_id:
            request.session['direccion_id'] = direccion_id
    return redirect('carro:carro')

def cambiar_direccion(request):
    request.session.pop('direccion_id', None)
    return redirect('carro:carro')
