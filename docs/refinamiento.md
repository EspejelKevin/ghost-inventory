# Ghost Inventory: Sistema de Reservas y Liberación de Inventario Expirado

Este proyecto implementa el backend crítico para un sistema de venta de boletos en vivo, enfocado en resolver el problema del **inventario fantasma**. Utiliza un mecanismo dinámico en segundo plano para garantizar que los asientos apartados por usuarios que abandonan el proceso de compra sean liberados automáticamente, manteniendo el stock real siempre disponible.

---

## 1. Historias de Usuario y Criterios de Aceptación

### Historia de Usuario 1: Apartado Temporal de Asientos
> **Como** Usuario del sistema,  
> **Quiero** seleccionar un asiento y que se reserve temporalmente,  
> **Para** asegurar mis boletos mientras ingreso mis datos de pago sin que otro usuario los gane.

*   **Criterio de Aceptación 1.1:** Cuando un usuario selecciona un asiento con estado `DISPONIBLE`, el sistema debe cambiar su estado a `RESERVADO` y generar una orden en estado `PENDIENTE`.
*   **Criterio de Aceptación 1.2:** El sistema debe iniciar un temporizador de cuenta regresiva de **8 minutos**. Durante este periodo, ningún otro usuario podrá seleccionar ni reservar este asiento.
*   **Criterio de Aceptación 1.3:** La API debe responder con el ID de la reserva y el timestamp exacto (`ISO 8601`) de la expiración.

### Historia de Usuario 2: Confirmación por Pago Exitoso
> **Como** Sistema de Reservas,  
> **Quiero** procesar la confirmación del pago de una orden,  
> **Para** consolidar la compra del asiento de forma permanente.

*   **Criterio de Aceptación 2.1:** Si se recibe la confirmación de pago exitoso (`PAGADO`) dentro del límite de los 8 minutos, el estado del asiento debe cambiar permanentemente a `VENDIDO` y la orden a `COMPLETADA`.
*   **Criterio de Aceptación 2.2:** El temporizador de expiración en segundo plano asociado a esa reserva debe ser cancelado inmediatamente para liberar recursos del sistema.

### Historia de Usuario 3: Liberación por Expiración de Tiempo
> **Como** Organizador del Evento,  
> **Quiero** que los asientos no pagados se liberen automáticamente tras 8 minutos,  
> **Para** maximizar la venta de boletos y garantizar un inventario saludable.

*   **Criterio de Aceptación 3.1:** Si transcurren los 8 minutos y la orden asociada sigue en estado `PENDIENTE`, el sistema debe cambiar el estado del asiento de vuelta a `DISPONIBLE` y la orden a `EXPIRADA`.
*   **Criterio de Aceptación 3.2:** El sistema debe ser **resiliente**: si la aplicación se reinicia o se cae, las tareas de liberación pendientes almacenadas en el JobStore persistente deben reanudarse y ejecutarse correctamente al volver a encender el servicio.

---

## 2. Refinamiento Técnico y Arquitectura Hexagonal

Para este sistema se aplica **Arquitectura Hexagonal (Ports & Adapters)**. El dominio (reglas de negocio para reservar, pagar y expirar) es completamente puro y no sabe de la existencia de FastAPI, PostgreSQL o APScheduler. La infraestructura interactúa con el dominio únicamente a través de **Puertos** (Interfaces).

