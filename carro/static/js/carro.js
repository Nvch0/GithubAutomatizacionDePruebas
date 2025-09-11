function actualizarTotal(total) {
    $('#total').text(total);
}

function sumarProducto(productoId) {
    $.ajax({
        url: `/carro/sumar_producto/${productoId}/`,
        method: 'GET',
        success: function(data) {
            $('#cantidad-' + productoId).val(data.cantidad);
            actualizarTotal(data.total);
        }
    });
}

function restarProducto(productoId) {
    $.ajax({
        url: `/carro/restar/${productoId}/`,
        method: 'GET',
        success: function(data) {
            alert(data.message);
            if (data.cantidad > 0) {
                $('#cantidad-' + productoId).val(data.cantidad);
            } else {
                $('#producto-' + productoId).remove();
            }
            actualizarTotal(data.total);
        }
    });
}

function eliminarProducto(productoId) {
    $.ajax({
        url: `/carro/eliminar/${productoId}/`,
        method: 'GET',
        success: function(data) {
            alert(data.message);
            $('#producto-' + productoId).remove();
            actualizarTotal(data.total);
        }
    });
}
