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
    this.carritoSubject.next([...this.carrito]);
  }

  limpiarCarrito() {
    this.carrito = [];
    this.actualizarCarrito();
  }

  obtenerCarrito(): any[] {
    return this.carrito;
  }
}
