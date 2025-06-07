import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProductosService } from '../services/productos.service';
import { CarritoService } from '../services/carrito.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  productos: any[] = [];
  mostrarAlerta: boolean = false;
  alertaMensaje: string = '';

  constructor(private productosService: ProductosService, private carritoService: CarritoService) {
    this.productosService.getProductos().subscribe((data: any) => {
      this.productos = data;
    });
  }

  agregar_productos_carrito(producto: any) {
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

    console.log('HomeComponent: Agregando producto al carrito', producto);
    this.carritoService.agregarProducto(producto);
    this.alertaMensaje = 'Producto guardado en el carrito';
    this.mostrarAlerta = true;
    setTimeout(() => {
      this.mostrarAlerta = false;
      this.alertaMensaje = '';
    }, 3000);
  }
}
