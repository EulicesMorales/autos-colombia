import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
    <div class="login-container">
      
      <!-- Lado Izquierdo: Imagen y Branding -->
      <div class="login-left">
        <div class="brand">
          <span class="logo-icon">🚘</span> AutosParkingColombia
        </div>
        <div class="hero-text-login">
          <h1>Piensa a lo grande.<br>Gestiona más rápido.</h1>
          <p>Administra usuarios, celdas y pagos de tu parqueadero de forma rápida, segura y en tiempo real.</p>
        </div>
      </div>

      <!-- Lado Derecho: Formulario Moderno -->
      <div class="login-right">
        <div class="login-card">
          <h2>Bienvenido de nuevo</h2>
          <p class="subtitle">Ingresa tus credenciales para acceder al sistema.</p>

          <div class="form-group">
            <label>Usuario</label>
            <input 
              type="text" 
              [(ngModel)]="username" 
              placeholder="admin / operador"
              (keyup.enter)="ingresar()">
          </div>

          <div class="form-group">
            <label>Contraseña</label>
            <input 
              type="password" 
              [(ngModel)]="password" 
              placeholder="••••••••" 
              (keyup.enter)="ingresar()">
          </div>

          <button (click)="ingresar()" class="btn-login" [disabled]="cargando">
            <span *ngIf="!cargando">Iniciar Sesión <span class="arrow">→</span></span>
            <span *ngIf="cargando">Validando... ⏳</span>
          </button>

          <p *ngIf="error" class="error-msg">❌ {{ error }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');

    .login-container {
      display: flex;
      height: 100vh;
      width: 100vw;
      font-family: 'Inter', sans-serif;
      background: #fff;
      margin: -8px;
      overflow: hidden;
    }

    /* ── Lado Izquierdo (Branding e Imagen) ── */
    .login-left {
      flex: 1.2;
      /* Mezcla la imagen del F1 con un degradado oscuro para que el texto resalte */
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%), url('/f1.jpg');
      background-size: cover;
      background-position: center;
      padding: 60px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      color: #fff;
      position: relative;
    }

    .brand {
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
      z-index: 2;
    }

    .hero-text-login {
      position: relative;
      z-index: 2;
      margin-bottom: 40px;
    }

    .hero-text-login h1 {
      font-size: 56px;
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -2px;
      margin-bottom: 20px;
    }

    .hero-text-login p {
      font-size: 18px;
      color: #cbd5e1;
      max-width: 450px;
      line-height: 1.6;
    }

    /* ── Lado Derecho (Formulario) ── */
    .login-right {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #f8fafc; /* Color de fondo gris muy suave */
    }

    .login-card {
      width: 100%;
      max-width: 420px;
      background: #fff;
      padding: 50px 40px;
      border-radius: 24px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
      border: 1px solid #e2e8f0;
      animation: slideUp 0.5s ease-out;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .login-card h2 {
      font-size: 28px;
      font-weight: 800;
      color: #0f172a;
      margin: 0 0 10px 0;
      letter-spacing: -1px;
    }

    .subtitle {
      color: #64748b;
      margin-bottom: 35px;
      font-size: 15px;
    }

    .form-group {
      margin-bottom: 24px;
    }

    .form-group label {
      display: block;
      font-size: 14px;
      font-weight: 600;
      color: #334155;
      margin-bottom: 8px;
    }

    .form-group input {
      width: 100%;
      padding: 16px;
      font-size: 15px;
      border: 2px solid #e2e8f0;
      border-radius: 12px;
      background: #f8fafc;
      box-sizing: border-box;
      transition: all 0.3s ease;
      font-family: 'Inter', sans-serif;
    }

    /* Efecto cuando el usuario hace clic en el input */
    .form-group input:focus {
      outline: none;
      border-color: #000;
      background: #fff;
      box-shadow: 0 0 0 4px rgba(0,0,0,0.05);
    }

    .btn-login {
      width: 100%;
      padding: 16px;
      background: #000;
      color: #fff;
      font-size: 16px;
      font-weight: 700;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
      transition: transform 0.2s ease, background 0.2s;
      font-family: 'Inter', sans-serif;
      margin-top: 10px;
    }

    .btn-login:hover:not([disabled]) {
      background: #1e293b;
      transform: translateY(-2px);
    }

    .btn-login:disabled {
      background: #94a3b8;
      cursor: not-allowed;
    }

    .arrow {
      font-size: 20px;
      transition: transform 0.2s;
    }

    .btn-login:hover .arrow {
      transform: translateX(5px);
    }

    .error-msg {
      color: #dc2626;
      background: #fee2e2;
      padding: 12px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      margin-top: 20px;
      text-align: center;
      animation: shake 0.4s ease-in-out;
    }

    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      25% { transform: translateX(-5px); }
      75% { transform: translateX(5px); }
    }

    /* Responsive para celulares */
    @media (max-width: 900px) {
      .login-container { flex-direction: column; }
      .login-left { display: none; }
      .login-right { padding: 20px; }
    }
  `]
})
export class LoginComponent {
  username = '';
  password = '';
  error = '';
  cargando = false; // Variable para mostrar el estado de carga

  constructor(private authService: AuthService, private router: Router) {}

  ingresar() {
    // Evitar que envíe múltiples peticiones si ya está cargando
    if (this.cargando) return;

    if (!this.username || !this.password) {
      this.error = 'Por favor, llena todos los campos';
      return;
    }
    
    this.cargando = true;
    this.error = '';

    this.authService.login({ username: this.username, password: this.password }).subscribe({
      next: (res) => {
        this.authService.setRol(res.rol);
        this.router.navigate(['/dashboard']); 
      },
      error: (err) => {
        this.error = 'Usuario o contraseña incorrectos';
        this.cargando = false;
      }
    });
  }
}