from fastapi import Request

def get_client_ip(request: Request) -> str:
    ##We make this utility in order to get the IP address of users
    ##behind Cloudfare, regular proxies, and finally the end user.

    # Cloudflare header (most reliable if using Cloudflare)
    cloudflare_ip = request.headers.get("CF-Connecting-IP")
    if cloudflare_ip:
        return cloudflare_ip

    # Standard proxy header
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Getting the IP if connecting
    return request.client.host