from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):

    nombre = models.CharField(max_length=100)
    precio = models.IntegerField()
    descripcion = models.TextField()
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='marca', default=1)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    imagen = models.ImageField(upload_to='producto', default='C:/Users/nicol/Desktop/Integracionnde plataformas/Pagina web/FERREMAS/media/default.jpg')
    stock = models.IntegerField(null=True)

    def __str__(self):
        return self.nombre
    
class Direccion(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='direccion')
    nombre = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=50)  # <- cambiado de IntegerField a CharField
    dep = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.nombre)


class Pedido(models.Model):

    ESTADO_OPCIONES = [
        (0, 'En preparación'),
        (1, 'En camino'),
        (2, 'Entregado'),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name='pedidos')
    created_at = models.DateTimeField(auto_now_add=True)
    direccion = models.ForeignKey(Direccion,on_delete=models.PROTECT, default=1, related_name='direccion')
    total = models.IntegerField()
    estado = models.IntegerField(choices=ESTADO_OPCIONES, default=0)

    def __str__(self):

        return str(self.id)
    
    @property
    def estado_display(self):
        return dict(Pedido.ESTADO_OPCIONES).get(self.estado)
    

    class Meta:
        db_table = 'pedidos' #Como se va a ver en la basen de datos
        verbose_name ='pedido'
        verbose_name_plural ='pedidos'
    
    
class DetallePedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='detalle_pedido')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_pedido')
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name='detalles_pedido')
    cantidad = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cantidad} unidades de {self.producto}'

    class Meta:
        db_table = 'detalle_pedido'  # Cómo se verá en la base de datos
        verbose_name = 'detalle_pedido'
        verbose_name_plural = 'detalle_pedidos'