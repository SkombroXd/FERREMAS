import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: '',
        redirectTo: '',
        pathMatch: 'full'
    },
    {
        path: 'pago',
        loadComponent: () => import('./pago/pago.component').then(m => m.PagoComponent)
    },
    {
        path: 'home',
        loadComponent: () => import('./home/home.component').then(m => m.HomeComponent)
    },
    {
        path: 'stock',
        loadComponent: () => import('./stock/stock.component').then(m => m.StockComponent)
    },
    {
        path: 'checkout',
        loadComponent: () => import('./checkout/checkout.component').then(m => m.CheckoutComponent)
    },
    {
        path: '**',
        redirectTo: ''
    }
];
