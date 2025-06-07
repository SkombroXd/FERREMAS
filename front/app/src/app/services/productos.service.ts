import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Producto {
  cod_producto: string;
  nombre_p: string;
  precio_p: number;
  unidades_p: number;
}

@Injectable({
  providedIn: 'root'
})
export class ProductosService {

  constructor(private http: HttpClient) { }

  getProductos(): Observable<Producto[]> {
    return this.http.get<Producto[]>('http://localhost:5000/api/lista-productos');
  }
}