import { Component, OnInit, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProductosService, ProductoInterface, SucursalInterface } from '../services/productos.service';
import { CarritoService } from '../services/carrito.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit, OnDestroy {
  productos: ProductoInterface[] = [];
  sucursales: SucursalInterface[] = [];
  sucursalSeleccionada: number = 0;
  mostrarAlerta: boolean = false;
  alertaMensaje: string = '';
  cargando: boolean = false;
  private eventSource: EventSource | null = null;

  constructor(
    private productosService: ProductosService, 
    private carritoService: CarritoService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    this.cargarSucursales();
    this.iniciarEventSource();
  }

  ngOnDestroy() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  }

  iniciarEventSource() {
    if (this.eventSource) {
      this.eventSource.close();
    }
    this.eventSource = new EventSource('http://localhost:5000/api/notificaciones');
    this.eventSource.onmessage = (event) => {
      this.ngZone.run(() => {
        this.cargarProductosPorSucursal();
        this.cdr.detectChanges();
      });
    };
    this.eventSource.onerror = (error) => {
      if (this.eventSource && this.eventSource.readyState === EventSource.CLOSED) {
        setTimeout(() => this.iniciarEventSource(), 5000);
      }
    };
  }

  cargarSucursales() {
    this.productosService.getSucursales().subscribe({
      next: (sucursales) => {
        this.sucursales = sucursales;
        if (sucursales.length > 0) {
          this.sucursalSeleccionada = sucursales[0].cod_sucursal;
          this.cargarProductosPorSucursal();
        }
      },
      error: (error) => {
        console.error('Error cargando sucursales:', error);
        this.alertaMensaje = 'Error al cargar sucursales';
        this.mostrarAlerta = true;
        setTimeout(() => this.mostrarAlerta = false, 3000);
      }
    });
  }

  cargarProductosPorSucursal() {
    if (this.sucursalSeleccionada === 0) return;
    
    this.cargando = true;
    this.productosService.getProductosPorSucursal(this.sucursalSeleccionada).subscribe({
      next: (productos) => {
        this.productos = productos.sort((a, b) => a.nombre_p.localeCompare(b.nombre_p));
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error cargando productos:', error);
        this.alertaMensaje = 'Error al cargar productos';
        this.mostrarAlerta = true;
        setTimeout(() => this.mostrarAlerta = false, 3000);
        this.cargando = false;
      }
    });
  }

  onSucursalChange() {
    this.cargarProductosPorSucursal();
  }

  agregar_productos_carrito(producto: ProductoInterface) {
    if (producto.unidades_p <= 0) {
      console.log('HomeComponent: No hay stock para', producto.nombre_p);
      this.alertaMensaje = 'No hay stock disponible';
      this.mostrarAlerta = true;
      setTimeout(() => {
        this.mostrarAlerta = false;
        this.alertaMensaje = '';
      }, 3000);
      return;
    }

    // Verificar si ya hay productos en el carrito y calcular cantidad total
    const carritoActual = this.carritoService.obtenerCarrito();
    const productosEnCarrito = carritoActual.filter(p => p.cod_producto === producto.cod_producto);
    const cantidadEnCarrito = productosEnCarrito.length;
    
    if (cantidadEnCarrito >= producto.unidades_p) {
      this.alertaMensaje = `No puedes agregar más de ${producto.unidades_p} unidades de este producto`;
      this.mostrarAlerta = true;
      setTimeout(() => {
        this.mostrarAlerta = false;
        this.alertaMensaje = '';
      }, 3000);
      return;
    }

    console.log('HomeComponent: Agregando producto al carrito', producto);
    this.carritoService.agregarProducto(producto);
    this.alertaMensaje = 'Producto guardado en el carrito';
    this.mostrarAlerta = true;
    setTimeout(() => {
      this.mostrarAlerta = false;
      this.alertaMensaje = '';
    }, 3000);
  }

  getImagenUrl(imagen: any): string {
    if (!imagen) return '';
    
    // Si la imagen es base64, convertirla a URL
    if (typeof imagen === 'string' && imagen.startsWith('data:')) {
      return imagen;
    }
    
    // Si es bytes, convertir a base64
    if (imagen instanceof Uint8Array || Array.isArray(imagen)) {
      const bytes = new Uint8Array(imagen);
      const binaryString = bytes.reduce((data, byte) => data + String.fromCharCode(byte), '');
      return 'data:image/jpeg;base64,' + btoa(binaryString);
    }
    
    return '';
  }
}
