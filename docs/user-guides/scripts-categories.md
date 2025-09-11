# Audit Script Configuration Categories

## Overview

The document includes details on the list of topics used to organize the searches performed by `kpat_cli scripts`.

## Topics

The current list of topical configuration files can be displayed with the following command:
```powershell
# List available audit configuration files
kpat_cli scripts --list-audit-configs
```

![List Audit Configs](../assets/kpat-scripts-audit-configs.png)

### 1. System Information & Asset Management

| Configuration File | Purpose |
|---|---|
| `audit-sysinfo.yaml` | Basic system identification, versioning, and hardware details |

- **Script versions:** KPNIXAUDIT, KPWINAUDIT, KPMACAUDIT version checks
- **OS versions:** Linux distribution info, Windows build details, macOS version information
- **Hardware details:** BIOS information, system specifications
- **System identification:** Hostname, domain membership, basic system facts

### 2. Vulnerability Management

| Configuration File | Purpose |
|---|---|
| `audit-vuln-mgmt.yaml` | Patch management, update status, and vulnerability remediation tracking |

- **Package management:** Linux package managers (apt, yum, dnf)
- **Windows Update:** Update history, patch levels, hotfix installations
- **macOS Updates:** Software Update configurations and history
- **System maintenance:** Scheduled update jobs and automated patching

### 3. Endpoint Protection & Security Software

| Configuration File | Purpose |
|---|---|
| `audit-endpoint-protection.yaml` | Antivirus, HIDS, FIM, and other security tools |

- **Antivirus solutions:** Windows Security Center data, ClamAV (Linux)
- **HIDS/EDR tools:** CarbonBlack, CrowdStrike, OSSEC agents
- **File Integrity Monitoring:** AIDE (Linux), Tripwire configurations
- **Security agent status:** Process verification and configuration validation

### 4. Remote Access

| Configuration File | Purpose |
|---|---|
| `audit-remote-mgmt.yaml` | Remote access methods, protocols, and security configurations |

- **SSH configurations:** Server settings, encryption algorithms, authentication methods, cipher suites, key exchange algorithms, weak moduli detection
- **RDP settings:** Windows Remote Desktop configurations and encryption layers
- **VPN access:** OpenVPN and IPSec configurations including encryption settings and cipher suites
- **Remote management protocols:** Network-accessible management interfaces such as:
  - **SNMP (Simple Network Management Protocol):** Network device monitoring and configuration
  - **WinRM (Windows Remote Management):** PowerShell remoting and remote administration via WS-MAN protocol

### 5. Network Configuration & Security

| Configuration File | Purpose |
|---|---|
| `audit-network.yaml` | Network interfaces, routing, firewall, and network security settings |

- **IP addressing:** Interface configurations, IPv4/IPv6 settings
- **DNS resolution:** Nameserver configurations, resolver settings
- **Network security:** ICMP redirect settings, packet forwarding
- **Connectivity testing:** Ping tests, network reachability
- **Routing configuration:** Network routing tables and policies
- **Network intrusion detection:** Snort configurations

### 6. Auditing & Logging Configuration

| Configuration File | Purpose |
|---|---|
| `audit-logging.yaml` | Event logging, audit trails, and monitoring configurations |

- **Windows Event Log:** Audit policy settings, log retention, event log samples
- **Linux audit systems:** auditd configurations, syslog settings
- **macOS logging:** System log configurations and audit trails
- **File system auditing:** File access monitoring configurations
- **Log management:** Retention policies, log rotation, centralized logging

### 7. User Account Management & Authentication

| Configuration File | Purpose |
|---|---|
| `audit-user-auth.yaml` | User accounts, password policies, authentication controls, and identity management systems |

- **Local user accounts:** User listings, account status, password settings
- **Password policies:** Complexity requirements, aging, lockout policies
- **Authentication methods:** PAM configurations (Linux), domain authentication
- **Privileged accounts:** Administrator/root account configurations
- **Group memberships:** Administrative group assignments
- **Account security:** Blank passwords, weak authentication settings
- **Directory services:** OpenLDAP configurations, Active Directory integration, domain membership
- **Identity management:** Centralized authentication systems, identity federation mechanisms
- **Group Policy Objects:** Results from the `gpresult` command on Windows devices

### 8. System Services & Process Management

| Configuration File | Purpose |
|---|---|
| `audit-system-services.yaml` | Running services, scheduled tasks, and process configurations |

- **System services:** Service status, startup configurations, daemon settings
- **Scheduled tasks:** Cron jobs (Linux/macOS), Task Scheduler (Windows), periodic tasks
- **File sharing services:** NFS, Samba, SMB configurations
- **Network services:** SNMP, web servers, database services, anything with a Listening TCP/UDP port
- **Running Processes:** Running process lists

### 9. File System Security & Permissions

| Configuration File | Purpose |
|---|---|
| `audit-file-systems.yaml` | File permissions, encryption, and access controls |

- **World-accessible files:** World-readable/writable file detection
- **File system encryption:** FileVault (macOS), BitLocker (Windows), LUKS (Linux)
- **Permission anomalies:** Unusual file ownership or permissions
- **Sensitive file access:** Configuration file permissions, key material protection
- **Enabled file system:** Currently-supported file system kernel modules

### 10. Cryptographic Controls & PKI

| Configuration File | Purpose |
|---|---|
| `audit-crypto-policies.yaml` | Encryption configurations, certificate management, and cryptographic policies |

- **System crypto policies:** Enterprise cryptographic policy enforcement (affects OpenSSH, OpenSSL, IPSec, DNSSec, OpenJDK)

### 11. Time Synchronization

| Configuration File | Purpose |
|---|---|
| `audit-time-sync.yaml` | NTP, Chrony, AD Domain time synchronization and related log entries |

- **Network time services:** NTP, Chrony, timesyncd, and Active Directory time service status
- **Network time configurations:** Configuration settings for various network time services
- **NTP Peer Status:** Current status information for network time services

---
