class IPAddressMiddleware:
    """
    Middleware para obtener la dirección IP real del cliente.

    Inspecciona las cabeceras 'X-Forwarded-For' y 'X-Real-IP' que son comúnmente
    añadidas por proxies y balanceadores de carga. Si no existen, utiliza
    el valor estándar 'REMOTE_ADDR'.

    La IP resultante se almacena en `request.client_ip`.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Intenta obtener la IP desde la cabecera X-Forwarded-For.
        # Esta cabecera puede contener una lista de IPs: "client, proxy1, proxy2".
        # La IP del cliente real es la primera de la lista.
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Toma la primera IP de la lista
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Si X-Forwarded-For no está, prueba con X-Real-IP o finalmente REMOTE_ADDR.
            client_ip = request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR'))

        # Adjuntamos la IP del cliente al objeto request para fácil acceso en las vistas.
        request.client_ip = client_ip

        response = self.get_response(request)
        return response