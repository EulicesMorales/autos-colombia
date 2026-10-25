import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html'
})
export class App implements OnInit {

  vehiculos: any[] = [];
  placa: string = '';
  tipo: string = 'Carro';
  placaSalida: string = '';

  mostrarModal: boolean = false;
  mensajeModal: string = '';
  esError: boolean = false;

  private readonly apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.cargarVehiculos();
  }

  // ── GET /vehiculos ─────────────────────────────────────
  cargarVehiculos(): void {
    this.http.get<any[]>(`${this.apiUrl}/vehiculos`).subscribe({
      next: (data) => {
        this.vehiculos = data;
        // Forzamos a Angular a redibujar la tabla inmediatamente
        this.cdr.detectChanges(); 
      },
      error: (err) => console.error('Error al cargar vehículos', err)
    });
  }

  // ── POST /entrada ──────────────────────────────────────
  registrarEntrada(): void {
    const placaLimpia = (this.placa || '').toUpperCase().trim();

    if (!placaLimpia) {
      this.abrirModal('Debes ingresar una placa para poder registrar el vehículo.', true);
      return;
    }

    this.http.post<any>(`${this.apiUrl}/entrada`, {
      placa: placaLimpia,
      tipo_vehiculo: this.tipo
    }).subscribe({
      next: () => {
        this.abrirModal(`El vehículo con placa ${placaLimpia} ha ingresado exitosamente al parqueadero.`, false);
        this.placa = '';
        this.cargarVehiculos(); 
      },
      error: (err) => {
        const detalle = err?.error?.detail || 'Error al conectar con el servidor.';
        this.abrirModal(detalle, true);
      }
    });
  }

  // ── PUT /salida/{placa} ────────────────────────────────
  registrarSalida(): void {
    const placaLimpia = (this.placaSalida || '').toUpperCase().trim();

    if (!placaLimpia) {
      this.abrirModal('Debes ingresar la placa del vehículo que va a salir.', true);
      return;
    }

    this.http.put<any>(`${this.apiUrl}/salida/${placaLimpia}`, {}).subscribe({
      next: (res) => {
        this.abrirModal(res.mensaje, false); 
        this.placaSalida = '';
        this.cargarVehiculos(); 
      },
      error: (err) => {
        const detalle = err?.error?.detail || 'Error al conectar con el servidor.';
        this.abrirModal(detalle, true);
      }
    });
  }

  // ── Control del Modal ──────────────────────────────────
  abrirModal(mensaje: string, esError: boolean): void {
    this.mensajeModal = mensaje;
    this.esError = esError;
    this.mostrarModal = true; 
    this.cdr.detectChanges(); // Fuerza a que el modal aparezca
  }

  cerrarModal(): void {
    this.mostrarModal = false; 
    this.cdr.detectChanges(); // Fuerza a que la tabla se muestre actualizada al cerrar
  }
}