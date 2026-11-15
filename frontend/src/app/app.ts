import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

type Pestana = 'operacion' | 'historial' | 'usuarios' | 'celdas';

// Formato de placa colombiano: carro ABC123 · moto ABC12D
const RE_CARRO = /^[A-Z]{3}\d{3}$/;
const RE_MOTO = /^[A-Z]{3}\d{2}[A-Z]$/;

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html'
})
export class App implements OnInit {

  private readonly apiUrl = 'http://127.0.0.1:8000';

  pestana: Pestana = 'operacion';
  servidorActivo = false;

  // ── Operación (Iteración 1) ──
  vehiculos: any[] = [];
  placa = '';
  tipo = 'Carro';
  placaSalida = '';

  // ── Historial / consulta de estancias (RF-06 · HU-02) ──
  estancias: any[] = [];
  filtroEstado = 'finalizadas';
  filtroPlaca = '';
  filtroDesde = '';
  filtroHasta = '';
  consultaHecha = false;
  cargandoHistorial = false;

  // ── Usuarios y mensualidades ──
  usuarios: any[] = [];
  mensualidades: any[] = [];
  buscarUsuario = '';
  nuevoUsuario: any = { tipo_documento: 'CC', documento: '', nombre: '', telefono: '', email: '' };
  nuevoVehiculo: any = { usuario_id: null, placa: '', tipo_vehiculo: 'Carro' };
  nuevaMensualidad: any = { usuario_id: null, placa: '' };

  // ── Celdas ──
  celdas: any[] = [];
  resumen: any = { total: 0, Disponible: 0, Ocupada: 0, Mantenimiento: 0 };
  nuevaCelda: any = { numero: '', tipo: 'Carro' };

