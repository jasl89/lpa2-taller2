// ========================================
// Generador de Facturas - JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    const facturaForm = document.getElementById('facturaForm');
    const loadingDiv = document.getElementById('loading');
    const resultadoCard = document.getElementById('resultadoCard');
    const alertContainer = document.getElementById('alertContainer');
    const btnConsultar = document.getElementById('btnConsultar');

    // Manejar el envío del formulario
    facturaForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const numeroFactura = document.getElementById('numero_factura').value.trim();
        
        if (!numeroFactura) {
            mostrarAlerta('Por favor ingrese un número de factura', 'warning');
            return;
        }

        // Mostrar loading y ocultar resultados anteriores
        loadingDiv.style.display = 'block';
        resultadoCard.style.display = 'none';
        alertContainer.innerHTML = '';
        btnConsultar.disabled = true;

        try {
            // Llamar al endpoint del frontend que consume el backend
            const response = await fetch(`/api/factura/${encodeURIComponent(numeroFactura)}`);
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: No se pudo obtener la factura`);
            }

            const factura = await response.json();
            
            // Mostrar los datos de la factura
            mostrarFactura(factura);
            mostrarAlerta('Factura generada exitosamente', 'success');
            
        } catch (error) {
            console.error('Error:', error);
            mostrarAlerta(`Error al consultar la factura: ${error.message}`, 'danger');
        } finally {
            loadingDiv.style.display = 'none';
            btnConsultar.disabled = false;
        }
    });

    /**
     * Muestra los datos de la factura en la interfaz
     */
    function mostrarFactura(factura) {
        // Información básica
        document.getElementById('detalle_numero').textContent = factura.numero_factura;
        document.getElementById('detalle_fecha').textContent = factura.fecha;

        // Información del cliente
        document.getElementById('detalle_cliente_nombre').textContent = factura.cliente_nombre;
        document.getElementById('detalle_cliente_documento').textContent = factura.cliente_documento;
        document.getElementById('detalle_cliente_direccion').textContent = factura.cliente_direccion;
        document.getElementById('detalle_cliente_telefono').textContent = factura.cliente_telefono;
        document.getElementById('detalle_cliente_email').textContent = factura.cliente_email;

        // Tabla de productos
        const productosBody = document.getElementById('productosBody');
        productosBody.innerHTML = '';

        factura.productos.forEach(producto => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-secondary">${producto.codigo}</span></td>
                <td>${producto.nombre}</td>
                <td><small class="text-muted">${producto.categoria}</small></td>
                <td class="text-center">${producto.cantidad}</td>
                <td class="text-end">$${formatearNumero(producto.precio_unitario)}</td>
                <td class="text-end fw-bold">$${formatearNumero(producto.subtotal)}</td>
            `;
            productosBody.appendChild(row);
        });

        // Totales
        document.getElementById('detalle_subtotal').textContent = `$${formatearNumero(factura.subtotal)}`;
        document.getElementById('detalle_iva').textContent = `$${formatearNumero(factura.iva)}`;
        document.getElementById('detalle_total').textContent = `$${formatearNumero(factura.total)}`;

        // Preparar formulario de PDF
        document.getElementById('numero_factura_pdf').value = factura.numero_factura;

        // Mostrar card de resultados con animación
        resultadoCard.style.display = 'block';
        resultadoCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Muestra un mensaje de alerta
     */
    function mostrarAlerta(mensaje, tipo) {
        const iconos = {
            'success': 'fa-check-circle',
            'danger': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };

        const icono = iconos[tipo] || iconos['info'];

        const alert = document.createElement('div');
        alert.className = `alert alert-${tipo} alert-dismissible fade show`;
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            <i class="fas ${icono} me-2"></i>
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        alertContainer.innerHTML = '';
        alertContainer.appendChild(alert);

        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }

    /**
     * Formatea un número con separadores de miles
     */
    function formatearNumero(numero) {
        return new Intl.NumberFormat('es-CO', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(numero);
    }

    // Manejar el envío del formulario de PDF
    const formPDF = document.getElementById('formPDF');
    formPDF.addEventListener('submit', function(e) {
        mostrarAlerta('Generando PDF... Por favor espere', 'info');
    });

    // Efecto de focus en el input
    const inputFactura = document.getElementById('numero_factura');
    inputFactura.focus();
});

