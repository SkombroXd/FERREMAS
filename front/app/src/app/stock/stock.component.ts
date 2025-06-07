import { Component, OnInit, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
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
  mostrarHistorial: boolean = false;
  private eventSource: EventSource | null = null;
  private subscription: Subscription | null = null;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private ngZone: NgZone) {}

  ngOnInit() {
    this.cargarProductos();
    this.iniciarEventSource();
  }

  ngOnDestroy() {
    if (this.eventSource) {
      this.eventSource.close();
    }
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  toggleHistorial() {
    this.mostrarHistorial = !this.mostrarHistorial;
  }

  cargarProductos() {
    this.http.get<any[]>('http://localhost:5000/api/lista-productos').subscribe(
      (data) => {
        this.productos = data.sort((a, b) => a.unidades_p - b.unidades_p);
        if (this.productoActual) {
          const productoActualizado = this.productos.find(p => p.cod_producto === this.productoActual.cod_producto);
          if (productoActualizado) {
            this.productoActual = productoActualizado;
          }
        }
        this.actualizarNotificaciones();
      },
      (error) => {
        console.error('Error al cargar productos:', error);
      }
    );
  }

  iniciarEventSource() {
    if (this.eventSource) {
      this.eventSource.close(); 
    }
    this.eventSource = new EventSource('http://localhost:5000/api/notificaciones');
    
    this.eventSource.onmessage = (event) => {
      this.ngZone.run(() => {
        console.log('StockComponent: Mensaje SSE recibido:', event.data);
        const notificacion = JSON.parse(event.data);
        
        const existe = this.notificaciones.some(n => 
          n.producto === notificacion.producto && n.stock === notificacion.stock
        );
        
        if (!existe) {
          this.notificaciones.unshift(notificacion);
          this.cdr.detectChanges();
        }

        this.cargarProductos();
      });
    };

    this.eventSource.onerror = (error) => {
      this.ngZone.run(() => {
        console.error('StockComponent: Error en la conexión SSE:', error);
        if (this.eventSource && this.eventSource.readyState === EventSource.CLOSED) {
          console.log('StockComponent: Reconectando a SSE...');
          setTimeout(() => this.iniciarEventSource(), 5000);
        }
      });
    };
  }

  actualizarNotificaciones() {
    const productosStockBajo = this.productos.filter(p => p.unidades_p < 10);
    
    const nuevasNotificaciones = productosStockBajo.map(producto => ({
      tipo: 'stock_bajo',
      producto: producto.nombre_p,
      stock: producto.unidades_p
    }));

    this.notificaciones = nuevasNotificaciones;
    this.cdr.detectChanges();
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
    const existe = this.notificaciones.some(n => 
      n.producto === notificacion.producto && n.stock === notificacion.stock
    );
    
    if (!existe) {
      this.notificaciones.unshift(notificacion);
      this.cdr.detectChanges();
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

  seleccionarProductoTabla(producto: any) {
    this.productoActual = producto;
    this.cantidadAgregar = 0;
  }

  agregarStock() {
    if (!this.productoActual || this.cantidadAgregar <= 0) return;

    this.http.post('http://localhost:5000/api/actualizar-stock', {
      cod_producto: this.productoActual.cod_producto,
      cantidad: this.cantidadAgregar
    }).subscribe(
      (response: any) => {
        this.productoActual.unidades_p = response.stock_actual;
        this.cantidadAgregar = 0;

        this.productos = this.productos.sort((a, b) => a.unidades_p - b.unidades_p);

        if (this.productoActual.unidades_p < 10) {
          const notificacion = {
            tipo: 'stock_bajo',
            producto: this.productoActual.nombre_p,
            stock: this.productoActual.unidades_p
          };
          this.agregarNotificacion(notificacion);
        } else {
          this.notificaciones = this.notificaciones.filter(n => n.producto !== this.productoActual.nombre_p);
        }
      },
      (error) => {
        console.error('Error al actualizar stock:', error);
      }
    );
  }

  esStockBajo(producto: any): boolean {
    return producto.unidades_p < 10;
  }

  estaEnAlertas(producto: any): boolean {
    return this.notificaciones.some(n => n.producto === producto.nombre_p);
  }
}
