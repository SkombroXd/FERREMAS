import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { PagoService } from '../services/pago.service';
import { CarritoService } from '../services/carrito.service';

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './checkout.component.html',
  styleUrl: './checkout.component.css'
})
export class CheckoutComponent implements OnInit {
  loading = true;
  error = false;
  transactionData: any = null;

  constructor(
    private router: Router,
    private pagoService: PagoService,
    private carritoService: CarritoService
  ) {}

  ngOnInit() {
    this.procesarRespuestaTransbank();
  }

  private async procesarRespuestaTransbank() {
    try {
      const token = localStorage.getItem('token_ws');
      const ordenCompra = localStorage.getItem('orden_compra');

      if (!token || !ordenCompra) {
        throw new Error('No se encontró información de la transacción');
      }

      const resultado = await this.pagoService.confirmarPago(token, ordenCompra).toPromise();
      this.transactionData = resultado;
      this.loading = false;
      
      if (resultado?.status === 'success') {
        this.carritoService.limpiarCarrito();
      }
    } catch (error) {
      console.error('Error al procesar el pago:', error);
      this.error = true;
      this.loading = false;
    }
  }

  volverAInicio() {
    this.router.navigate(['/home']);
  }
}