  // ── Modal ──
  mostrarModal = false;
  mensajeModal = '';
  esError = false;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.cargarTodo();
  }

  cambiarPestana(p: Pestana): void {
    this.pestana = p;
    this.cargarTodo();
  }

  cargarTodo(): void {
    this.cargarVehiculos();
    this.cargarCeldas();
    if (this.pestana === 'usuarios') {
      this.cargarUsuarios();
      this.cargarMensualidades();
    }
    if (this.pestana === 'historial' && this.consultaHecha) {
      this.consultarEstancias();
    }
  }

  // ═════════ Utilidades ═════════
  private normalizarPlaca(p: string): string {
    return (p || '').toUpperCase().replace(/[\s-]/g, '');
  }

  /** Devuelve un mensaje de rechazo si la placa/tipo son inválidos; null si son válidos. */
  private errorPlaca(placa: string, tipo?: string): string | null {
    if (!placa) return 'Debes ingresar la placa del vehículo.';
    if (!RE_CARRO.test(placa) && !RE_MOTO.test(placa)) {
      return `La placa '${placa}' no tiene un formato válido. Carro: ABC123 · Moto: ABC12D.`;
    }
    if (tipo === 'Carro' && !RE_CARRO.test(placa)) return `La placa ${placa} tiene formato de moto, pero el tipo es Carro.`;
    if (tipo === 'Moto' && !RE_MOTO.test(placa)) return `La placa ${placa} tiene formato de carro, pero el tipo es Moto.`;
    return null;
  }

  private mensajeError(err: any): string {
    if (err?.status === 0) {
      return 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo en http://127.0.0.1:8000.';
    }
    const d = err?.error?.detail;
    return typeof d === 'string' ? d : 'Ocurrió un error inesperado.';
  }

  private fallo = (err: any): void => this.abrirModal(this.mensajeError(err), true);

  // ═════════ Operación: entrada / salida ═════════
  cargarVehiculos(): void {
    this.http.get<any[]>(`${this.apiUrl}/vehiculos`).subscribe({
      next: (data) => { this.vehiculos = data; this.servidorActivo = true; this.cdr.detectChanges(); },
      error: () => { this.servidorActivo = false; this.cdr.detectChanges(); }
    });
  }

  registrarEntrada(): void {
    const placaLimpia = this.normalizarPlaca(this.placa);
    const error = this.errorPlaca(placaLimpia, this.tipo);
    if (error) { this.abrirModal(error, true); return; }

    this.http.post<any>(`${this.apiUrl}/entrada`, { placa: placaLimpia, tipo_vehiculo: this.tipo }).subscribe({
      next: (r) => {
        this.abrirModal(`El vehículo ${r.placa} ingresó exitosamente. Celda asignada: ${r.celda_numero}.`, false);
        this.placa = '';
        this.cargarTodo();
      },
      error: this.fallo
    });
  }

  registrarSalida(): void {
    const placaLimpia = this.normalizarPlaca(this.placaSalida);
    const error = this.errorPlaca(placaLimpia);
    if (error) { this.abrirModal(error, true); return; }

    this.http.put<any>(`${this.apiUrl}/salida/${placaLimpia}`, {}).subscribe({
      next: (res) => {
        this.abrirModal(res.mensaje, false);
        this.placaSalida = '';
        this.cargarTodo();
      },
      error: this.fallo
    });
  }

  // ═════════ Historial ═════════
  consultarEstancias(): void {
    const placaLimpia = this.normalizarPlaca(this.filtroPlaca);
    if (placaLimpia) {
      const error = this.errorPlaca(placaLimpia);
      if (error) { this.abrirModal(error, true); return; }
    }
    let url = `${this.apiUrl}/estancias?estado=${this.filtroEstado}`;
    if (placaLimpia) url += `&placa=${placaLimpia}`;
    if (this.filtroDesde) url += `&desde=${this.filtroDesde}`;
    if (this.filtroHasta) url += `&hasta=${this.filtroHasta}`;

    this.cargandoHistorial = true;
    this.http.get<any[]>(url).subscribe({
      next: (data) => { this.estancias = data; this.consultaHecha = true; this.cargandoHistorial = false; this.cdr.detectChanges(); },
      error: (err) => { this.cargandoHistorial = false; this.fallo(err); }
    });
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'finalizadas';
    this.filtroPlaca = this.filtroDesde = this.filtroHasta = '';
    this.estancias = [];
    this.consultaHecha = false;
  }

  // ═════════ Usuarios ═════════
  cargarUsuarios(): void {
    const q = this.buscarUsuario.trim() ? `?buscar=${encodeURIComponent(this.buscarUsuario.trim())}` : '';
    this.http.get<any[]>(`${this.apiUrl}/usuarios${q}`).subscribe({
      next: (d) => { this.usuarios = d; this.cdr.detectChanges(); },
      error: this.fallo
    });
  }

  crearUsuario(): void {
    this.http.post<any>(`${this.apiUrl}/usuarios`, this.nuevoUsuario).subscribe({
      next: (u) => {
        this.abrirModal(`Usuario ${u.nombre} registrado correctamente.`, false);
        this.nuevoUsuario = { tipo_documento: 'CC', documento: '', nombre: '', telefono: '', email: '' };
        this.cargarUsuarios();
      },
      error: this.fallo
    });
  }

  agregarVehiculo(): void {
    const placaLimpia = this.normalizarPlaca(this.nuevoVehiculo.placa);
    if (!this.nuevoVehiculo.usuario_id) { this.abrirModal('Selecciona el usuario titular del vehículo.', true); return; }
    const error = this.errorPlaca(placaLimpia, this.nuevoVehiculo.tipo_vehiculo);
    if (error) { this.abrirModal(error, true); return; }

    this.http.post<any>(`${this.apiUrl}/usuarios/${this.nuevoVehiculo.usuario_id}/vehiculos`,
      { placa: placaLimpia, tipo_vehiculo: this.nuevoVehiculo.tipo_vehiculo }).subscribe({
      next: () => {
        this.abrirModal(`Vehículo ${placaLimpia} asociado correctamente.`, false);
        this.nuevoVehiculo.placa = '';
        this.cargarUsuarios();
      },
      error: this.fallo
    });
  }

  cambiarEstadoUsuario(u: any): void {
    const estado = u.estado === 'Activo' ? 'Inactivo' : 'Activo';
    this.http.put<any>(`${this.apiUrl}/usuarios/${u.id}/estado`, { estado }).subscribe({
      next: () => this.cargarUsuarios(),
      error: this.fallo
    });
  }

  vehiculosDe(usuarioId: any): any[] {
    const u = this.usuarios.find((x) => x.id === usuarioId);
    return u ? u.vehiculos : [];
  }

  // ═════════ Mensualidades ═════════
  cargarMensualidades(): void {
    this.http.get<any[]>(`${this.apiUrl}/mensualidades`).subscribe({
      next: (d) => { this.mensualidades = d; this.cdr.detectChanges(); },
      error: this.fallo
    });
  }

  crearMensualidad(): void {
    if (!this.nuevaMensualidad.usuario_id || !this.nuevaMensualidad.placa) {
      this.abrirModal('Selecciona el usuario y el vehículo para la mensualidad.', true);
      return;
    }
    this.http.post<any>(`${this.apiUrl}/mensualidades`, this.nuevaMensualidad).subscribe({
      next: (m) => {
        this.abrirModal(`Mensualidad creada para ${m.placa}: $${Number(m.valor_mensual).toLocaleString('es-CO')} · vigente hasta ${m.fecha_fin}.`, false);
        this.nuevaMensualidad = { usuario_id: this.nuevaMensualidad.usuario_id, placa: '' };
        this.cargarMensualidades();
      },
      error: this.fallo
    });
  }

  cancelarMensualidad(m: any): void {
    this.http.put<any>(`${this.apiUrl}/mensualidades/${m.id}/cancelar`, {}).subscribe({
      next: () => this.cargarMensualidades(),
      error: this.fallo
    });
  }

  // ═════════ Celdas ═════════
  cargarCeldas(): void {
    this.http.get<any[]>(`${this.apiUrl}/celdas`).subscribe({
      next: (d) => { this.celdas = d; this.cdr.detectChanges(); },
      error: () => {}
    });
    this.http.get<any>(`${this.apiUrl}/celdas/resumen`).subscribe({
      next: (d) => { this.resumen = d; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  crearCelda(): void {
    this.http.post<any>(`${this.apiUrl}/celdas`, this.nuevaCelda).subscribe({
      next: (c) => {
        this.abrirModal(`Celda ${c.numero} (${c.tipo}) creada correctamente.`, false);
        this.nuevaCelda = { numero: '', tipo: 'Carro' };
        this.cargarCeldas();
      },
      error: this.fallo
    });
  }

  alternarMantenimiento(c: any): void {
    const estado = c.estado === 'Mantenimiento' ? 'Disponible' : 'Mantenimiento';
    this.http.put<any>(`${this.apiUrl}/celdas/${c.id}/estado`, { estado }).subscribe({
      next: () => this.cargarCeldas(),
      error: this.fallo
    });
  }

  // ═════════ Modal ═════════
  abrirModal(mensaje: string, esError: boolean): void {
    this.mensajeModal = mensaje;
    this.esError = esError;
    this.mostrarModal = true;
    this.cdr.detectChanges();
  }

  cerrarModal(): void {
    this.mostrarModal = false;
    this.cdr.detectChanges();
  }
}
