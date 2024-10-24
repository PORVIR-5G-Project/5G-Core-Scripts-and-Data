# UPF 


## Slices

- [**Slice01**](upf-1.yaml)
- [**Slice02**](upf-2.yaml)
- [**Slice03**](upf-3.yaml)
- [**Slice04**](upf-4.yaml)

## Config base

Config TUN in UPF 
```
ip tuntap add name ogstun mode tun
ip addr add 192.168.0.1/16 dev ogstun
ip addr add 2001:db8:cafe::1/48 dev ogstun
ip link set ogstun up
```

Enable forwarding between the interfaces.
```
### Enable IPv4/IPv6 Forwarding
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1

### Add NAT Rule
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```