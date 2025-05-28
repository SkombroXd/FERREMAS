import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class PagoService {
  private apiUrl = 'http://localhost:5000/api';
  private httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  procesarPago(productos: any[], total: number): Observable<any> {
    console.log('Enviando pago:', { productos, total });
    return this.http.post(
      `${this.apiUrl}/procesar-pago`,
      { productos, total },
      this.httpOptions
    ).pipe(
      catchError(error => {
        console.error('Error en procesarPago:', error);
        return throwError(() => error);
      })
    );
  }

  confirmarPago(token: string, ordenCompra: string): Observable<any> {
    console.log('Confirmando pago:', { token, ordenCompra });
    return this.http.post(
      `${this.apiUrl}/commit-transaction`,
      { token_ws: token, orden_compra: ordenCompra },
      this.httpOptions
    ).pipe(
      catchError(error => {
        console.error('Error en confirmarPago:', error);
        return throwError(() => error);
      })
    );
  }
} 