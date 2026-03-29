import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '', // landing o presentación inicial
    loadComponent: () => import('./features/landing/landing-layout/landing-layout').then((m) => m.LandingLayout),
    pathMatch: 'full',
  },
  {
    path: 'panel', // panel de control
    loadChildren: () =>
      import('./features/panel_ctrl/routes/panel_ctrl.routes').then((m) => m.PANEL_CTRL_ROUTES),
  },
  {
    path: '**', // fallback
    redirectTo: '',
    pathMatch: 'full',
  },
];
