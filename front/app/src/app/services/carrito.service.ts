import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CarritoService {
  private carrito: any[] = [];
  private carritoSubject = new BehaviorSubject<any[]>([]);

  constructor() {
    // Inicializar el carrito desde localStorage si existe
    const carritoGuardado = localStorage.getItem('carrito');
    if (carritoGuardado) {
      this.carrito = JSON.parse(carritoGuardado);
      this.carritoSubject.next(this.carrito);
    }

    // Escuchar cambios en localStorage para sincronización entre pestañas/ventanas
    window.addEventListener('storage', this.syncCarritoFromLocalStorage.bind(this));
  }

  getCarrito(): Observable<any[]> {
    return this.carritoSubject.asObservable();
  }

  agregarProducto(producto: any) {
    console.log('Agregando producto al carrito:', producto);
    this.carrito.push(producto);
    this.actualizarCarrito();
  }

  eliminarProducto(codProducto: string) {
    // Encontrar el índice del primer producto con ese código
    const index = this.carrito.findIndex(p => p.cod_producto === codProducto);
    if (index !== -1) {
      // Eliminar solo un producto
      this.carrito.splice(index, 1);
      this.actualizarCarrito();
    }
  }

  private actualizarCarrito() {
    // Guardar en localStorage
    localStorage.setItem('carrito', JSON.stringify(this.carrito));
    // Notificar a los suscriptores
    console.log('CarritoService: Notificando a suscriptores con:', [...this.carrito]);
    this.carritoSubject.next([...this.carrito]);
  }

  limpiarCarrito() {
    this.carrito = [];
    this.actualizarCarrito();
  }

  obtenerCarrito(): any[] {
    return this.carrito;
  }

  private syncCarritoFromLocalStorage(event: StorageEvent) {
    if (event.key === 'carrito' && event.newValue !== null) {
      console.log(`CarritoService: localStorage 'carrito' ha cambiado en otra pestaña.`);
      try {
        const nuevoCarrito = JSON.parse(event.newValue);
        // Solo actualizar si el carrito realmente ha cambiado para evitar bucles
        if (JSON.stringify(this.carrito) !== JSON.stringify(nuevoCarrito)) {
          this.carrito = nuevoCarrito;
          this.carritoSubject.next([...this.carrito]);
          console.log('CarritoService: Carrito sincronizado desde localStorage.');
        }
      } catch (e) {
        console.error('Error al parsear el carrito desde localStorage:', e);
      }
    } else if (event.key === 'carrito' && event.newValue === null) {
      // Carrito limpiado en otra pestaña
      if (this.carrito.length > 0) {
        this.carrito = [];
        this.carritoSubject.next([]);
        console.log('CarritoService: Carrito limpiado desde localStorage.');
      }
    }
  }
}
