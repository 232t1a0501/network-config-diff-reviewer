# Network Config Diff - Approval Pack

**Generated:** 2026-06-13 17:06:28
**Old config:** `sample_config_old.txt`
**New config:** `sample_config_new.txt`

## 1. Risk Summary

| # | Risk Type | Line | Detail |
|---|-----------|------|--------|
| 1 | ACL Widened | `permit ip any any` | A broad 'permit ip any any' rule was added to an ACL. |
| 2 | Route Added | `ip route 172.16.0.0 255.255.0.0 10.0.1.254` | A new static route was added. |
| 3 | Peer Change | `neighbor 203.0.113.1 remote-as 65002` | A BGP neighbor's remote-as (peer AS number) was changed - this can change trust/routing relationships. |
| 4 | Peer Change | `neighbor 203.0.113.1 description PEER-ISP-A` | A BGP neighbor's description was changed. |
| 5 | Peer Change | `neighbor 203.0.113.1 remote-as 65009` | A BGP neighbor's remote-as (peer AS number) was changed - this can change trust/routing relationships. |
| 6 | Peer Change | `neighbor 203.0.113.1 description PEER-ISP-B-BACKUP` | A BGP neighbor's description was changed. |
| 7 | SNMP Change | `snmp-server community public RO` | SNMP community configuration was changed. |
| 8 | SNMP Risk | `snmp-server community public RW` | SNMP community was set to RW (read-write) - this is a significant security risk. |

## 2. AI Plain-English Review

**Overall risk level:** High

This change set widens an outbound ACL to allow all IP traffic (permit ip any any), adds a new static route to the 172.16.0.0/16 network, and modifies a BGP peering relationship by changing the neighbor's remote-as value and description. The SNMP community string was also escalated from read-only to read-write. Together these changes significantly increase the attack surface and change external routing trust relationships.

### Findings
- **ACL Widened** (`permit ip any any`) - Risk: **High**
  - A catch-all permit rule was added before the existing deny-all rule, effectively allowing all IP traffic regardless of the more specific rules above it.
  - *Recommended action:* Confirm this is intentional; if not, remove the rule or replace it with a more specific permit statement.
- **Route Added** (`ip route 172.16.0.0 255.255.0.0 10.0.1.254`) - Risk: **Medium**
  - A new route to the 172.16.0.0/16 network was added via the internal gateway 10.0.1.254, extending internal reachability.
  - *Recommended action:* Verify 172.16.0.0/16 is an authorized internal network and that the gateway is correct.
- **Peer Change** (`neighbor 203.0.113.1 remote-as 65009`) - Risk: **High**
  - The BGP neighbor's remote AS number changed from 65002 to 65009, and its description changed to PEER-ISP-B-BACKUP, indicating a change of upstream/peer provider or trust relationship.
  - *Recommended action:* Confirm with the network team that this peer change is expected and that routing policies still apply correctly to the new AS.
- **SNMP Risk** (`snmp-server community public RW`) - Risk: **High**
  - SNMP community 'public' was changed from read-only (RO) to read-write (RW), allowing remote configuration changes via SNMP with a well-known community string.
  - *Recommended action:* Revert to RO or remove the 'public' community entirely; use a strong, unique community string or SNMPv3.

**Assumptions / limitations:** This is a sample AI review generated for documentation purposes (offline sample). The live app calls the Gemini API to generate this section dynamically for any uploaded config pair.

## 3. Raw Unified Diff

```diff
--- sample_config_old.txt
+++ sample_config_new.txt
@@ -1,5 +1,5 @@
 ! ==========================================
-! Router1 Configuration - VERSION: OLD (pre-change)
+! Router1 Configuration - VERSION: NEW (post-change)
 ! ==========================================
 hostname Router1
 !
@@ -17,17 +17,19 @@
  permit tcp 10.0.1.0 0.0.0.255 any eq 443
  permit tcp 10.0.1.0 0.0.0.255 any eq 80
  permit udp 10.0.1.0 0.0.0.255 any eq 53
+ permit ip any any
  deny ip any any log
 !
 ip route 192.168.10.0 255.255.255.0 10.0.1.254
+ip route 172.16.0.0 255.255.0.0 10.0.1.254
 ip route 0.0.0.0 0.0.0.0 203.0.113.1
 !
 router bgp 65001
  bgp log-neighbor-changes
- neighbor 203.0.113.1 remote-as 65002
- neighbor 203.0.113.1 description PEER-ISP-A
+ neighbor 203.0.113.1 remote-as 65009
+ neighbor 203.0.113.1 description PEER-ISP-B-BACKUP
  neighbor 203.0.113.1 password CiscoPass123
 !
-snmp-server community public RO
+snmp-server community public RW
 !
 end
```

## 4. Approval

- [ ] Reviewed by Network Engineer
- [ ] Reviewed by Security Team
- [ ] Approved for deployment

_This pack was generated automatically as a prototype aid. Final approval must be made by a human reviewer._