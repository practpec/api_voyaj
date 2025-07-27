# src/shared/services/EmailService.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional
from datetime import datetime
from ..exceptions.EmailExceptions import EmailSendException

class EmailService:
    def __init__(self):
        # Configuración SMTP (Gmail)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@voyaj.com")
        self.from_name = os.getenv("FROM_NAME", "Voyaj")
        
        if not self.smtp_user or not self.smtp_pass:
            print("[WARN] EmailService: SMTP_USER y SMTP_PASS no configurados - emails no se enviarán")
            self.enabled = False
        else:
            self.enabled = True
        
        # Configurar Jinja2 para templates
        try:
            self.template_env = Environment(
                loader=FileSystemLoader('src/shared/templates/emails')
            )
        except Exception as e:
            print(f"[WARN] EmailService: Error cargando templates - {e}")
            self.template_env = None

    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Enviar email base usando SMTP"""
        if not self.enabled:
            print(f"[WARN] EmailService: Email no enviado (servicio deshabilitado) - {subject} to {to_email}")
            return False
            
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Agregar contenido de texto si existe
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Agregar contenido HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            print(f"[INFO] EmailService: Email enviado exitosamente - {subject} to {to_email}")
            return True
            
        except Exception as e:
            print(f"[ERROR] EmailService: Error enviando email - {str(e)}")
            raise EmailSendException(f"Error enviando email: {str(e)}")

    async def send_welcome_email(self, to_email: str, name: str, verification_code: str) -> bool:
        """Enviar email de bienvenida con código de verificación"""
        if self.template_env:
            try:
                template = self.template_env.get_template('welcome.html')
                html_content = template.render(
                    name=name,
                    verification_code=verification_code,
                    app_name="Voyaj"
                )
            except Exception as e:
                print(f"[WARN] EmailService: Error cargando template welcome.html - {e}")
                html_content = self._get_fallback_welcome_html(name, verification_code)
        else:
            html_content = self._get_fallback_welcome_html(name, verification_code)
        
        text_content = f"""
¡Bienvenido a Voyaj, {name}!

Para completar tu registro, verifica tu cuenta con el código: {verification_code}

Este código expira en 24 horas.

Si no solicitaste esta cuenta, puedes ignorar este correo.

¡Felices viajes!
El equipo de Voyaj
        """
        
        return await self.send_email(
            to_email,
            "¡Bienvenido a Voyaj! Verifica tu cuenta",
            html_content,
            text_content
        )

    async def send_verification_email(self, to_email: str, name: str, verification_code: str) -> bool:
        """Enviar email de verificación"""
        if self.template_env:
            try:
                template = self.template_env.get_template('verification.html')
                html_content = template.render(
                    name=name,
                    verification_code=verification_code,
                    app_name="Voyaj"
                )
            except Exception as e:
                print(f"[WARN] EmailService: Error cargando template verification.html - {e}")
                html_content = self._get_fallback_verification_html(name, verification_code)
        else:
            html_content = self._get_fallback_verification_html(name, verification_code)
        
        text_content = f"""
Hola {name},

Tu código de verificación para Voyaj es: {verification_code}

Este código expira en 24 horas.

Si no solicitaste este código, puedes ignorar este correo.

El equipo de Voyaj
        """
        
        return await self.send_email(
            to_email,
            "Código de verificación - Voyaj",
            html_content,
            text_content
        )

    async def send_password_reset_email(self, to_email: str, name: str, reset_code: str) -> bool:
        """Enviar email de recuperación de contraseña"""
        if self.template_env:
            try:
                template = self.template_env.get_template('password_reset.html')
                html_content = template.render(
                    name=name,
                    reset_code=reset_code,
                    app_name="Voyaj"
                )
            except Exception as e:
                print(f"[WARN] EmailService: Error cargando template password_reset.html - {e}")
                html_content = self._get_fallback_reset_html(name, reset_code)
        else:
            html_content = self._get_fallback_reset_html(name, reset_code)
        
        text_content = f"""
Hola {name},

Recibimos una solicitud para restablecer tu contraseña en Voyaj.

Tu código de recuperación es: {reset_code}

Este código expira en 1 hora.

Si no solicitaste este cambio, ignora este correo. Tu contraseña permanecerá sin cambios.

