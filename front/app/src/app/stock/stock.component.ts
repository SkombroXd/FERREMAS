import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-stock',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './stock.component.html',
  styleUrl: './stock.component.css'
})
export class StockComponent implements OnInit, OnDestroy {
  productos: any[] = [];
  notificaciones: any[] = [];
  productoSeleccionado: string = '';
  productoActual: any = null;
  cantidadAgregar: number = 0;
  mostrarAlertas: boolean = false;
  private eventSource: EventSource | null = null;
  private subscription: Subscription | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.cargarProductos();
    this.iniciarNotificaciones();
  }

  ngOnDestroy() {
    if (this.eventSource) {
      this.eventSource.close();
    }
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  toggleAlertas() {
    this.mostrarAlertas = !this.mostrarAlertas;
  }

  cargarProductos() {
    this.http.get<any[]>('http://localhost:5000/api/lista-productos').subscribe(
      (data) => {
        // Ordenar productos alfabéticamente por nombre
        this.productos = data.sort((a, b) => a.nombre_p.localeCompare(b.nombre_p));
        // Verificar productos con stock bajo al cargar
        this.verificarStockBajo();
      },
      (error) => {
        console.error('Error al cargar productos:', error);
      }
    );
  }

  verificarStockBajo() {
    this.productos.forEach(producto => {
      if (producto.unidades_p < 10) {
        const notificacion = {
          tipo: 'stock_bajo',
          producto: producto.nombre_p,
          stock: producto.unidades_p
        };
        this.agregarNotificacion(notificacion);
      }
    });
  }

  agregarNotificacion(notificacion: any) {
    // Evitar duplicados
    const existe = this.notificaciones.some(n => 
      n.producto === notificacion.producto && n.stock === notificacion.stock
    );
    
    if (!existe) {
      this.notificaciones.unshift(notificacion);
      // Mostrar automáticamente las alertas cuando hay nuevas
      this.mostrarAlertas = true;
    }
  }

  seleccionarProducto() {
    if (this.productoSeleccionado) {
      this.productoActual = this.productos.find(p => p.cod_producto === this.productoSeleccionado);
      this.cantidadAgregar = 0;
    } else {
      this.productoActual = null;
    }
  }

  iniciarNotificaciones() {
    this.eventSource = new EventSource('http://localhost:5000/api/notificaciones');
    
    this.eventSource.onmessage = (event) => {
      const notificacion = JSON.parse(event.data);
      if (notificacion.tipo === 'stock_bajo') {
        this.agregarNotificacion(notificacion);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('Error en SSE:', error);
      if (this.eventSource) {
        this.eventSource.close();
        // Intentar reconectar después de 5 segundos
        setTimeout(() => this.iniciarNotificaciones(), 5000);
      }
    };
  }

  agregarStock() {
    if (!this.productoActual || this.cantidadAgregar <= 0) return;

    this.http.post('http://localhost:5000/api/actualizar-stock', {
      cod_producto: this.productoActual.cod_producto,
      cantidad: this.cantidadAgregar
    }).subscribe(
      (response: any) => {
        // Actualizar localmente
        this.productoActual.unidades_p = response.stock_actual;
        this.cantidadAgregar = 0;

        // Verificar si el stock sigue bajo
        if (this.productoActual.unidades_p < 10) {
          const notificacion = {
            tipo: 'stock_bajo',
            producto: this.productoActual.nombre_p,
            stock: this.productoActual.unidades_p
          };
          this.agregarNotificacion(notificacion);
        } else {
          // Remover notificación si el stock ya no está bajo
          this.notificaciones = this.notificaciones.filter(n => n.producto !== this.productoActual.nombre_p);
        }
      },
      (error) => {
        console.error('Error al actualizar stock:', error);
      }
    );
  }
}
