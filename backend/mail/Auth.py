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
        domain =self.email.split("@")[-1]
        print("Finding email provider...")
        print("Domain:", domain)
        try:
            # Get MX record (Mail Exchange server)
            mx_records = dns.resolver.resolve(domain, "MX")
            print("MX Records:", mx_records)
            mx_host = str(mx_records[0].exchange).rstrip(".")
            print("MX Host:", mx_host)
            # Known email providers (predefined for faster results)
            domain2 =mx_host.split(".")[-2]+"."+  mx_host.split(".")[-1]
            known_providers = {
                "gmail.com": ("imap.gmail.com", 993, "smtp.gmail.com", 587),
                "yahoo.com": ("imap.mail.yahoo.com", 993, "smtp.mail.yahoo.com", 587),
                "outlook.com": ("outlook.office365.com", 993, "smtp.office365.com", 587),
                "icloud.com": ("imap.mail.me.com", 993, "smtp.mail.me.com", 587),
                "zoho.com": ("imap.zoho.com", 993, "smtp.zoho.com", 587),
            }

            # If domain is known, return predefined IMAP/SMTP
            if domain in known_providers:
                self.imapHost, self.imapPort, self.smtpHost, self.smtpPort = known_providers[domain]
            elif domain2 in known_providers:
                self.imapHost, self.imapPort, self.smtpHost, self.smtpPort = known_providers[domain2]
            else:
                domain =mx_host.split(".")[-2]+"."+  mx_host.split(".")[-1]
                print("Domain:", domain)
                # Common IMAP & SMTP subdomains
                imap_hosts = [f"imap.{domain}", f"mail.{domain}"]
                smtp_hosts = [f"smtp.{domain}", f"mail.{domain}"]

                # Common IMAP & SMTP ports
                imap_ports = [993, 143]
                smtp_ports = [465, 587, 25]

                # Find working IMAP server & port
                for imap_host in imap_hosts:
                    for port in imap_ports:
                        if await self.check_port(imap_host, port):
                            self.imapHost = imap_host
                            self.imapPort = port
                            break
                    if self.imapHost:
                        break

                # Find working SMTP server & port
                for smtp_host in smtp_hosts:
                    for port in smtp_ports:
                        if await self.check_port(smtp_host, port):
                            self.smtpHost = smtp_host
                            self.smtpPort = port
                            break
                    if self.smtpHost:
                        break

            return {
                "Email": self.email,
                "MX Host": mx_host,
                "IMAP Host": self.imapHost or "Not found",
                "IMAP Port": self.imapPort or "Not found",
                "SMTP Host": self.smtpHost or "Not found",
                "SMTP Port": self.smtpPort or "Not found",
            }

        except Exception as e:
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
        
        if smtp_check and imap_check:
            return {
                "Email": self.email,
                "SMTPHost": self.smtpHost,
                "SMTPPort": self.smtpPort,
                "IMAPHost": self.imapHost,
                "IMAPPort": self.imapPort,
                "Password": self.password,
                "login":True
            }
        return {
            "Email": self.email,
            "SMTPHost": self.smtpHost,
            "SMTPPort": self.smtpPort,
            "IMAPHost": self.imapHost,
            "IMAPPort": self.imapPort,
            "Password": self.password,
            "login":False
        }
