import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { CarritoService } from '../services/carrito.service';
import { PagoService } from '../services/pago.service';
import { Subscription } from 'rxjs';
import { HttpClient } from '@angular/common/http';

interface ProductoAgrupado {
  cod_producto: string;
  nombre_p: string;
  precio_p: number;
  cantidad: number;
  subtotal: number;
}

@Component({
  selector: 'app-pago',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pago.component.html',
  styleUrl: './pago.component.css'
})
export class PagoComponent implements OnInit, OnDestroy {
  productosAgrupados: ProductoAgrupado[] = [];
  totalProductos: number = 0;
  totalPagar: number = 0;
  totalDolares: number = 0;
  valorDolar: number = 0;
  private subscription: Subscription;
  procesandoPago: boolean = false;

  constructor(
    private carritoService: CarritoService,
    private pagoService: PagoService,
    private router: Router,
    private http: HttpClient
  ) {
    this.subscription = new Subscription();
  }

  ngOnInit() {
    this.cargarValorDolar();
    this.subscription = this.carritoService.getCarrito().subscribe(productos => {
      console.log('Productos en el carrito:', productos);
      this.productosAgrupados = this.agruparProductos(productos);
      this.calcularTotales();
    });
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  private agruparProductos(productos: any[]): ProductoAgrupado[] {
    const productosMap = new Map<string, ProductoAgrupado>();

    productos.forEach(producto => {
      if (productosMap.has(producto.cod_producto)) {
        const productoExistente = productosMap.get(producto.cod_producto)!;
        productoExistente.cantidad += 1;
        productoExistente.subtotal = productoExistente.cantidad * productoExistente.precio_p;
      } else {
        productosMap.set(producto.cod_producto, {
          cod_producto: producto.cod_producto,
          nombre_p: producto.nombre_p,
          precio_p: Number(producto.precio_p),
          cantidad: 1,
          subtotal: Number(producto.precio_p)
        });
      }
    });

    return Array.from(productosMap.values());
  }

  private calcularTotales() {
    this.totalProductos = this.productosAgrupados.reduce((total, producto) => total + producto.cantidad, 0);
    this.totalPagar = this.productosAgrupados.reduce((total, producto) => total + producto.subtotal, 0);
    console.log('Total productos:', this.totalProductos);
    console.log('Total a pagar:', this.totalPagar);
    this.calcularTotalDolares();
  }

  private calcularTotalDolares() {
    if (this.valorDolar > 0) {
      this.totalDolares = this.totalPagar / this.valorDolar;
    }
  }

  eliminarProducto(producto: ProductoAgrupado) {
    console.log('Eliminando producto:', producto);
    this.carritoService.eliminarProducto(producto.cod_producto);
  }

  cancelarCompra() {
    this.carritoService.limpiarCarrito();
    this.router.navigate(['/home']);
  }

  private actualizarProductos() {
    const productos = this.carritoService.obtenerCarrito();
    this.productosAgrupados = this.agruparProductos(productos);
    this.calcularTotales();
  }

  async procesarPago() {
    if (this.procesandoPago) return;
    
    try {
      this.procesandoPago = true;
      console.log('Iniciando proceso de pago...');
      console.log('Productos:', this.productosAgrupados);
      console.log('Total:', this.totalPagar);

      const response = await this.pagoService.procesarPago(
        this.productosAgrupados,
        this.totalPagar
      ).toPromise();

      console.log('Respuesta del servidor:', response);

      if (response && response.url && response.token_ws) {
        // Guardar datos necesarios en localStorage para el checkout
        localStorage.setItem('token_ws', response.token_ws);
        localStorage.setItem('orden_compra', response.orden_compra);
        
        console.log('Redirigiendo a:', response.url);
        
        // Crear un formulario y enviarlo para la redirección
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = response.url;
        
        const tokenInput = document.createElement('input');
        tokenInput.type = 'hidden';
        tokenInput.name = 'token_ws';
        tokenInput.value = response.token_ws;
        
        form.appendChild(tokenInput);
        document.body.appendChild(form);
        form.submit();
      } else {
        throw new Error('Respuesta inválida del servidor');
      }
    } catch (error) {
      console.error('Error al procesar el pago:', error);
      alert('Error al procesar el pago. Por favor, intente nuevamente.');
    } finally {
      this.procesandoPago = false;
    }
  }

  private cargarValorDolar() {
    // Usando la API de Mindicador.cl para obtener el valor del dólar
    this.http.get('https://mindicador.cl/api/dolar').subscribe(
      (data: any) => {
        this.valorDolar = data.serie[0].valor;
        this.calcularTotalDolares();
      },
      error => {
        console.error('Error al cargar valor del dólar:', error);
      }
    );
  }
}
