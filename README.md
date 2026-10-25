# 🏎️ Autos Colombia - Parking Management System V2.0

> Un sistema Full-Stack de nivel empresarial para la gestión en tiempo real de celdas, vehículos y facturación, diseñado con estándares SaaS y una UI/UX de vanguardia.

![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)
![Angular](https://img.shields.io/badge/Angular_18-DD0031?style=for-the-badge&logo=angular&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## 📌 Visión General del Proyecto

**Autos Colombia** es una plataforma de alta eficiencia que resuelve el problema de la gestión de inventario de celdas en parqueaderos de alto flujo. Construido sobre una arquitectura desacoplada, garantiza tiempos de respuesta ultrarrápidos y un flujo de trabajo fluido para los operadores.

### ✨ Características Principales (Features)
- 🎛️ **Dashboard Interactivo:** Tarjetas de KPIs en tiempo real (Ocupación, Disponibilidad, Estado del Servidor).
- ⚡ **Asignación Inteligente:** Lógica de entrada/salida que asigna celdas dinámicamente y calcula tarifas de forma automatizada según el tipo de vehículo (Carro/Moto).
- 🎨 **UI/UX Premium:** Interfaz con diseño *Glassmorphism*, sistema de diseño basado en Figma, fuentes Inter y feedback visual (Toasts) al usuario.
- 🔄 **Sincronización Bidireccional:** Comunicación fluida mediante REST API que asegura la persistencia de datos en PostgreSQL, incluso tras reinicios.

---

## 🏗️ Arquitectura y Tecnologías

El proyecto sigue una arquitectura Cliente-Servidor (Frontend-Backend-Database) altamente escalable:

### Frontend
* **Framework:** Angular 18 (Standalone Components, Vite).
* **Lenguaje:** TypeScript / HTML5 / CSS3 Avanzado.
* **Integración:** Consumo de API REST nativo con `fetch` y renderizado reactivo con `[(ngModel)]`.

### Backend
* **Framework:** FastAPI (Python 3).
* **Ventajas:** Validaciones nativas con Pydantic, endpoints asíncronos y documentación automática (Swagger UI).
* **Conexión:** Integración mediante CORS configurado para despliegue seguro.

### Base de Datos
* **Motor:** PostgreSQL.
* **Modelo:** Tablas relacionales para control de celdas y vehículos activos.

---

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos para desplegar el entorno de desarrollo local.

### 1. Prerrequisitos
- Node.js (v18 o superior) y npm.
- Python (3.9 o superior).
- PostgreSQL instalado y corriendo en el puerto 5432.

### 2. Configuración del Backend (FastAPI)
Abre una terminal y ejecuta:
```bash
# Activa tu entorno virtual
.\venv\Scripts\activate  # En Windows

# Instala las dependencias
pip install fastapi uvicorn psycopg2-binary sqlalchemy

# Inicia el servidor
uvicorn main:app --reload
```
> 📍 El backend estará corriendo en: `http://127.0.0.1:8000`

### 3. Configuración del Frontend (Angular)
Abre **otra** terminal y ejecuta:
```bash
# Instala los paquetes de Node
npm install

# Levanta el servidor de desarrollo
npm start
```
> 📍 La interfaz estará disponible en: `http://localhost:4200`

---

## 💡 Uso del Sistema

1. **Ingreso de Vehículo:** Dirígete a la tarjeta "NUEVO INGRESO", digita la placa (ej: `ABC-123`), selecciona el tipo y haz clic en "Autorizar Ingreso".
2. **Visualización:** Observa cómo la tabla de "Celdas Ocupadas" y los contadores (KPIs) se actualizan inmediatamente y la notificación de éxito aparece en pantalla.
3. **Salida de Vehículo:** Ve a la tarjeta "LIBERAR CELDA", ingresa la placa del vehículo a retirar, y el sistema liberará el espacio devolviendo el total a pagar en tiempo real.

---
*Desarrollado para la asignatura de Ingeniería de Software.* 💻🔥