# Troubleshooting

### Agent Error: WRONG_VERSION_NUMBER

Cause: Agent using TLS but collector running HTTP.

Fix: Ensure Caddy is proxying HTTPS → HTTP on 127.0.0.1:8000.

---

### Collector Error: unable to open database file

Cause: Incorrect permissions or wrong DB path.

Fix:

```bash
sudo chown watchtower/collector:watchtower/collector /opt/watchtower/collector
sudo chmod 700 /opt/watchtower/collector
```

--- 

### Caddy not serving HTTPS

Check:

```bash
sudo systemctl status caddy
sudo caddy reload
```

---

### Agent cannot resolve watchtower.local

Fix: Add host entry.

```bash
sudo sh -c 'echo "192.168.1.82 watchtower.local" >> /etc/hosts'
```

---

### No events showing

Check agent's logs:

```bash
sudo journalctl -u watchtower/agent -f
```
