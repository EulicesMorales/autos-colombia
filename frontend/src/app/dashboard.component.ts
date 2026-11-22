import { Component, OnInit, Inject, PLATFORM_ID  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router'; 
import { isPlatformBrowser } from '@angular/common';

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
  rolUsuario: string ='';

  mostrarModal: boolean = false;
  esError: boolean = false;
  mensajeModal: string = '';

  // Operacion
  placa: string = '';
  tipo: string = 'Carro';
  placaSalida: string = '';
  vehiculos: any[] = [];

  // Historial
  filtroEstado: string = 'finalizadas';
  filtroPlaca: string = '';
  filtroDesde: string = '';
  filtroHasta: string = '';
  cargandoHistorial: boolean = false;
  consultaHecha: boolean = false;
  estancias: any[] = [];

  // Usuarios y Mensualidades
  nuevoUsuario: any = { tipo_documento: 'CC', documento: '', nombre: '', telefono: '', email: '' };
  nuevoVehiculo: any = { usuario_id: null, placa: '', tipo_vehiculo: 'Carro' };
  nuevaMensualidad: any = { usuario_id: null, placa: '' };
  buscarUsuario: string = '';
  usuarios: any[] = [];
  mensualidades: any[] = [];

  // Celdas
  nuevaCelda: any = { numero: '', tipo: 'Carro' };
  celdas: any[] = [];
  resumen: any = { Disponible: 0, Ocupada: 0, Mantenimiento: 0, total: 0 };

  // Pagos (Iteración 3)
  nuevoPago: any = { mensualidad_id: null, metodo_pago: 'Transferencia', banco: 'Bancolombia' };

    constructor(
    private http: HttpClient, 
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

      ngOnInit(): void {
    // Verificamos que estemos en el navegador
    if (typeof window !== 'undefined') {
      this.rolUsuario = localStorage.getItem('rol') || 'Operador';
      
      // Usamos un pequeño retraso (0 ms) para que Angular termine de dibujar la pantalla antes de pedir los datos
      setTimeout(() => {
        this.actualizarDatos();
      }, 0);
    }
  }

  // El actualizarDatos se queda EXACTAMENTE igual
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
  }

  cerrarModal() { this.mostrarModal = false; }

  // ═══════════════ MÉTODOS DE LA API ═══════════════
    cargarVehiculos() {
    this.http.get(`${this.apiUrl}/estancias?estado=activas`).subscribe({
      next: (res: any) => { 
        // Si el backend devuelve un objeto con la lista adentro, la sacamos.
        // Si devuelve la lista directa, la usa tal cual.
        console.log("Veamos qué trae:", res);
        
        if (Array.isArray(res)) {
          this.vehiculos = res;
        } else if (res.estancias) {
          this.vehiculos = res.estancias;
        } else if (res.datos) {
          this.vehiculos = res.datos;
        } else {
          // Si no reconoce nada, asume que el objeto en sí es la lista o está vacío
          this.vehiculos = [];
        }
      },
      error: () => { this.servidorActivo = false; }
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
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al ingresar", true)
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
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al registrar salida", true)
    });
  }

  consultarEstancias() {
    this.cargandoHistorial = true;
    let url = `${this.apiUrl}/estancias?estado=${this.filtroEstado}`;
    if (this.filtroPlaca) url += `&placa=${this.filtroPlaca}`;
    
    this.http.get(url).subscribe({
      next: (res: any) => {
        this.estancias = res;
        this.cargandoHistorial = false;
        this.consultaHecha = true;
      },
      error: () => {
        this.mostrarAlerta("Error al consultar estancias", true);
        this.cargandoHistorial = false;
      }
    });
  }

  limpiarFiltros() {
    this.filtroPlaca = '';
    this.filtroDesde = '';
    this.filtroHasta = '';
    this.consultaHecha = false;
    this.estancias = [];
  }

  cargarUsuarios() {
    let url = `${this.apiUrl}/usuarios`;
    if (this.buscarUsuario) url += `?buscar=${this.buscarUsuario}`;
    this.http.get(url).subscribe({
      next: (res: any) => { this.usuarios = res; },
      error: () => this.mostrarAlerta("Error al cargar usuarios", true)
    });
  }

  crearUsuario() {
    this.http.post(`${this.apiUrl}/usuarios`, this.nuevoUsuario).subscribe({
      next: () => {
        this.mostrarAlerta("Usuario creado exitosamente", false);
        this.nuevoUsuario = { tipo_documento: 'CC', documento: '', nombre: '', telefono: '', email: '' };
        this.cargarUsuarios();
      },
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al crear usuario", true)
    });
  }

  agregarVehiculo() {
    this.http.post(`${this.apiUrl}/usuarios/${this.nuevoVehiculo.usuario_id}/vehiculos`, this.nuevoVehiculo).subscribe({
      next: () => {
        this.mostrarAlerta("Vehículo asociado exitosamente", false);
        this.nuevoVehiculo = { usuario_id: null, placa: '', tipo_vehiculo: 'Carro' };
        this.cargarUsuarios();
      },
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al asociar vehículo", true)
    });
  }

  crearMensualidad() {
    this.http.post(`${this.apiUrl}/mensualidades`, this.nuevaMensualidad).subscribe({
      next: () => {
        this.mostrarAlerta("Mensualidad creada exitosamente", false);
        this.nuevaMensualidad = { usuario_id: null, placa: '' };
        this.cargarMensualidades();
      },
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al crear mensualidad", true)
    });
  }

  cargarMensualidades() {
    this.http.get(`${this.apiUrl}/mensualidades`).subscribe({
      next: (res: any) => { 
        this.mensualidades = Array.isArray(res) ? res : (res.mensualidades || res.data || []); 
      }
    });
  }

  cancelarMensualidad(m: any) {
    if(confirm(`¿Seguro que deseas cancelar la mensualidad de ${m.nombre_usuario}?`)) {
      this.http.put(`${this.apiUrl}/mensualidades/${m.id}/cancelar`, {}).subscribe({
        next: () => { this.mostrarAlerta("Mensualidad cancelada", false); this.cargarMensualidades(); }
      });
    }
  }

  cambiarEstadoUsuario(u: any) {
    const nuevoEstado = u.estado === 'Activo' ? 'Inactivo' : 'Activo';
    this.http.put(`${this.apiUrl}/usuarios/${u.id}/estado`, { estado: nuevoEstado }).subscribe({
      next: () => { this.mostrarAlerta(`Usuario ${nuevoEstado}`, false); this.cargarUsuarios(); },
      error: () => this.mostrarAlerta("Error al cambiar estado", true)
    });
  }

  vehiculosDe(usuario_id: number) {
    const user = this.usuarios.find(u => u.id === usuario_id);
    return user ? user.vehiculos : [];
  }

  cargarCeldas() {
    this.http.get(`${this.apiUrl}/celdas`).subscribe({
      next: (res: any) => {
        console.log("Datos de celdas que llegan:", res);
        // 1. Extraemos la lista
        const listaCeldas = Array.isArray(res) ? res : (res.celdas || res.data || []);
        this.celdas = listaCeldas;

        // 2. Calculamos el resumen (por si el backend no envía el objeto "resumen")
        if (res.resumen) {
          this.resumen = res.resumen; 
        } else {
          this.resumen = {
            total: listaCeldas.length,
            Disponible: listaCeldas.filter((c: any) => c.estado === 'Disponible').length,
            Ocupada: listaCeldas.filter((c: any) => c.estado === 'Ocupada').length,
            Mantenimiento: listaCeldas.filter((c: any) => c.estado === 'Mantenimiento').length
          };
        }
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
    this.http.put(`${this.apiUrl}/celdas/${c.id}/estado`, { estado: nuevoEstado }).subscribe({
      next: () => { this.mostrarAlerta(`Celda en ${nuevoEstado}`, false); this.cargarCeldas(); },
      error: () => this.mostrarAlerta("Error al actualizar celda", true)
    });
  }

  // ═══════════════ NUEVO: REGISTRAR PAGO (ITERACIÓN 3) ═══════════════
  registrarPago() {
    if (!this.nuevoPago.mensualidad_id) return this.mostrarAlerta("Debe ingresar el ID de la mensualidad", true);
    
    this.http.post(`${this.apiUrl}/pagos`, this.nuevoPago).subscribe({
      next: (res: any) => {
        this.mostrarAlerta(`Pago registrado. Recibo: ${res.referencia}`, false);
        this.nuevoPago = { mensualidad_id: null, metodo_pago: 'Transferencia', banco: 'Bancolombia' };
      },
      error: (err) => this.mostrarAlerta(err.error?.detail || "Error al registrar el pago", true)
    });
  }
      cerrarSesion() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('rol');
    }
    this.router.navigate(['/login']);
  }
}