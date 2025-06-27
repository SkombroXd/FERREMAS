import { Component, OnInit, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { ProductosService, SucursalInterface } from '../services/productos.service';
import { interval } from 'rxjs';

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
  sucursales: SucursalInterface[] = [];
  sucursalSeleccionada: number = 0;
  productosEnAlertaPorSucursal: { [cod_sucursal: number]: number } = {};
  private eventSource: EventSource | null = null;
  private subscription: Subscription | null = null;
  mostrarAlerta: boolean = false;
  alertaMensaje: string = '';

  constructor(
    private http: HttpClient, 
    private cdr: ChangeDetectorRef, 
    private ngZone: NgZone,
    private productosService: ProductosService
  ) {}

  ngOnInit() {
    this.cargarSucursales();
    this.iniciarEventSource();
    
    // Refrescar datos cada 30 segundos para mantener sincronización
    this.subscription = new Subscription();
    this.subscription.add(
      interval(30000).subscribe(() => {
        if (this.sucursalSeleccionada > 0) {
          this.cargarProductosPorSucursal();
        }
      })
    );
  }

  ngOnDestroy() {
    if (this.eventSource) {
      this.eventSource.close();
    }
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  cargarSucursales() {
    this.productosService.getSucursales().subscribe({
      next: (sucursales) => {
        this.sucursales = sucursales;
        if (sucursales.length > 0) {
          this.sucursalSeleccionada = sucursales[0].cod_sucursal;
          this.cargarProductosPorSucursal();
        }
        this.actualizarNotificaciones();
      },
      error: (error) => {
        console.error('Error cargando sucursales:', error);
      }
    });
  }

  cargarProductosPorSucursal() {
    if (this.sucursalSeleccionada === 0) return;
    
    this.productosService.getProductosPorSucursalStock(this.sucursalSeleccionada).subscribe({
      next: (data) => {
        this.productos = data.sort((a, b) => a.unidades_p - b.unidades_p);
        if (this.productoActual) {
          const productoActualizado = this.productos.find(p => p.cod_producto === this.productoActual.cod_producto);
          if (productoActualizado) {
            this.productoActual = productoActualizado;
          }
        }
        this.actualizarNotificaciones();
      },
      error: (error) => {
        console.error('Error al cargar productos:', error);
      }
    });
  }

  onSucursalChange() {
    this.cargarProductosPorSucursal();
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
    
    // Contador para pruebas de rendimiento
    let mensajeCount = 0;
    
    this.eventSource.onopen = () => {
      console.log('✅ Conexión SSE establecida');
    };
    
    this.eventSource.onmessage = (event) => {
      this.ngZone.run(() => {
        mensajeCount++;
        if (mensajeCount % 100 === 0) {
          console.log(`📊 Recibidos ${mensajeCount} mensajes SSE`);
        }
        
        console.log('StockComponent: Mensaje SSE recibido:', event.data);
        
        try {
        const notificacion = JSON.parse(event.data);
        
          // Mostrar timestamp si existe
          if (notificacion.timestamp) {
            console.log('🕓 Timestamp:', notificacion.timestamp);
          }
          
          // Manejar diferentes tipos de notificación
          switch (notificacion.tipo) {
            case 'conexion':
              console.log('🔗 Conexión SSE confirmada:', notificacion.mensaje);
              break;
              
            case 'stock_bajo':
              this.procesarNotificacionStockBajo(notificacion);
              break;
              
            case 'stock_actualizado':
              this.procesarNotificacionStockActualizado(notificacion);
              break;
              
            case 'manual':
              console.log('📝 Mensaje manual recibido:', notificacion.mensaje);
              break;
              
            case 'orden':
              console.log(`📋 Mensaje ordenado ${notificacion.secuencia}:`, notificacion.mensaje);
              break;
              
            case 'error_verificacion':
              console.warn('⚠️ Error en verificación de stock:', notificacion.mensaje);
              break;
              
            default:
              console.log('📨 Mensaje SSE genérico:', notificacion);
          }
          
          this.cdr.detectChanges();
        } catch (error) {
          console.error('❌ Error parseando JSON SSE:', error);
          console.error('Datos recibidos:', event.data);
        }
      });
    };

    // Escuchar eventos de error personalizados
    this.eventSource.addEventListener("error", (event: any) => {
      this.ngZone.run(() => {
        console.warn("⚠️ Evento SSE de error personalizado:", event.data);
        try {
          const errorData = JSON.parse(event.data);
          this.alertaMensaje = `Error SSE: ${errorData.mensaje}`;
          this.mostrarAlerta = true;
          setTimeout(() => {
            this.mostrarAlerta = false;
            this.alertaMensaje = '';
          }, 5000);
        } catch (e) {
          console.error('Error parseando evento de error:', e);
        }
      });
    });

    // Escuchar eventos de cierre
    this.eventSource.addEventListener("close", (event: any) => {
      this.ngZone.run(() => {
        console.warn("🔌 Conexión SSE cerrada por el servidor");
        try {
          const closeData = JSON.parse(event.data);
          console.log('Mensaje de cierre:', closeData.mensaje);
        } catch (e) {
          console.error('Error parseando evento de cierre:', e);
        }
        this.eventSource?.close();
      });
    });

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

  procesarNotificacionStockBajo(notificacion: any) {
        // Actualizar el producto en la lista si existe y es de la sucursal actual
        const productoIndex = this.productos.findIndex(p => p.cod_producto === notificacion.cod_producto);
        if (productoIndex !== -1 && notificacion.cod_sucursal === this.sucursalSeleccionada) {
          // Actualizar el stock del producto
          this.productos[productoIndex].unidades_p = notificacion.stock;
          
          // Si es el producto actual, actualizarlo también
          if (this.productoActual && this.productoActual.cod_producto === notificacion.cod_producto) {
            this.productoActual.unidades_p = notificacion.stock;
          }

          // Ordenar productos por stock
          this.productos = this.productos.sort((a, b) => a.unidades_p - b.unidades_p);
        }

        // Actualizar notificaciones globales
          const existe = this.notificaciones.some(n => 
            n.cod_producto === notificacion.cod_producto && 
            n.cod_sucursal === notificacion.cod_sucursal
          );
          if (!existe) {
            this.notificaciones.unshift(notificacion);
          } else {
            // Actualizar la notificación existente
            const index = this.notificaciones.findIndex(n => 
              n.cod_producto === notificacion.cod_producto && 
              n.cod_sucursal === notificacion.cod_sucursal
            );
            if (index !== -1) {
              this.notificaciones[index] = notificacion;
            }
          }

    // Actualizar el contador de alertas por sucursal
    this.actualizarContadorAlertasPorSucursal();
  }

  procesarNotificacionStockActualizado(notificacion: any) {
          // Si el stock se actualizó y ya no está bajo, eliminar la notificación
          this.notificaciones = this.notificaciones.filter(n => 
            !(n.cod_producto === notificacion.cod_producto && n.cod_sucursal === notificacion.cod_sucursal)
          );

        // Actualizar el contador de alertas por sucursal
        this.actualizarContadorAlertasPorSucursal();
  }

  actualizarNotificaciones() {
    // Obtener todas las notificaciones de todas las sucursales
    this.notificaciones = [];
    
    // Consultar cada sucursal para obtener productos con stock bajo
    this.sucursales.forEach(sucursal => {
      this.productosService.getProductosPorSucursalStock(sucursal.cod_sucursal).subscribe(productos => {
        const productosStockBajo = productos.filter(p => p.unidades_p < 10);
        
        productosStockBajo.forEach(producto => {
          const notificacion = {
            tipo: 'stock_bajo',
            producto: producto.nombre_p,
            stock: producto.unidades_p,
            cod_producto: producto.cod_producto,
            sucursal: sucursal.nombre_sucursal,
            cod_sucursal: sucursal.cod_sucursal
          };
          
          // Evitar duplicados
          const existe = this.notificaciones.some(n => 
            n.cod_producto === notificacion.cod_producto && 
            n.cod_sucursal === notificacion.cod_sucursal
          );
          
          if (!existe) {
            this.notificaciones.push(notificacion);
          }
        });
        
        this.actualizarContadorAlertasPorSucursal();
        this.cdr.detectChanges();
      });
    });
  }

  actualizarContadorAlertasPorSucursal() {
    // Limpiar contador anterior
    this.productosEnAlertaPorSucursal = {};
    
    // Contar productos en alerta por sucursal
    this.notificaciones.forEach(notificacion => {
      if (notificacion.tipo === 'stock_bajo') {
        if (!this.productosEnAlertaPorSucursal[notificacion.cod_sucursal]) {
          this.productosEnAlertaPorSucursal[notificacion.cod_sucursal] = 0;
        }
        this.productosEnAlertaPorSucursal[notificacion.cod_sucursal]++;
      }
    });
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
      cod_sucursal: this.sucursalSeleccionada,
      cantidad: this.cantidadAgregar
    }).subscribe(
      (response: any) => {
        // Actualizar el producto actual
        this.productoActual.unidades_p = response.stock_actual;
        // Actualizar el producto en la lista
        const productoIndex = this.productos.findIndex(p => p.cod_producto === this.productoActual.cod_producto);
        if (productoIndex !== -1) {
          this.productos[productoIndex].unidades_p = response.stock_actual;
        }
        this.cantidadAgregar = 0;
        this.productos = this.productos.sort((a, b) => a.unidades_p - b.unidades_p);
        // Actualizar notificaciones después de agregar stock
        this.actualizarNotificaciones();
        this.cdr.detectChanges();
        // Mostrar alerta de éxito
        this.alertaMensaje = 'Stock de producto actualizado';
        this.mostrarAlerta = true;
        setTimeout(() => {
          this.mostrarAlerta = false;
          this.alertaMensaje = '';
        }, 3000);
      },
      (error) => {
        console.error('Error al actualizar stock:', error);
        this.alertaMensaje = 'Error al actualizar stock';
        this.mostrarAlerta = true;
        setTimeout(() => {
          this.mostrarAlerta = false;
          this.alertaMensaje = '';
        }, 3000);
      }
    );
  }

  esStockBajo(producto: any): boolean {
    return producto.unidades_p < 10;
  }

  estaEnAlertas(producto: any): boolean {
    return this.notificaciones.some(n => 
      n.cod_producto === producto.cod_producto && 
      n.cod_sucursal === this.sucursalSeleccionada &&
      n.tipo === 'stock_bajo'
    );
  }
}
