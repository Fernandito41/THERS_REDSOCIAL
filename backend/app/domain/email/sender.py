# Puerto (interfaz) del transporte de correo. Vive en domain/ (no en
# domain/auth/) porque no es una regla de negocio de autenticación -- es una
# capacidad transversal que cualquier dominio futuro puede necesitar
# (ADR-009-password-reset-and-email-verification.md §Decisión, FASE 8 de la
# tarea: "dejar preparada la arquitectura" para otros correos más adelante).
# Mismo patrón Repository que domain/auth/repositories.py y el resto de
# puertos ya establecidos -- domain/ no conoce Resend, ni HTTP, ni ningún
# detalle de transporte; application/email/email_service.py (la capa de
# "Email Service" que orquesta contenido) depende de esta interfaz,
# infrastructure/email/ la implementa con el SDK de Resend.
#
# Deliberadamente mínimo: solo sabe enviar un correo ya armado (destinatario,
# asunto, HTML) -- no sabe nada sobre recuperación de contraseña,
# verificación de email, ni ningún otro caso de uso concreto. Esa capa de
# significado vive en application/email/email_service.py, no acá.

from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    def send(self, to_email, subject, html_body):
        """Envía un correo. `to_email` es una única dirección (string) --
        THERS no envía correos a múltiples destinatarios en esta versión.
        No devuelve nada; una falla de transporte debe propagar la excepción
        real (quien llama decide si la registra y continúa, o la deja
        fallar) -- este puerto no traga errores silenciosamente."""
