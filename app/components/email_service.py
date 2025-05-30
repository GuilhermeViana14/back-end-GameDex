import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "supgamedex@gmail.com"  # Substitua pelo e-mail do remetente

def send_reset_password_email(to_email: str, reset_token: str):
    """
    Envia um e-mail de redefinição de senha com o link contendo o token usando SendGrid.
    """
    try:
        # Cria o link de redefinição de senha
        reset_link = f"http://localhost:8000/reset-password?token={reset_token}"

        # Configura o conteúdo do e-mail
        subject = "Redefinição de senha - GameDex"
        body = f"""
        <html>
        <body>
            <p>Olá,</p>
            <p>Você solicitou a redefinição de sua senha. Clique no link abaixo para redefinir sua senha:</p>
            <p><a href="{reset_link}">Redefinir senha</a></p>
            <p>Se você não solicitou a redefinição de senha, ignore este e-mail.</p>
            <p>Atenciosamente,<br>Equipe GameDex</p>
        </body>
        </html>
        """

        # Configura o e-mail usando SendGrid
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=body
        )

        # Envia o e-mail
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print(f"E-mail enviado com sucesso para {to_email}. Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        raise
    
    
def send_confirmation_email(to_email: str, confirmation_token: str):
    """
    Envia e-mail de confirmação de cadastro.
    """
    try:
        confirm_link = f"http://localhost:3000/confirmacao-cadastro?token={confirmation_token}"
        subject = "Confirme seu cadastro - GameDex"
        body = f"""
        <html>
        <body>
            <p>Olá,</p>
            <p>Obrigado por se cadastrar no GameDex! Confirme seu cadastro clicando no link abaixo:</p>
            <p><a href="{confirm_link}">Confirmar cadastro</a></p>
            <p>Se você não se cadastrou, ignore este e-mail.</p>
            <p>Equipe GameDex</p>
        </body>
        </html>
        """
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=body
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(f"Erro ao enviar e-mail de confirmação: {e}")
        raise