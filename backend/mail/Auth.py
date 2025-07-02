import smtplib
import aioimaplib
import asyncio
import dns.resolver
import socket


class Auth:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.smtpHost = None
        self.smtpPort = None
        self.imapHost = None
        self.imapPort = None

    async def get_email_provider(self):
        """Finds the SMTP and IMAP servers for a given email address."""
        try:
            # For custom domain email servers
            self.imapHost = "server53.hostingraja.org"
            self.imapPort = 993  # SSL enabled
            self.smtpHost = "server53.hostingraja.org"
            self.smtpPort = 465  # SSL enabled
            
            return {
                "Email": self.email,
                "IMAP Host": self.imapHost,
                "IMAP Port": self.imapPort,
                "SMTP Host": self.smtpHost,
                "SMTP Port": self.smtpPort
            }
        except Exception as e:
            print(f"Error in get_email_provider: {e}")
            return {"error": str(e)}

    async def check_port(self, host, port):
        """Checks if a given host and port are reachable."""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False

    async def verify_smtp(self):
        """Verifies SMTP login."""
        if not self.smtpHost or not self.smtpPort:
            print("SMTP server not found")
            return False
        try:
            loop = asyncio.get_running_loop()
            # Use SMTP_SSL for port 465, regular SMTP for other ports
            if self.smtpPort == 465:
                server = await loop.run_in_executor(
                    None, smtplib.SMTP_SSL, self.smtpHost, self.smtpPort
                )
            else:
                server = await loop.run_in_executor(
                    None, smtplib.SMTP, self.smtpHost, self.smtpPort
                )
                await loop.run_in_executor(None, server.starttls)
            
            # Add debug logging for SMTP connection
            print(f"SMTP connection established to {self.smtpHost}")
            
            # Try login with timeout
            await asyncio.wait_for(
                loop.run_in_executor(None, server.login, self.email, self.password),
                timeout=10
            )
            print("SMTP login successful")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP authentication failed: {str(e)}")
            return False
        except asyncio.TimeoutError:
            print("SMTP login timed out")
            return False
        except Exception as e:
            print(f"SMTP verification failed: {str(e)}")
            return False

    async def verify_imap(self):
        """Verifies IMAP login."""
        if not self.imapHost or not self.imapPort:
            print("IMAP server not found")
            return False
        try:
            im = aioimaplib.IMAP4_SSL(host=self.imapHost, port=self.imapPort)
            print("IMAP connection established")
            
            # Wait for server greeting
            await im.wait_hello_from_server()
            
            # Attempt login
            login_response = await im.login(self.email, self.password)
            
            # Verify successful login
            if login_response and login_response[0] == "OK":
                print("IMAP login successful")
                return True
            else:
                print("IMAP login failed")
                return False
                
        except aioimaplib.exceptions.IMAP4Error as e:
            print(f"IMAP protocol error: {str(e)}")
            return False
        except asyncio.TimeoutError:
            print("IMAP connection timed out")
            return False
        except Exception as e:
            print(f"IMAP verification failed: {str(e)}")
            return False

    async def login(self):
        """Finds the email servers and verifies login credentials."""
        print("Starting login verification...")
        await self.get_email_provider()
        if not self.smtpHost or not self.imapHost:
            return False
        
        # Verify SMTP and IMAP login
        smtp_check = await self.verify_smtp()
        imap_check = await self.verify_imap()
        
        try:
            # If login successful
            return {
                "login": True,
                "SMTPHost": self.smtpHost,
                "IMAPHost": self.imapHost,
                "SMTPPort": self.smtpPort,
                "IMAPPort": self.imapPort,
            }
        except Exception as e:
            print("Auth.login error:", e)
            return {
                "login": False,
                "SMTPHost": self.smtpHost,
                "IMAPHost": self.imapHost,
                "SMTPPort": self.smtpPort,
                "IMAPPort": self.imapPort,
            }
