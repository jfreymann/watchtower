# Caddy Reverse Proxy Configuration

Watchtower uses Caddy to terminate TLS and enforce access controls.

---

## Example Caddyfile

```bash
watchtower.local {
tls internal
encode zstd gzip

@admin_protected {
	path /events*
	path /admin/*
	not remote_ip 192.168.1.0/24
}
respond @admin_protected "Forbidden" 403

reverse_proxy 127.0.0.1:8000
```

## Restart Caddy

```bash
sudo caddy reload
```

## Notes

- tls internal uses Caddy’s built-in CA → perfect for LAN or internal networks.
- reverse_proxy ensures uvicorn stays private.
- IP fencing can include:
  - VPN subnets
  - jumpbox IPs
  - admin workstations