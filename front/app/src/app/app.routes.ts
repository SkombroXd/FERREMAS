import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
    },
    {
        path: 'home',
        loadComponent: () => import('./home/home.component').then(m => m.HomeComponent)
    },
    {
        path: 'pago',
        loadComponent: () => import('./pago/pago.component').then(m => m.PagoComponent)
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
        path: 'crearproducto',
        loadComponent: () => import('./crearproducto/crearproducto.component').then(m => m.CrearproductoComponent).catch(err => {
            console.error('Error loading crearproducto component:', err);
            return import('./home/home.component').then(m => m.HomeComponent);
        })
    },
    {
        path: '**',
        redirectTo: 'home'
    }
];
