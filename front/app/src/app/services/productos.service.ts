import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ProductoInterface {
  cod_producto: string;
  nombre_p: string;
  precio_p: number;
  unidades_p: number;
  imagen_p?: string;
}

export interface SucursalInterface {
  cod_sucursal: number;
  nombre_sucursal: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProductosService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  getProductos(): Observable<ProductoInterface[]> {
    return this.http.get<ProductoInterface[]>(`${this.apiUrl}/lista-productos`);
  }

  getProductosPorSucursal(codSucursal: number): Observable<ProductoInterface[]> {
    return this.http.get<ProductoInterface[]>(`${this.apiUrl}/productos-sucursal/${codSucursal}`);
  }

  getProductosPorSucursalStock(codSucursal: number): Observable<ProductoInterface[]> {
    return this.http.get<ProductoInterface[]>(`${this.apiUrl}/productos-sucursal-stock/${codSucursal}`);
  }

  getSucursales(): Observable<SucursalInterface[]> {
    return this.http.get<SucursalInterface[]>(`${this.apiUrl}/sucursales`);
  }

  crearProducto(productoData: ProductoInterface): Observable<{exito: boolean, mensaje: string}> {
    const requestData = {
      nombreP: productoData.nombre_p,
      precioP: productoData.precio_p,
      imagen: productoData.imagen_p
    };
    
    return this.http.post<{exito: boolean, mensaje: string}>(`${this.apiUrl}/crear-producto`, requestData);
  }
}