### Diagrama de Arquitectura e Interacción (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Cliente / Webhook
    box LightBlue Entrada (Primary Adapters)
        participant API as FastAPI Router
        participant Worker as APScheduler Worker
    end
    box Pink Dominio y Aplicación (Core)
        participant UC as Casos de Uso<br/>(Reserve / Pay / Expire)
        participant Domain as Entidades de Dominio<br/>(Seat / Order)
    end
    box LightGreen Salida (Secondary Adapters)
        participant DB as PostgreSQL<br/>(SQLAlchemy)
        participant Cache as Redis<br/>(JobStore)
    end

    %% FLUJO 1: RESERVA TEMPORAL
    Note over Usuario, Cache: FLUJO 1: RESERVA TEMPORAL DE ASIENTOS (8 MINUTOS)
    Usuario->>API: POST /seats/{id}/reserve
    API->>UC: Execute ReserveSeatUseCase(seat_id)
    
    Note over UC, DB: Bloqueo Pesimista (Evita Race Conditions)
    UC->>DB: SELECT * FROM seats WHERE id = {id} FOR UPDATE
    DB-->>UC: Seat disponible ✓
    
    UC->>Domain: seat.reserve()
    Domain-->>UC: Estado cambiado a 'RESERVADO'
    UC->>DB: COMMIT (Guarda estado y crea Orden PENDIENTE)
    
    Note over UC, Cache: Programación Dinámica del Job
    UC->>Cache: schedule_expiration_task(job_id, ahora + 8min)
    Cache-->>Usuario: HTTP 201 Created (Expira en 8 min)

    %% FLUJO 2: CASO A - EL USUARIO PAGA A TIEMPO
    Note over Usuario, Cache: FLUJO 2: CASO A - CONFIRMACIÓN DE PAGO EXITOSO
    Usuario->>API: POST /reservations/{id}/pay
    API->>UC: Execute ConfirmPaymentUseCase(reservation_id)
    UC->>DB: SELECT * FROM orders WHERE id = {id}
    DB-->>UC: Orden PENDIENTE y Asiento RESERVADO
    UC->>Domain: seat.sell()
    Domain-->>UC: Estado cambiado a 'VENDIDO'
    UC->>DB: COMMIT (Guarda Orden COMPLETADA y Asiento VENDIDO)
    
    Note over UC, Cache: Liberación de recursos en segundo plano
    UC->>Cache: cancel_expiration_task(job_id)
    Cache-->>Usuario: HTTP 200 OK (Boleto asegurado)

    %% FLUJO 3: CASO B - EL TIEMPO EXPIRA (WORKER)
    Note over Usuario, Cache: FLUJO 3: CASO B - EXPIRACIÓN AUTOMÁTICA DEL TIEMPO
    Note over Worker, Cache: El reloj de Redis llega a 0 (8 minutos transcurridos)
    Cache->>Worker: Dispara trigger_expiration_callback(seat_id, res_id)
    Worker->>UC: Execute ExpireReservationUseCase(seat_id, res_id)
    UC->>DB: SELECT * FROM orders WHERE id = {res_id} FOR UPDATE
    
    Note over UC, DB: Validación de Seguridad (Garantiza que no pagó en el último segundo)
    alt Si la orden sigue PENDIENTE
        UC->>Domain: seat.release()
        Domain-->>UC: Estado cambiado a 'DISPONIBLE'
        UC->>DB: COMMIT (Orden EXPIRADA y Asiento DISPONIBLE)
        Note over Worker: Log: "Asiento liberado con éxito"
    else Si la orden ya cambió a COMPLETADA (Pagada)
        UC->>DB: ROLLBACK (No hace cambios)
        Note over Worker: Log: "El asiento ya fue comprado, se ignora la expiración"
    end

    %% FLUJO 4: RESILIENCIA ANTE CAÍDAS
    Note over Worker, Cache: SCENARIO: RESILIENCIA (El servidor se apaga al minuto 4 y enciende al minuto 10)
    Note over DB, Cache: Servidor Crash ❌ (RAM perdida, pero los Jobs persisten en Redis)
    Note over DB, Cache: Servidor Reboot 🔄 (APScheduler reconecta al JobStore de Redis)
    Worker->>Cache: Al arrancar, escanea tareas vencidas del pasado
    Cache-->>Worker: Retorna Job vencido (debió correr hace 2 minutos)
    Note over Worker, UC: Trigger con 'misfire_grace_time' activo -> Ejecuta flujo de expiración inmediatamente
```

---

## 3. Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Framework API:** FastAPI (Manejo asíncrono nativo de alta velocidad).
* **Programador de Tareas:** APScheduler (AsyncIOScheduler para integrarse al event loop de FastAPI).
* **Base de Datos Relacional:** PostgreSQL (Garantiza consistencia transaccional ACID).
* **Persistencia de Tareas:** Redis (Utilizado como RedisJobStore para APScheduler; si el servidor se cae, las tareas no se pierden ya que residen en memoria persistente de Redis).
* **ORM:** SQLAlchemy + Alembic (Para interactuar asíncronamente con la BD y gestionar migraciones).