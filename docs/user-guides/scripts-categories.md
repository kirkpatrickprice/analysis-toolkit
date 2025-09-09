# Audit Script Configuration Categories

## Overview

This document outlines a recommended reorganization of the existing audit script configurations from an OS-based grouping (Linux, Windows, macOS) to a topic-based grouping aligned with information security domains. This reorganization will improve usability by allowing auditors to focus on specific security controls across all operating systems rather than switching between OS-specific configurations.

## Current State Analysis

### Existing OS-Based Files

The current configuration structure includes 24 YAML files organized by operating system:

**Linux configurations (9 files):**
- `audit-linux.yaml` - Main Linux aggregator
- `audit-linux-logging.yaml` - Linux logging and audit configurations
- `audit-linux-network.yaml` - Network settings and connectivity
- `audit-linux-sec-tools.yaml` - Security tools and HIDS/FIM solutions
- `audit-linux-services.yaml` - System services and daemon configurations
- `audit-linux-ssh.yaml` - SSH server configurations
- `audit-linux-system.yaml` - Core system information and settings
- `audit-linux-users.yaml` - User accounts and authentication
- `audit-linux-worldfiles.yaml` - World-readable/writable files

**Windows configurations (6 files):**
- `audit-windows.yaml` - Main Windows aggregator
- `audit-windows-logging.yaml` - Windows Event Log configurations
- `audit-windows-network.yaml` - Network settings and configurations
- `audit-windows-security-software.yaml` - Antivirus and security software
- `audit-windows-system.yaml` - Core system information
- `audit-windows-users.yaml` - User accounts and password policies

**macOS configurations (6 files):**
- `audit-macos.yaml` - Main macOS aggregator
- `audit-macos-logging.yaml` - macOS logging configurations
- `audit-macos-network.yaml` - Network settings
- `audit-macos-system.yaml` - Core system information
- `audit-macos-users.yaml` - User accounts and authentication
- `audit-macos-worldfiles.yaml` - Permissions and file access

**Cross-platform files:**
- `audit-all.yaml` - Aggregator for all platforms
- `audit-vulnerability-management.yaml` - Currently empty placeholder

## Recommended Topic-Based Categories

Based on analysis of the comment fields and audit configuration purposes, the following topic-based categories are recommended:

### 1. System Information & Asset Management
**File:** `audit-sysinfo.yaml`
**Purpose:** Basic system identification, versioning, and hardware details

**Configurations from current files:**

- **Script versions:** KPNIXAUDIT, KPWINAUDIT, KPMACAUDIT version checks
- **OS versions:** Linux distribution info, Windows build details, macOS version information
- **Hardware details:** BIOS information, system specifications
- **System identification:** Hostname, domain membership, basic system facts

**Cross-platform applicability:** All three OS families

### 2. Vulnerability Management
**File:** `audit-vuln-mgmt.yaml`
**Purpose:** Patch management, update status, and vulnerability remediation tracking

**Configurations from current files:**

- **Package management:** Linux package managers (apt, yum, dnf)
- **Windows Update:** Update history, patch levels, hotfix installations
- **macOS Updates:** Software Update configurations and history
- **System maintenance:** Scheduled update jobs and automated patching

**Cross-platform applicability:** All three OS families

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

**Cross-platform applicability:** All three OS families

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

**Cross-platform applicability:** All three OS families

### 6. Auditing & Logging Configuration
**File:** `audit-logging.yaml`
**Purpose:** Event logging, audit trails, and monitoring configurations

**Configurations from current files:**

- **Windows Event Log:** Audit policy settings, log retention, event log samples
- **Linux audit systems:** auditd configurations, syslog settings
- **macOS logging:** System log configurations and audit trails
- **File system auditing:** File access monitoring configurations
- **Log management:** Retention policies, log rotation, centralized logging

**Cross-platform applicability:** All three OS families

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

**Cross-platform applicability:** All three OS families

### 8. System Services & Process Management
**File:** `audit-system-services.yaml`
**Purpose:** Running services, scheduled tasks, and process configurations

**Configurations from current files:**

- **System services:** Service status, startup configurations, daemon settings
- **Scheduled tasks:** Cron jobs (Linux/macOS), Task Scheduler (Windows), periodic tasks
- **File sharing services:** NFS, Samba, SMB configurations
- **Network services:** SNMP, web servers, database services, anything with a Listening TCP/UDP port
- **Running Processes:** Running process lists

**Cross-platform applicability:** All three OS families

### 9. File System Security & Permissions
**Purpose:** File permissions, encryption, and access controls
**File:** `audit-file-systems.yaml`

**Configurations from current files:**

- **World-accessible files:** World-readable/writable file detection
- **File system encryption:** FileVault (macOS), BitLocker (Windows), LUKS (Linux)
- **Permission anomalies:** Unusual file ownership or permissions
- **Sensitive file access:** Configuration file permissions, key material protection
- **Enabled file system:** Currently-supported file system kernel modules

**Cross-platform applicability:** All three OS families

### 10. Cryptographic Controls & PKI
**Purpose:** Encryption configurations, certificate management, and cryptographic policies
**File:** `audit-crypto-policies.yaml`

**Configurations from current files:**

- **System crypto policies:** Enterprise cryptographic policy enforcement (affects OpenSSH, OpenSSL, IPSec, DNSSec, OpenJDK)
- **SSL/TLS configurations:** Certificate stores, cipher suites, certificate management
- **Weak cryptographic implementations:** Detection of obsolete algorithms, weak key sizes, deprecated protocols

**Cross-platform applicability:** All three OS families

### 11. Time Synchronization
**Purpose:** NTP, Chrony, AD Domain time synchronization and related log entries
**File:** `audit-time-sync.yaml`

**Configurations from current files:**

- **Network time services:** NTP, Chrony, timesyncd, and Active Directory time service status
- **Network time configurations:** Configuration settings for various network time services
- **NTP Peer Status:** Current status information for network time services

**Cross-platform applicability:** All three OS families

## Implementation Recommendations

### Phase 1: Category Creation
1. Create new topic-based YAML files following the naming convention `audit-<topic>.yaml`
2. Migrate existing configurations to appropriate topic files
3. Maintain OS-specific filters within each topic using the `sys_filter` mechanism
4. Update the main `audit-all.yaml` to include topic-based files instead of OS-based files

### Phase 2: Enhanced Cross-Platform Coverage
1. Identify gaps where configurations exist for one OS but not others
2. Develop equivalent configurations for missing OS implementations
3. Standardize field naming and output formats across platforms where possible

### Phase 3: Documentation Updates
1. Update user guides to reflect topic-based organization
2. Create cross-reference documentation mapping old OS-based files to new topic files
3. Develop topic-specific audit guidance and best practices

### Benefits of Topic-Based Organization

1. **Improved Audit Efficiency:** Auditors can focus on specific control domains across all systems
2. **Better Coverage:** Ensures consistent evaluation of security controls regardless of OS
3. **Easier Maintenance:** Related configurations are grouped together for easier updates
4. **Standards Alignment:** Aligns with security frameworks (NIST, ISO 27001, CIS Controls)
5. **Reduced Redundancy:** Eliminates duplicate logic across OS-specific files
6. **Enhanced Usability:** More intuitive organization for security professionals

### Migration Strategy

The migration should maintain backward compatibility by:
- Keeping existing OS-based files as deprecated but functional
- Creating topic-based files that include appropriate OS filters
- Updating the main aggregator files to use the new structure
- Providing clear migration documentation for existing users

This reorganization will significantly improve the toolkit's usability while maintaining its comprehensive coverage across operating systems and security domains.
