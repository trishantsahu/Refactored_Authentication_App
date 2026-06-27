from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
import socks
import smtplib

class ProxySMTPBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False

        # Fetch proxy settings
        proxy_host = getattr(settings, 'PROXY_HOST', None)
        proxy_port = getattr(settings, 'PROXY_PORT', None)
        proxy_user = getattr(settings, 'PROXY_USERNAME', None)
        proxy_password = getattr(settings, 'PROXY_PASSWORD', None)

        if not proxy_host or not proxy_port:
            raise ValueError("Proxy settings are not configured correctly.")

        try:
            # Configure the proxy
            socks.set_default_proxy(
                socks.HTTP, proxy_host, int(proxy_port), username=proxy_user, password=proxy_password
            )
            socks.wrapmodule(smtplib)

            # Ensure local_hostname exists
            self.local_hostname = getattr(self, 'local_hostname', None)

            # Open the SMTP connection
            self.connection = self.connection_class(
                self.host,
                self.port,
                timeout=self.timeout,
                local_hostname=self.local_hostname,
            )
            self.connection.set_debuglevel(self.use_debugger)
            if self.use_tls:
                self.connection.starttls(keyfile=self.ssl_keyfile, certfile=self.ssl_certfile)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
