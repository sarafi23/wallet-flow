# 💰 Wallet Flow

**Aplicación web moderna para la gestión de finanzas personales**

> Sistema completo de control financiero con dashboard interactivo, gestión de transacciones, metas de ahorro y perfiles personalizables.

[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-orange.svg)](https://github.com/features/actions)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Tests](#-tests)
- [CI/CD](#-cicd)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## ✨ Características

### 📊 Dashboard Interactivo
- **Visualización en tiempo real** de balance, ingresos y gastos
- **Gráficos dinámicos** con estadísticas mensuales
- **Navegación SPA** para experiencia fluida sin recargas

### 💸 Gestión de Transacciones
- **Registro de ingresos y gastos** con categorización
- **Filtrado avanzado** por fecha, categoría y tipo
- **Categorías personalizables** con iconos y colores

### 🎯 Metas de Ahorro (Wishlist)
- **Seguimiento de objetivos** financieros
- **Barra de progreso visual** para cada meta
- **Priorización** de metas
- **Cálculo automático** de dinero faltante

### 👤 Perfiles de Usuario
- **Perfiles completos** con avatar, nombre, biografía
- **Información extendida**: pronombres, sitio web
- **Autenticación segura** con validación de contraseña
- **Temas personalizables** (oscuro/claro)

### 📱 Diseño Responsive
- **Interfaz moderna** con glassmorphism
- **Totalmente responsive** para móvil, tablet y desktop
- **Animaciones suaves** y transiciones

---

## 🛠 Tecnologías

### Backend
- **Django 5.0** - Framework web de Python
- **SQLite** - Base de datos (desarrollo)
- **Django Signals** - Lógica de negocio automatizada

### Frontend
- **HTML5** + **CSS3** + **JavaScript Vanilla**
- **Bootstrap Icons** - Iconografía
- **CSS Variables** - Sistema de temas dinámico

### DevOps
- **Docker** + **Docker Compose** - Contenerización
- **GitHub Actions** - CI/CD Pipeline
- **Git** - Control de versiones

---

## 🏗 Arquitectura

### Estructura del Proyecto

```
wallet-flow/
├── config/                 # Configuración de Django
│   ├── settings.py        # Settings principales
│   ├── urls.py            # Rutas globales
│   └── wsgi.py            # WSGI config
├── finance/                # App principal
│   ├── migrations/        # Migraciones de BD
│   ├── static/            # Assets estáticos
│   │   └── finance/
│   │       ├── css/       # Estilos
│   │       ├── js/        # Scripts
│   │       └── img/       # Imágenes
│   ├── templates/         # Templates HTML
│   │   └── finance/
│   │       ├── landing.html
│   │       ├── register.html
│   │       └── dashboard.html
│   ├── tests/             # Tests unitarios
│   │   ├── __init__.py
│   │   └── test_models.py
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Lógica de vistas
│   ├── forms.py           # Formularios
│   ├── validators.py      # Validadores custom
│   ├── signals.py         # Signals de Django
│   └── admin.py           # Panel admin
├── .github/
│   └── workflows/
│       └── ci.yml         # Pipeline CI/CD
├── Dockerfile             # Imagen Docker
├── docker-compose.yml     # Orquestación
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

### Modelos de Datos

#### Categoria
- Categorización de transacciones
- Soporte para iconos y colores

#### Transaccion
- Registro de movimientos financieros
- Relación con Usuario y Categoría
- Soft delete con campo `activo`

#### Wishlist (Metas de Ahorro)
- Objetivos financieros
- Progreso y cálculo de faltante
- Priorización de metas

#### UserProfile
- Extensión del modelo User de Django
- Avatar, biografía, preferencias
- Creación automática vía signals

---

## 🚀 Instalación

### Prerequisitos

- **Docker** y **Docker Compose** instalados
- **Git** para clonar el repositorio

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/wallet-flow.git
cd wallet-flow
```

### Paso 2: Construir y Levantar Contenedores

```bash
docker compose up --build
```

### Paso 3: Acceder a la Aplicación

Abre tu navegador en: **http://localhost:8000**

---

## 💻 Uso

### Desarrollo Local

#### Levantar el servidor
```bash
docker compose up
```

#### Detener el servidor
```bash
docker compose down
```

#### Ver logs
```bash
docker compose logs -f web
```

#### Ejecutar migraciones
```bash
docker compose exec web python manage.py migrate
```

#### Crear superusuario
```bash
docker compose exec web python manage.py createsuperuser
```

#### Acceder al shell de Django
```bash
docker compose exec web python manage.py shell
```

---

## 🧪 Tests

### Ejecutar todos los tests

```bash
docker compose exec web python manage.py test
```

### Ejecutar tests específicos

```bash
# Solo tests de modelos
docker compose exec web python manage.py test finance.tests.test_models

# Test específico
docker compose exec web python manage.py test finance.tests.test_models.UserProfileModelTest.test_get_full_name_con_datos
```

### Cobertura Actual

- ✅ **10 tests unitarios** para modelos
- ✅ **100% de cobertura** en modelos principales
- ✅ Tests de: Categoria, Transaccion, Wishlist, UserProfile

---

## 🔄 CI/CD

### Pipeline de GitHub Actions

El proyecto incluye un pipeline automatizado que se ejecuta en cada push o pull request:

#### Job 1: `test-django`
1. ✅ Checkout del código
2. ✅ Setup de Python 3.11
3. ✅ Instalación de dependencias
4. ✅ Verificación de migraciones
5. ✅ Ejecución de tests

#### Job 2: `build-docker`
1. ✅ Build de imagen Docker
2. ✅ Validación de la imagen

### Branches Monitoreados
- `main` - Rama principal
- `develop` - Rama de desarrollo

---

## 📚 Documentación Adicional

### Guía de Usuario

1. **Registro**: Crea tu cuenta en `/register`
2. **Login**: Accede con tus credenciales
3. **Dashboard**: Visualiza tu balance y estadísticas
4. **Transacciones**: Registra ingresos y gastos
5. **Metas**: Define objetivos de ahorro
6. **Perfil**: Personaliza tu información

### API Admin

Accede al panel de administración en `/admin` con credenciales de superusuario.

---

## 🤝 Contribución

### Flujo de Trabajo

1. **Fork** el repositorio
2. Crea una **branch** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'feat: Add AmazingFeature'`)
4. **Push** a la branch (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

### Convenciones de Commits

Usamos **Conventional Commits**:

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bugs
- `docs:` - Cambios en documentación
- `style:` - Formato, punto y coma faltantes, etc
- `refactor:` - Refactorización de código
- `test:` - Agregar tests
- `ci:` - Cambios en CI/CD

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [GitHub](https://github.com/tu-usuario)

---

## 🙏 Agradecimientos

- Django Framework
- Bootstrap Icons
- Docker Community
- GitHub Actions

---

## 📞 Soporte

¿Tienes preguntas o problemas?

- 📧 Email: tu-email@ejemplo.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/wallet-flow/issues)

---

**Hecho con ❤️ y ☕**
