import { Component, OnInit, Inject, PLATFORM_ID, ChangeDetectorRef } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  apiUrl = 'http://127.0.0.1:8000'; 
  pestana: string = 'operacion';
  servidorActivo: boolean = true;
  rolUsuario: string = '';

  mostrarModal: boolean = false;
  esError: boolean = false;
  mensajeModal: string = '';
  procesandoPago: boolean = false;

  // Operacion
  placa: string = '';
  tipo: string = 'Carro';
  placaSalida: string = '';
  vehiculos: any[] = [];

  // Historial
  filtroEstado: string = 'finalizadas';
  filtroPlaca: string = '';
  consultaHecha: boolean = false;
  estancias: any[] = [];

  // Usuarios y Mensualidades
  nuevoUsuario: any = { tipo_documento: 'CC', documento: '', nombre: '', telefono: '', email: '' };
  nuevaMensualidad: any = { usuario_id: null, placa: '' };
  usuarios: any[] = [];
  mensualidades: any[] = [];

  // Celdas
  nuevaCelda: any = { numero: '', tipo: 'Carro' };
  celdas: any[] = [];
  resumen: any = { Disponible: 0, Ocupada: 0, Mantenimiento: 0, total: 0 };

  // Pagos
  nuevoPago: any = { mensualidad_id: null, metodo_pago: 'Transferencia', banco: 'Bancolombia' };
  mensualidadSeleccionada: any = null; // 

  constructor(
    private http: HttpClient, 
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      if (typeof window !== 'undefined' && window.localStorage) {
        this.rolUsuario = localStorage.getItem('rol') || 'Operador';
      }
      this.actualizarDatos();
    }
  }

  actualizarDatos() {
    this.cargarVehiculos();
    this.cargarUsuarios();
    this.cargarMensualidades();
    this.cargarCeldas();
  }

  cambiarPestana(nuevaPestana: string) {
    this.pestana = nuevaPestana;
    if (nuevaPestana === 'operacion') this.cargarVehiculos();
    if (nuevaPestana === 'usuarios') { this.cargarUsuarios(); this.cargarMensualidades(); }
    if (nuevaPestana === 'celdas') this.cargarCeldas();
  }

  mostrarAlerta(mensaje: string, esError: boolean) {
    this.mensajeModal = mensaje;
    this.esError = esError;
    this.mostrarModal = true;
    this.cdr.detectChanges();
  }

  cerrarModal() { this.mostrarModal = false; }

  cerrarSesion() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('rol');
    }
    this.router.navigate(['/login']);
  }

  // ═══════════════ MÉTODOS DE LA API BLINDADOS ═══════════════

  cargarVehiculos() {
    this.http.get(`${this.apiUrl}/estancias?estado=activas`).subscribe({
      next: (res: any) => { 
        this.vehiculos = Array.isArray(res) ? res : (res.estancias || res.datos || []); 
      },
      error: (err) => { 
        this.servidorActivo = false; 
        console.error("Error cargando vehículos:", err);
      }
    });
  }

  registrarEntrada() {
    if (!this.placa || !this.tipo) return this.mostrarAlerta("Llene todos los campos", true);
    
    this.http.post(`${this.apiUrl}/estancias`, { placa: this.placa, tipo_vehiculo: this.tipo }).subscribe({
      next: () => {
        this.mostrarAlerta("Vehículo ingresado correctamente", false);
        this.placa = '';
        this.cargarVehiculos();
        this.cargarCeldas();
      },
      error: (err) => {
        console.error(err);
        this.mostrarAlerta(err.error?.detail || "Error al ingresar el vehículo", true);
      }
    });
  }

  registrarSalida() {
    if (!this.placaSalida) return this.mostrarAlerta("Ingrese la placa", true);
    
    this.http.put(`${this.apiUrl}/estancias/salida/${this.placaSalida}`, {}).subscribe({
      next: () => {
        this.mostrarAlerta("Salida registrada correctamente", false);
        this.placaSalida = '';
        this.cargarVehiculos();
        this.cargarCeldas();
      },
      error: (err) => {
        console.error(err);
        this.mostrarAlerta(err.error?.detail || "Error al registrar la salida", true);
      }
    });
  }

  consultarEstancias() {
    let url = `${this.apiUrl}/estancias?estado=${this.filtroEstado}`;
    if (this.filtroPlaca) url += `&placa=${this.filtroPlaca}`;
    
    this.http.get(url).subscribe({
      next: (res: any) => {
        this.estancias = Array.isArray(res) ? res : (res.estancias || res.datos || []);
        this.consultaHecha = true;
      },
      error: (err) => this.mostrarAlerta("Error al consultar el historial", true)
    });
  }

  cargarUsuarios() {
    let url = `${this.apiUrl}/usuarios`;
    this.http.get(url).subscribe({
      next: (res: any) => { this.usuarios = Array.isArray(res) ? res : (res.usuarios || res.datos || []); },
      error: (err) => console.error("Error cargando usuarios", err)
    });
  }

  crearUsuario() {
    this.http.post(`${this.apiUrl}/usuarios`, this.nuevoUsuario).subscribe({
      next: () => {
        this.mostrarAlerta("Usuario creado exitosamente", false);
        this.nuevoUsuario = { tipo_documento: 'CC', documento: '', nombre: '', telefono: '', email: '' };
        this.cargarUsuarios();
      },
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al crear el usuario", true)
    });
  }

  cargarMensualidades() {
    this.http.get(`${this.apiUrl}/mensualidades`).subscribe({
      next: (res: any) => { this.mensualidades = Array.isArray(res) ? res : (res.mensualidades || res.datos || []); }
    });
  }

  crearMensualidad() {
    this.http.post(`${this.apiUrl}/mensualidades`, this.nuevaMensualidad).subscribe({
      next: () => {
        this.mostrarAlerta("Mensualidad creada exitosamente", false);
        this.nuevaMensualidad = { usuario_id: null, placa: '' };
        this.cargarMensualidades();
      },
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al crear la mensualidad", true)
    });
  }

  vehiculosDe(usuario_id: number) {
    const user = this.usuarios.find(u => u.id === usuario_id);
    return user ? user.vehiculos : [];
  }

  cargarCeldas() {
    this.http.get(`${this.apiUrl}/celdas`).subscribe({
      next: (res: any) => {
        const listaCeldas = Array.isArray(res) ? res : (res.celdas || res.datos || []);
        this.celdas = listaCeldas;
        this.resumen = {
          total: listaCeldas.length,
          Disponible: listaCeldas.filter((c: any) => c.estado === 'Disponible').length,
          Ocupada: listaCeldas.filter((c: any) => c.estado === 'Ocupada').length,
          Mantenimiento: listaCeldas.filter((c: any) => c.estado === 'Mantenimiento').length
        };
      },
      error: (err) => console.error("Error cargando celdas", err)
    });
  }

  crearCelda() {
    this.http.post(`${this.apiUrl}/celdas`, this.nuevaCelda).subscribe({
      next: () => {
        this.mostrarAlerta("Celda creada", false);
        this.nuevaCelda = { numero: '', tipo: 'Carro' };
        this.cargarCeldas();
      },
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al crear celda", true)
    });
  }

  alternarMantenimiento(c: any) {
    const nuevoEstado = c.estado === 'Mantenimiento' ? 'Disponible' : 'Mantenimiento';
    
    // Hacemos la petición. Si el backend usa otro endpoint, aquí saltará el error.
    this.http.put(`${this.apiUrl}/celdas/${c.id}/estado`, { estado: nuevoEstado }).subscribe({
      next: () => { 
        this.mostrarAlerta(`Celda ${c.numero} en ${nuevoEstado}`, false); 
        this.cargarCeldas(); 
      },
      error: (err) => {
        console.error(err);
        this.mostrarAlerta(err.error?.detail || "Error al cambiar estado de la celda", true);
      }
    });
  }

     registrarPago() {
    if (!this.nuevoPago.mensualidad_id) {
      return this.mostrarAlerta("Debe seleccionar una mensualidad de la lista", true);
    }

    // Si es efectivo, forzamos el banco a "No aplica"
    if (this.nuevoPago.metodo_pago === 'Efectivo') {
      this.nuevoPago.banco = 'No aplica';
    } else if (!this.nuevoPago.banco || this.nuevoPago.banco === 'No aplica') {
      // Si es transferencia, obligamos a que sea Bancolombia
      this.nuevoPago.banco = 'Bancolombia';
    }

    this.procesandoPago = true;
    this.mostrarModal = false;

    const rolActual = this.rolUsuario;
    const metodoActual = this.nuevoPago.metodo_pago;
    const bancoActual = this.nuevoPago.banco;

    this.http.post(`${this.apiUrl}/pagos`, this.nuevoPago).subscribe({
      next: (res: any) => {
        this.mostrarAlerta(
          `Pago de $${res.monto} registrado.\nMétodo: ${metodoActual}.\nBanco: ${bancoActual}.\nAtendido por: ${rolActual}.`, 
          false
        );
        this.nuevoPago = { mensualidad_id: null, metodo_pago: 'Transferencia', banco: 'Bancolombia' };
        this.procesandoPago = false;
      },
      error: (err) => {
        const mensajeError = err.error?.detail || "Error al procesar el pago";
        this.mostrarAlerta(mensajeError, true);
        this.procesandoPago = false;
      }
    });
  }
}