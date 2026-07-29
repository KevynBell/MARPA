# MARPA-NODE-001

## Host Information

Hostname:
marpa-node-001

Operating System:
Ubuntu Server 24.04 LTS

---

## Network Configuration

### Ethernet (Primary)

Interface: enp1s0

MAC Address:
18:60:24:17:ef:be

Reserved DHCP Address:
192.168.0.251

Priority:
Primary (Metric 100)

---

### Wi-Fi (Backup)

Interface: wlp2s0

MAC Address:
54:13:79:22:ef:14

Reserved DHCP Address:
192.168.0.252

Priority:
Backup (Metric 600)

---

## Router

Gateway:
192.168.0.1

DHCP:
Reservations configured by MAC address.

---

## SSH

Primary

ssh marpa@192.168.0.251

Backup

ssh marpa@192.168.0.252

---

## Notes

- Ethernet is the preferred network interface.
- Wi-Fi remains enabled for emergency access.
- DHCP reservations prevent IP changes while avoiding static IP conflicts.
- Suspend/hibernate disabled for 24/7 server operation.
