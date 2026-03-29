import { Routes } from '@angular/router';
import { PanelLayout } from '../layout/panel-layout/panel-layout';
export const PANEL_CTRL_ROUTES: Routes = [
  {
    path: '',
    component: PanelLayout,
    children: [
      {
        path: '', // ruta vacía dentro del panel
        redirectTo: 'dashboard', // redirige automáticamente al dashboard
        pathMatch: 'full', // importante para rutas exactas
      },
      {
        path: 'dashboard', // /panel/dashboard
        loadComponent: () => import('../pages/dashboard/dashboard').then((m) => m.Dashboard),
      },
      {
        path: 'productos', // /panel/productos
        loadComponent: () => import('../pages/productos/productos').then((m) => m.Productos),
      },
      {
        path: 'crud', // /panel/crud
        loadComponent: () => import('../pages/crud/crud').then((m) => m.Crud),
      }
    ],
  },
];