El equipo de Voyaj
        """
        
        return await self.send_email(
            to_email,
            "Recuperar contraseña - Voyaj",
            html_content,
            text_content
        )

    async def send_password_changed_email(self, to_email: str, name: str) -> bool:
        """Enviar confirmación de cambio de contraseña"""
        timestamp = datetime.utcnow().strftime("%d/%m/%Y a las %H:%M UTC")
        
        if self.template_env:
            try:
                template = self.template_env.get_template('password_changed.html')
                html_content = template.render(
                    name=name,
                    timestamp=timestamp,
                    app_name="Voyaj"
                )
            except Exception as e:
                print(f"[WARN] EmailService: Error cargando template password_changed.html - {e}")
                html_content = self._get_fallback_changed_html(name, timestamp)
        else:
            html_content = self._get_fallback_changed_html(name, timestamp)
        
        text_content = f"""
Hola {name},

Te confirmamos que la contraseña de tu cuenta en Voyaj ha sido actualizada exitosamente el {timestamp}.

Si no realizaste este cambio, contacta inmediatamente a nuestro equipo de soporte.

El equipo de Voyaj
        """
        
        return await self.send_email(
            to_email,
            "Contraseña actualizada - Voyaj",
            html_content,
            text_content
        )

    def _get_fallback_welcome_html(self, name: str, verification_code: str) -> str:
        """HTML básico de bienvenida cuando no hay template"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
                <h1 style="color: #2563eb;">¡Bienvenido a Voyaj!</h1>
                <p>Hola <strong>{name}</strong>,</p>
                <p>¡Gracias por unirte a Voyaj! Para completar tu registro, verifica tu cuenta con este código:</p>
                <div style="background-color: #f3f4f6; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                    <h2 style="color: #2563eb; font-size: 32px; letter-spacing: 4px; margin: 0;">{verification_code}</h2>
                    <p style="color: #ef4444; margin: 10px 0 0 0;">Expira en 24 horas</p>
                </div>
                <p style="color: #6b7280; font-size: 14px;">Si no solicitaste esta cuenta, puedes ignorar este correo.</p>
                <p>¡Felices viajes! ✈️</p>
            </div>
        </body>
        </html>
        """

    def _get_fallback_verification_html(self, name: str, verification_code: str) -> str:
        """HTML básico de verificación cuando no hay template"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
                <h1 style="color: #059669;">🔐 Verificación de cuenta</h1>
                <p>Hola <strong>{name}</strong>,</p>
                <p>Tu código de verificación es:</p>
                <div style="background-color: #f0fdf4; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; border: 2px solid #10b981;">
                    <h2 style="color: #059669; font-size: 32px; letter-spacing: 4px; margin: 0;">{verification_code}</h2>
                    <p style="color: #ef4444; margin: 10px 0 0 0;">Expira en 24 horas</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _get_fallback_reset_html(self, name: str, reset_code: str) -> str:
        """HTML básico de reset cuando no hay template"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
                <h1 style="color: #dc2626;">🔑 Recuperar contraseña</h1>
                <p>Hola <strong>{name}</strong>,</p>
                <p>Tu código de recuperación es:</p>
                <div style="background-color: #fef2f2; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; border: 2px solid #ef4444;">
                    <h2 style="color: #dc2626; font-size: 28px; letter-spacing: 3px; margin: 0;">{reset_code}</h2>
                    <p style="color: #ef4444; margin: 10px 0 0 0; font-weight: bold;">Expira en 1 hora</p>
                </div>
                <p style="background-color: #fffbeb; padding: 15px; border-left: 4px solid #f59e0b; color: #92400e;">
                    <strong>Importante:</strong> Si no solicitaste este cambio, ignora este correo.
                </p>
            </div>
        </body>
        </html>
        """

    def _get_fallback_changed_html(self, name: str, timestamp: str) -> str:
        """HTML básico de cambio exitoso cuando no hay template"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
                <h1 style="color: #059669;">✅ Contraseña actualizada</h1>
                <div style="background-color: #f0fdf4; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; border: 2px solid #10b981;">
                    <h2 style="color: #059669; margin: 0;">🔐 ¡Cambio exitoso!</h2>
                </div>
                <p>Hola <strong>{name}</strong>,</p>
                <p>Tu contraseña ha sido actualizada exitosamente el <strong>{timestamp}</strong>.</p>
                <p style="background-color: #eff6ff; padding: 15px; border-left: 4px solid #2563eb; color: #374151;">
                    <strong>🛡️ Información de seguridad:</strong> Si no realizaste este cambio, contacta inmediatamente a soporte.
                </p>
            </div>
        </body>
        </html>
        """