import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-pagos',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
    <div style="max-width: 500px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; font-family: sans-serif;">
      <h2>Registrar Pago de Mensualidad</h2>
      <div style="margin-bottom: 10px;">
        <label>ID de la Mensualidad (Ej: 1):</label><br>
        <input type="number" [(ngModel)]="mensualidad_id" style="width: 100%; padding: 8px;">
      </div>
      <div style="margin-bottom: 10px;">
        <label>Método de Pago:</label><br>
        <select [(ngModel)]="metodo_pago" style="width: 100%; padding: 8px;">
          <option value="Efectivo">Efectivo</option>
          <option value="Transferencia">Transferencia</option>
        </select>
      </div>
      <div style="margin-bottom: 10px;">
        <label>Banco:</label><br>
        <input type="text" [(ngModel)]="banco" value="Bancolombia" style="width: 100%; padding: 8px;" readonly>
      </div>
      <button (click)="registrarPago()" style="width: 100%; padding: 10px; background: #28a745; color: white; border: none; cursor: pointer;">
        Registrar Pago
      </button>
      
      <div *ngIf="mensaje" style="margin-top: 15px; padding: 10px; background: #d4edda; color: #155724;">
        {{ mensaje }}
      </div>
      <div *ngIf="error" style="margin-top: 15px; padding: 10px; background: #f8d7da; color: #721c24;">
        {{ error }}
      </div>
    </div>
  `
})
export class PagosComponent {
  mensualidad_id = 1;
  metodo_pago = 'Transferencia';
  banco = 'Bancolombia';
  mensaje = '';
  error = '';

  constructor(private http: HttpClient) {}

  registrarPago() {
    const body = { mensualidad_id: this.mensualidad_id, metodo_pago: this.metodo_pago, banco: this.banco };
    
    this.http.post('http://127.0.0.1:8000/pagos', body).subscribe({
      next: (res: any) => {
        this.mensaje = `¡Pago exitoso! Monto: $${res.monto}. Referencia: ${res.referencia}`;
        this.error = '';
      },
      error: (err) => {
        this.error = 'Error al registrar el pago. Verifica el ID de la mensualidad.';
        this.mensaje = '';
      }
    });
  }
}