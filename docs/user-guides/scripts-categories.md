# Audit Script Configuration Categories

## Overview

The document includes details on the list of topics used to organize the searches performed by `kpat_cli scripts`.

## Topics

### 1. System Information & Asset Management
**File:** `audit-sysinfo.yaml`
**Purpose:** Basic system identification, versioning, and hardware details

**Configurations from current files:**

- **Script versions:** KPNIXAUDIT, KPWINAUDIT, KPMACAUDIT version checks
- **OS versions:** Linux distribution info, Windows build details, macOS version information
- **Hardware details:** BIOS information, system specifications
- **System identification:** Hostname, domain membership, basic system facts

### 2. Vulnerability Management
**File:** `audit-vuln-mgmt.yaml`
**Purpose:** Patch management, update status, and vulnerability remediation tracking

**Configurations from current files:**

- **Package management:** Linux package managers (apt, yum, dnf)
- **Windows Update:** Update history, patch levels, hotfix installations
- **macOS Updates:** Software Update configurations and history
- **System maintenance:** Scheduled update jobs and automated patching

### 3. Endpoint Protection & Security Software
**File:** `audit-endpoint-protection.yaml`
**Purpose:** Antivirus, HIDS, FIM, and other security tools

**Configurations from current files:**

- **Antivirus solutions:** Windows Security Center data, ClamAV (Linux)
- **HIDS/EDR tools:** CarbonBlack, CrowdStrike, OSSEC agents
- **File Integrity Monitoring:** AIDE (Linux), Tripwire configurations
- **Security agent status:** Process verification and configuration validation

**Cross-platform applicability:** All three OS families (with platform-specific tools)

### 4. Remote Access
**File:** `audit-remote-mgmt.yaml`
**Purpose:** Remote access methods, protocols, and security configurations

**Configurations from current files:**

- **SSH configurations:** Server settings, encryption algorithms, authentication methods, cipher suites, key exchange algorithms, weak moduli detection
- **RDP settings:** Windows Remote Desktop configurations and encryption layers
- **VPN access:** OpenVPN and IPSec configurations including encryption settings and cipher suites
- **Remote management protocols:** Network-accessible management interfaces such as:
  - **SNMP (Simple Network Management Protocol):** Network device monitoring and configuration
  - **WinRM (Windows Remote Management):** PowerShell remoting and remote administration via WS-MAN protocol

### 5. Network Configuration & Security
**File:** `audit-network.yaml`
**Purpose:** Network interfaces, routing, firewall, and network security settings

**Configurations from current files:**

- **IP addressing:** Interface configurations, IPv4/IPv6 settings
- **DNS resolution:** Nameserver configurations, resolver settings
- **Network security:** ICMP redirect settings, packet forwarding
- **Connectivity testing:** Ping tests, network reachability
- **Routing configuration:** Network routing tables and policies
- **Network intrusion detection:** Snort configurations

### 6. Auditing & Logging Configuration
**File:** `audit-logging.yaml`
**Purpose:** Event logging, audit trails, and monitoring configurations

**Configurations from current files:**

- **Windows Event Log:** Audit policy settings, log retention, event log samples
- **Linux audit systems:** auditd configurations, syslog settings
- **macOS logging:** System log configurations and audit trails
- **File system auditing:** File access monitoring configurations
- **Log management:** Retention policies, log rotation, centralized logging

### 7. User Account Management & Authentication
**File:** `audit-user-auth.yaml`
**Purpose:** User accounts, password policies, authentication controls, and identity management systems

**Configurations from current files:**

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
**File:** `audit-system-services.yaml`
**Purpose:** Running services, scheduled tasks, and process configurations

**Configurations from current files:**

- **System services:** Service status, startup configurations, daemon settings
- **Scheduled tasks:** Cron jobs (Linux/macOS), Task Scheduler (Windows), periodic tasks
- **File sharing services:** NFS, Samba, SMB configurations
- **Network services:** SNMP, web servers, database services, anything with a Listening TCP/UDP port
- **Running Processes:** Running process lists

### 9. File System Security & Permissions
**Purpose:** File permissions, encryption, and access controls
**File:** `audit-file-systems.yaml`

**Configurations from current files:**

- **World-accessible files:** World-readable/writable file detection
- **File system encryption:** FileVault (macOS), BitLocker (Windows), LUKS (Linux)
- **Permission anomalies:** Unusual file ownership or permissions
- **Sensitive file access:** Configuration file permissions, key material protection
- **Enabled file system:** Currently-supported file system kernel modules

### 10. Cryptographic Controls & PKI
**Purpose:** Encryption configurations, certificate management, and cryptographic policies
**File:** `audit-crypto-policies.yaml`

**Configurations from current files:**

- **System crypto policies:** Enterprise cryptographic policy enforcement (affects OpenSSH, OpenSSL, IPSec, DNSSec, OpenJDK)

### 11. Time Synchronization
**Purpose:** NTP, Chrony, AD Domain time synchronization and related log entries
**File:** `audit-time-sync.yaml`

**Configurations from current files:**

- **Network time services:** NTP, Chrony, timesyncd, and Active Directory time service status
- **Network time configurations:** Configuration settings for various network time services
- **NTP Peer Status:** Current status information for network time services

---
