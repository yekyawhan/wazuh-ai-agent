# Wazuh Rules MITRE ATT&CK Coverage Matrix

This document provides a mapping of custom Wazuh rules to MITRE ATT&CK techniques, offering an overview of the detection capabilities against various adversary tactics and techniques.

## PSTool Rules (unwanted_sw.xml)

| Rule ID | Description                                     | MITRE ATT&CK ID(s) |
|---------|-------------------------------------------------|--------------------|
| 100500  | Unauthorized software started                   | T1036              |
| 100510  | Unauthorized software on ADMIN host             | T1036              |
| 100520  | Unauthorized software on HR host                | T1036              |
| 100530  | Unauthorized software on LEGAL host             | T1036              |
| 100540  | Unauthorized software on PROCUREMENT host       | T1036              |
| 100550  | Unauthorized software on CALLCENTER host        | T1036              |
| 100560  | Unauthorized software on INO host               | T1036              |
| 100570  | Unauthorized software on SOFTWARE DEVELOPMENT host | T1036              |
| 100580  | Unauthorized software on OSS host               | T1036              |
| 100590  | Unauthorized software on INFRA host             | T1036              |
| 100600  | Unauthorized software on BILLING host           | T1036              |
| 100610  | Unauthorized software on COMMERCIAL host        | T1036              |
| 100620  | Unauthorized software on CYBERSECURITY host     | T1036              |
| 100630  | Unauthorized software on SYSTEM SOLUTION host   | T1036              |
| 100640  | Unauthorized software on FINANACE host          | T1036              |
| 100650  | Unauthorized software on AON host               | T1036              |
| 100660  | Unauthorized software on DIGITAL TRANSFORMATION host | T1036              |
| 100700  | P2P File Sharing Software Detected              | T1190              |
| 100701  | Unauthorized Remote Access Tool Detected        | T1021              |
| 100702  | Cryptominer Software Detected                   | T1496              |
| 100703  | Hacking/Penetration Testing Tool Detected       | T1595              |

## Suricata Custom Rules (suricata_custom.xml)

| Rule ID | Description                                     | MITRE ATT&CK ID(s) |
|---------|-------------------------------------------------|--------------------|
| 100010  | Suricata: Possible Network Scan Detected        | T1046              |
| 100011  | Suricata: Possible C2 Communication or Data Exfiltration | T1071, T1041       |
| 100020  | Suricata: Possible DNS Tunneling Activity       | T1071.004          |
| 100030  | Suricata: Possible Lateral Movement Activity    | T1021, T1078       |

## Sysmon Custom Rules (sysmon_custom.xml)

| Rule ID | Description                                     | MITRE ATT&CK ID(s) |
|---------|-------------------------------------------------|--------------------|
| 100101  | Sysmon: Suspicious process chain detected       | T1059, T1218       |
| 100102  | Sysmon: LOLBin execution detected               | T1218, T1059       |
| 100201  | Sysmon: Unusual outbound connection to common C2/exfil port | T1071              |
| 100301  | Sysmon: Ransomware file extension created       | T1486              |
| 100401  | Sysmon: Registry Run Key modified for persistence | T1547.001          |
| 100501  | Sysmon: Possible DLL Hijacking                  | T1574.001          |
| 100602  | Sysmon: Highly suspicious process injection     | T1055              |
