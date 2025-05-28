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

  constructor(private productosService: ProductosService, private carritoService: CarritoService) {
    this.productosService.getProductos().subscribe((data: any) => {
      this.productos = data;
    });
  }

  agregar_productos_carrito(producto: any) {
    this.carritoService.agregarProducto(producto);
    console.log('Producto agregado:', producto);
  }
}
