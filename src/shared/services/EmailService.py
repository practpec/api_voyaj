import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional
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
            raise ValueError("SMTP_USER y SMTP_PASS deben estar configurados")
        
        # Configurar Jinja2 para templates
        self.template_env = Environment(
            loader=FileSystemLoader('src/shared/templates/emails')
        )

    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Enviar email base usando SMTP"""
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
            
            return True
            
        except Exception as e:
            raise EmailSendException(f"Error enviando email: {str(e)}")

    async def send_welcome_email(self, to_email: str, name: str, verification_code: str) -> bool:
        """Enviar email de bienvenida con código de verificación"""
        template = self.template_env.get_template('welcome.html')
        html_content = template.render(
            name=name,
            verification_code=verification_code,
            app_name="Voyaj"
        )
        
        text_content = f"""
        ¡Bienvenido a Voyaj, {name}!
        
        Para completar tu registro, verifica tu cuenta con el código: {verification_code}
        
        Este código expira en 24 horas.
        """
        
        return await self.send_email(
            to_email,
            "¡Bienvenido a Voyaj! - Verifica tu cuenta",
            html_content,
            text_content
        )

    async def send_verification_email(self, to_email: str, name: str, verification_code: str) -> bool:
        """Enviar código de verificación de email"""
        template = self.template_env.get_template('verification.html')
        html_content = template.render(
            name=name,
            verification_code=verification_code
        )
        
        text_content = f"""
        Hola {name},
        
        Tu código de verificación es: {verification_code}
        
        Este código expira en 24 horas.
        """
        
        return await self.send_email(
            to_email,
            "Código de verificación - Voyaj",
            html_content,
            text_content
        )

    async def send_password_reset_email(self, to_email: str, name: str, reset_code: str) -> bool:
        """Enviar código de recuperación de contraseña"""
        template = self.template_env.get_template('password_reset.html')
        html_content = template.render(
            name=name,
            reset_code=reset_code
        )
        
        text_content = f"""
        Hola {name},
        
        Tu código de recuperación de contraseña es: {reset_code}
        
        Este código expira en 10 minutos por seguridad.
        Si no solicitaste este cambio, ignora este email.
        """
        
        return await self.send_email(
            to_email,
            "Recuperación de contraseña - Voyaj",
            html_content,
            text_content
        )

    async def send_password_changed_email(self, to_email: str, name: str) -> bool:
        """Notificar cambio de contraseña exitoso"""
        template = self.template_env.get_template('password_changed.html')
        html_content = template.render(name=name)
        
        text_content = f"""
        Hola {name},
        
        Tu contraseña ha sido cambiada exitosamente.
        
        Si no realizaste este cambio, contacta con soporte inmediatamente.
        """
        
        return await self.send_email(
            to_email,
            "Contraseña actualizada - Voyaj",
            html_content,
            text_content
        )

    async def send_account_deleted_email(self, to_email: str, name: str) -> bool:
        """Confirmar eliminación de cuenta"""
        template = self.template_env.get_template('account_deleted.html')
        html_content = template.render(name=name)
        
        text_content = f"""
        Adiós {name},
        
        Tu cuenta en Voyaj ha sido eliminada según tu solicitud.
        Lamentamos verte partir y esperamos que hayas disfrutado tu tiempo con nosotros.
        
        ¡Que tengas increíbles aventuras!
        """
        
        return await self.send_email(
            to_email,
            "Cuenta eliminada - Voyaj",
            html_content,
            text_content
        )