# PENETRATION TESTING REPORT

**Document title:** Internal security assessment of NDA web infrastructure  
**Application:** Nigerian Defence Academy portal and related web services  
**Primary hostname:** `portal.test.emrad.ng`  
**Assessment windows evidenced in the materials:** 7 September 2026 and 21 September 2026  
**Report date:** 24 September 2026  
**Classification of this document:** Confidential — client distribution  

This report consolidates the materials in the assessment directory. It does not add hosts, vulnerabilities, or test results that are not supported by those materials. Scanner severity labels were reassessed. Where a result could not be confirmed, it is recorded as unverified rather than as a finding.

---

## 1. Executive Summary

An authorized internal assessment was performed against two hosts that present the hostname `portal.test.emrad.ng`, together with a separate plaintext web application served from `10.0.255.254` when that address is requested directly.

The portal on `https://portal.test.emrad.ng` is a Laravel application fronted by nginx, with three FilamentPHP panels (staff, smart academy, and academic branch). Dynamic testing confirmed a weakness in cross-site request forgery protection on the Livewire update endpoint used by those login forms. The same testing confirmed that sub-portal login responses omit the `Secure` cookie attribute, while the public site root sets it. Several higher-impact web tests were attempted and did not succeed, including Livewire snapshot tampering, unauthenticated file upload, and retrieval of environment or source-control files.

A second issue is independent of that portal. A request to `http://10.0.255.254/` returned an application titled “Cadet Login — NDA G-Branch Survey”. Its login form submits credentials to `http://10.0.255.254/login`. Session cookies on that response were set without the `Secure` attribute, and the captured response did not include HSTS. Credential interception was not performed.

The earlier host, `10.0.38.0`, is a Windows system running Apache, PHP, and MariaDB. It exposes remote desktop, SMB, RPC, and the database port in addition to HTTP and HTTPS. The web service answered on plaintext HTTP and had the HTTP `TRACE` method enabled. No authentication bypass or data access against those services was demonstrated.

Nuclei output saved in the project is empty. Nmap’s version-based CVE suggestions for OpenSSH were not validated. No critical finding is supported by the evidence.

| Severity | Confirmed findings |
|----------|--------------------|
| Critical | 0 |
| High | 1 |
| Medium | 2 |
| Low | 4 |
| Informational | 7 |

The main themes are cleartext authentication on one internal web application, inconsistent CSRF and cookie handling on the Filament panels, and an overly broad service footprint on the Windows host.

---

## 2. Assessment Overview

| Item | Detail |
|------|--------|
| Assessment objective | Identify security weaknesses in the in-scope internal web infrastructure using the scans and tests preserved in this project. |
| Assessment type | Internal, authorized vulnerability assessment with targeted dynamic testing of the portal. The portal exercise is described in the test notes as black-box. |
| Assessment period | `10.0.38.0` was scanned on 7 September 2026. `10.0.255.254` and `https://portal.test.emrad.ng` were scanned and dynamically tested on 21 September 2026. |
| Tester / team | No tester name or engagement letter is present in the project materials. |
| Client / organization | The application content, certificate subject, and test notes identify the Nigerian Defence Academy portal in an EMRAD test environment (`portal.test.emrad.ng`, organization name EMRAD). |
| Target environment | Private IPv4 addresses `10.0.255.254` and `10.0.38.0`. |
| Testing methodology | Service discovery, web and TLS enumeration, automated web scanning, and targeted request/response testing of the portal. See Section 4. |
| Testing limitations | See below. |

**Limitations**

- No statement of work, rules of engagement, or credential pack was included. Authenticated testing of portal roles was not completed.
- Injection testing of `/search`, the contact form, and login fields was recorded as not finished.
- Account lockout and login rate limiting were not fully confirmed. Search responses did expose rate-limit headers.
- Database, SMB, and RDP services were enumerated. Authentication was not attempted in the preserved results, and no successful login is recorded.
- Denial-of-service checks were not executed. The Slowloris result is a scanner heuristic only.
- OpenSSH CVE names come from version matching. Package-level patch status was not verified.
- `NDAnuclei.json` contains an empty array. No Nuclei findings are available to correlate.
- ZAP reports include Mozilla Firefox configuration hosts contacted by the scanner browser. Those hosts are out of scope and are excluded from the findings.
- Two different software stacks answered for the same hostname on different dates. They are reported as separate assets.
- Recommended `sslscan` and `ffuf` commands appear in an Nmap recon note. Their output files are not in the project, so those tools are not treated as having been run.

---

## 3. Scope

| Target | IP Address | Hostname | Ports/Services | Notes |
|--------|------------|----------|----------------|-------|
| Linux web / SSH host | 10.0.255.254 | `portal.test.emrad.ng` (certificate SAN also contains this IP) | 22/tcp SSH; 53/tcp DNS; 80/tcp HTTP; 443/tcp HTTPS | VMware guest. Scanned 21 September 2026. Direct requests to the IP on port 80 served a different application from the hostname portal. |
| Windows web host | 10.0.38.0 | `portal.test.emrad.ng` (certificate CN) | 80/tcp HTTP; 135/tcp MSRPC; 139/tcp NetBIOS; 443/tcp HTTPS; 445/tcp SMB; 3306/tcp MariaDB; 3389/tcp RDP | Scanned 7 September 2026. Apache, PHP, and MariaDB. |
| Portal URL | 10.0.255.254 in the 21 September notes | `portal.test.emrad.ng` | 443/tcp HTTPS | Laravel / FilamentPHP / Livewire application tested dynamically on 21 September 2026. |

Names such as `www.nda.edu.ng`, `portals.nda.edu.ng`, and other `emrad.ng` hostnames appear only in notes or in a sitemap URL. They were not vulnerability-scanned in the preserved evidence and are not in-scope findings.

---

## 4. Methodology

The activities below are limited to techniques that left evidence in the project.

1. **Reconnaissance.** Hostname and certificate collection, `robots.txt` review, and technology identification from headers, titles, cookies, and static assets.
2. **Network and service enumeration.** Nmap 7.99, including a top-ports scan, a full TCP scan of `10.0.255.254`, service and version detection, and a UDP top-1000 scan. `nmapAutomator` wrapped several of these runs.
3. **Web application enumeration.** HTTP titles, robots entries, Nikto, and ZAP crawling of the portal and of `http://10.0.38.0`.
4. **Automated vulnerability scanning.** OWASP ZAP 2.17.0, Nikto, Nmap `vuln` and `vulners` scripts, and a Nuclei results file that contains no findings.
5. **Security configuration assessment.** TLS certificate fields, cookie flags, security headers, HTTP methods, and exposed administrative ports.
6. **Vulnerability validation.** Strix dynamic testing against `https://portal.test.emrad.ng` on 21 September 2026, including Livewire CSRF behaviour, cookie flags, sensitive-path requests, and negative tests of snapshot tampering and unauthenticated upload. ZAP and Nmap results were correlated with those tests and were not all re-executed.
7. **Evidence collection.** Nmap text output, Nikto HTML, ZAP HTML, and the Strix vulnerability write-ups and SARIF file.
8. **Risk assessment.** Severity in this report is based on what the evidence shows, including whether a condition was only fingerprinted.
9. **Reporting.** Deduplicated findings in this document.

Subfinder is mentioned in the portal recon notes. Raw Subfinder output is not stored here, so those names are not treated as verified scan results.

---

## 5. Tools Used

| Tool | Purpose | Evidence Found |
|------|---------|----------------|
| Nmap 7.99 | Port, service, version, NSE vulnerability, and TLS certificate checks | `10.0.255.254/nmap/`, `10.0.38.0/nmap/`, and the `nmapAutomator_*.txt` summaries |
| nmapAutomator | Wrapper that launched the Nmap phases | `nmapAutomator_10.0.255.254_all.txt`, `nmapAutomator_10.0.255.254_vulns.txt`, `nmapAutomator_10.0.38.0_vulns.txt` |
| OWASP ZAP 2.17.0 | Passive and active web scanning | `NDA-.html` (7 September 2026, `http://10.0.38.0`); `NDA-ZAP-Report-.html` and `10.0.255.254-ZAP-Report-.html` (21 September 2026) |
| Nikto | Web server checks | `htm.htm` (`10.0.38.0:443`); `10.0.255.htm`, `nda-new.htm`, `ndaold.htm` (port 80 on `10.0.255.254` / `portal.test.emrad.ng`) |
| Nuclei | Template-based vulnerability scan | `NDAnuclei.json` contains `[]` only |
| Strix | Dynamic black-box testing of the portal, with recorded HTTP results | `portal-test-emrad-ng_f4af/` (`vulnerabilities/`, `findings.sarif`, `strix.log`, `run.json`). Run window 21 September 2026, 12:17–13:22 UTC |

ZAP reports also list Firefox settings hosts. Those contacts are scanner noise and are not application findings.

---

## 6. Attack Surface / Reconnaissance Results

### 6.1 Hosts

| IP | Observed role | Operating system evidence | Hardware address |
|----|----------------|---------------------------|------------------|
| 10.0.255.254 | nginx web server, OpenSSH, and a DNS listener | Linux; OpenSSH banner `OpenSSH 10.0p2 Ubuntu 5ubuntu5.4`; CPE `cpe:/o:linux:linux_kernel` | `00:0C:29:E0:10:DD` (VMware) |
| 10.0.38.0 | Apache/PHP site plus Windows administrative services | Windows; CPE `cpe:/o:microsoft:windows`. Service fingerprint on 3389 matched a Terminal Server cookie | Not recorded |

Latency in the scans was low (tens to hundreds of milliseconds), consistent with an internal path.

### 6.2 Ports and services

**10.0.255.254 (21 September 2026)**

| Port | State | Service | Version evidence |
|------|--------|---------|------------------|
| 22/tcp | open | ssh | OpenSSH 10.0p2 Ubuntu 5ubuntu5.4 (protocol 2.0) |
| 53/tcp | open | domain | One service scan reported `Mikrotik dnsd`. A dedicated rescan of port 53 did not repeat that version string. Treat the product name as unconfirmed. |
| 80/tcp | open | http | nginx. Requesting the IP returned the cadet survey application. |
| 443/tcp | open | ssl/http | nginx. Nmap’s title when connecting without the portal hostname was `An Error Occurred: Bad Request`. |
| UDP top 1000 | open\|filtered | — | No UDP service was confirmed. |

The full TCP scan reported 65,531 filtered ports and these four open ports.

**10.0.38.0 (7 September 2026)**

| Port | State | Service | Version evidence |
|------|--------|---------|------------------|
| 80/tcp | open | http | Apache httpd 2.4.58 (OpenSSL/3.1.3 PHP/8.2.12). Banner: `Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12` |
| 135/tcp | open | msrpc | Microsoft Windows RPC |
| 139/tcp | open | netbios-ssn | Microsoft Windows netbios-ssn |
| 443/tcp | open | ssl/http | Same Apache/PHP banner. Nmap reported `TRACE` enabled. |
| 445/tcp | open | microsoft-ds | Service not fully identified (`microsoft-ds?`). SMB vulnerability scripts did not complete a negotiation. |
| 3306/tcp | open | mysql | `MariaDB 10.3.23 or earlier (unauthorized)`. In Nmap this label means a pre-authentication greeting was read. It is not evidence of anonymous database access. |
| 3389/tcp | open | ms-wbt-server | Responded to a Terminal Server cookie probe. Build was not identified. |

The top-ports scan reported 913 closed and 80 filtered TCP ports besides the open set. A full 65,535-port scan of this host was not preserved.

### 6.3 Web applications

**Portal (`https://portal.test.emrad.ng`)**

| Item | Evidence |
|------|----------|
| Server | nginx. Version string not disclosed on this host. |
| Application | Laravel. Cookies `academy-website-session` and `XSRF-TOKEN`. Health path `/up` recorded in notes. |
| Admin UI | FilamentPHP 3.3.54.0, from asset query strings such as `/js/filament/support/support.js?v=3.3.54.0` and `/css/filament/forms/forms.css?v=3.3.54.0`. |
| Client behaviour | Livewire v3 (`POST /livewire/update`, `wire:snapshot`), Alpine.js, Inertia.js on the public site, Vite assets under `/build/assets/`. |
| Panels | `/staff-login/login`, `/smart-academy/login`, `/academic-branch/login`. Unauthenticated requests to paths such as `/smart-academy/users` and `/academic-branch/users` returned redirects to login. |
| Public routes recorded | `/`, `/about`, `/contact`, `/news`, `/events`, `/search`, `/academics`, `/admissions`, `/robots.txt`, `/sitemap.xml`, `/build/manifest.json`. |
| `robots.txt` | Disallow: `/smart-academy/`, `/academic-branch/`, `/staff-login/`, `/search`. Sitemap referenced `https://www.nda.edu.ng/sitemap.xml`. |

**Cadet survey (direct IP on 10.0.255.254:80)**

| Item | Evidence |
|------|----------|
| Title | `Cadet Login — NDA G-Branch Survey` |
| Server | `nginx` |
| Login | `POST http://10.0.255.254/login` with email, password, remember-me, and a hidden `_token` field |
| Cookies | `XSRF-TOKEN` (`SameSite=Lax`, no `Secure`, no `HttpOnly` in the captured header); `surveyapplication-session` (`HttpOnly`, `SameSite=Lax`, no `Secure`) |
| Headers present | `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, `Cache-Control: no-cache, private` |
| Headers absent in the captured response | `Strict-Transport-Security` was not in the ZAP response headers |

The email field placeholder in that page is `30292@nda.edu.ng`. That value is a form placeholder, not a confirmed account.

**10.0.38.0**

ZAP retrieved application HTML over `http://10.0.38.0`, including a search form whose action is `https://portal.test.emrad.ng/search`. Nikto against `https://10.0.38.0:443` recorded the same Apache/PHP banner, `X-Powered-By: PHP/8.2.12`, rate-limit headers, and `robots.txt`. The two hosts are therefore related by hostname and application family, but they are not the same server.

### 6.4 TLS

| Host | Evidence |
|------|----------|
| 10.0.255.254:443 | Subject `CN=portal.test.emrad.ng`, `O=EMRAD`, `C=NG`. SAN: DNS `portal.test.emrad.ng`, IP `10.0.255.254`. Not before `2026-09-14T18:27:02`. Not after `2027-09-14T18:27:02`. ALPN: `http/1.1`, `http/1.0`, `http/0.9`. Nmap reported that the TLS random value did not represent time. The certificate issuer was not printed in the Nmap output. Test notes describe an EMRAD Local Root CA; that issuer is not confirmed by the Nmap excerpt. |
| 10.0.38.0:443 | Nikto: subject CN `portal.test.emrad.ng`, SAN `portal.test.emrad.ng`, issuer Let’s Encrypt `YE2`, cipher `TLS_AES_256_GCM_SHA384`. |

### 6.5 Security headers observed on the HTTPS portal

Recorded on primary HTTPS responses during the 21 September dynamic test:

| Header | Observed value |
|--------|----------------|
| Strict-Transport-Security | `max-age=31536000; includeSubDomains; preload` |
| X-Frame-Options | `SAMEORIGIN` |
| X-Content-Type-Options | `nosniff` |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| X-XSS-Protection | `0` |
| Cross-Origin-Opener-Policy | `same-origin` |
| Cross-Origin-Resource-Policy | `same-site` |
| X-Permitted-Cross-Domain-Policies | `none` |
| Content-Security-Policy | Present. `script-src` includes `'unsafe-inline'`. Sub-portal responses also include `'unsafe-eval'`. `img-src` allows `https:`. |

ZAP also reported no CSP on `GET https://portal.test.emrad.ng/storage/site/01KP5XVF8MD1SH0738C4V3P913.png` and no HSTS on `GET https://portal.test.emrad.ng/robots.txt`. Those are resource-specific scanner results. They do not cancel the headers observed on the HTML pages.

### 6.6 HTTP methods

| Source | Result |
|--------|--------|
| Nikto, `https://10.0.38.0:443` | `OPTIONS` allowed `GET` and `HEAD`. `TRACE` was reported active. |
| Nmap `http-trace`, `10.0.38.0:443` | `TRACE is enabled`. |
| Nmap `http-trace` | Not reported against `10.0.255.254`. |

---

## 7. Security Findings Summary

| ID | Finding | Severity | Affected Asset | Evidence Source | Status |
|----|---------|----------|----------------|-----------------|--------|
| PT-001 | Cleartext cadet login on the IP virtual host | High | `http://10.0.255.254/` | ZAP response; Nmap page title | Partially verified |
| PT-002 | CSRF control on `POST /livewire/update` accepts a missing Referer and does not enforce the CSRF token | Medium | `https://portal.test.emrad.ng` | Strix dynamic tests; ZAP anti-CSRF alert (partial) | Dynamically verified control bypass; login not completed |
| PT-003 | Database and remote-administration services exposed on the Windows web host | Medium | `10.0.38.0` | Nmap | Automatically detected; not exploited |
| PT-004 | `Secure` cookie attribute missing on Filament sub-portal logins | Low | `https://portal.test.emrad.ng` | Strix; ZAP | Dynamically verified |
| PT-005 | HTTP `TRACE` enabled | Low | `10.0.38.0:443` | Nmap; Nikto | Automatically detected; XST not demonstrated |
| PT-006 | Content Security Policy allows inline and eval script | Low | `https://portal.test.emrad.ng` and `http://10.0.38.0` | ZAP; dynamic header notes | Automatically detected; XSS not demonstrated |
| PT-007 | Portal HTML served over plaintext HTTP | Low | `http://10.0.38.0` | ZAP | Automatically detected |

---

## 8. Detailed Findings

### PT-001 — Cleartext authentication on the cadet survey virtual host

**Severity:** High  
**Affected Asset:** 10.0.255.254  
**Affected Endpoint:** `http://10.0.255.254/` and `POST http://10.0.255.254/login`  
**Evidence Source:** `10.0.255.254-ZAP-Report-.html`; Nmap `http-title` in `Script_10.0.255.254.nmap`  
**CWE:** CWE-319 (Cleartext Transmission of Sensitive Information); CWE-614 (Sensitive Cookie Without `Secure` Attribute)  
**CVSS:** A single base score is not assigned. The issue is a plaintext password form on an internal address. The numeric score changes with whether an attacker can observe that path (adjacent network versus a routed path, passive sniffing versus an active man-in-the-middle). Credential capture was not performed, so an exploited-impact score would be speculative.

### Description

Requesting the host by IP address on port 80 does not return the HTTPS portal. It returns a separate Laravel application, “Cadet Login — NDA G-Branch Survey”. The login form posts the password to an `http://` URL on the same host. The response that set the session cookie did not mark that cookie `Secure` and did not send HSTS.

This is distinct from `https://portal.test.emrad.ng`, which presented TLS and HSTS during the 21 September test.

### Technical Evidence

Nmap service detection against `10.0.255.254:80` recorded the page title `Cadet Login — NDA G-Branch Survey`.

ZAP stored this response for `GET http://10.0.255.254/` on 21 September 2026:

```
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html; charset=utf-8
Cache-Control: no-cache, private
Set-Cookie: XSRF-TOKEN=[REDACTED]; Max-Age=7200; path=/; samesite=lax
Set-Cookie: surveyapplication-session=[REDACTED]; Max-Age=7200; path=/; httponly; samesite=lax
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
```

The HTML form in that body was:

```
<form action="http://10.0.255.254/login" method="POST" autocomplete="off">
```

The form includes a hidden `_token` field, an email field, a password field, and a remember-me control. Cookie values and the token value are omitted here.

The captured response headers do not include `Strict-Transport-Security` or the `Secure` cookie flag.

### Security Impact

**Demonstrated:** The login page is served over HTTP, and the form target is HTTP. A party who can read that traffic can read submitted passwords and the session cookie. That capture was not carried out in the preserved test.

**Not demonstrated:** Valid credentials were not submitted. No session was hijacked. No account access was obtained.

### Attack Scenario

A user on a network path that can observe traffic to `10.0.255.254:80` opens the cadet login page and submits the form. The password and the subsequent `surveyapplication-session` cookie travel without TLS. The attacker replays the cookie to the same application.

This scenario is supported by the form and cookie evidence. It was not executed.

### Validation

Partially verified. The page, form action, and cookie flags were captured by ZAP and match the Nmap title. Interception of a real login was not performed.

### Recommendation

1. Serve this application only over HTTPS, with a certificate that matches the name users actually request.
2. Redirect port 80 to HTTPS and send HSTS on the HTTPS responses.
3. Set `Secure` on `surveyapplication-session` and `XSRF-TOKEN`. Keep `HttpOnly` on the session cookie.
4. Confirm that the IP-based virtual host cannot be used to bypass the HTTPS portal.
5. After the change, a direct request to `http://10.0.255.254/login` should not return a password form or set a session cookie.

### References

- CWE-319: https://cwe.mitre.org/data/definitions/319.html
- CWE-614: https://cwe.mitre.org/data/definitions/614.html
- OWASP ASVS session and transport requirements for cookies and TLS (transport layer protection)

---

### PT-002 — Livewire update endpoint does not enforce the CSRF token

**Severity:** Medium  
**Affected Asset:** `https://portal.test.emrad.ng`  
**Affected Endpoint:** `POST /livewire/update` on `/staff-login/login`, `/smart-academy/login`, and `/academic-branch/login`  
**Evidence Source:** `portal-test-emrad-ng_f4af/vulnerabilities/vuln-0002.md`; `findings.sarif`; ZAP alert “Absence of Anti-CSRF Tokens”  
**CWE:** CWE-352 (Cross-Site Request Forgery)  
**CVSS:** 5.4 (as recorded by the dynamic test). A vector consistent with that score and with the evidence is `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N`. User interaction is required. Impact is limited to the login-CSRF case that was actually exercised.

### Description

The Filament login panels submit authentication through Livewire’s `POST /livewire/update` endpoint. Dynamic tests showed that the server’s cross-origin decision follows the `Referer` header, and that a request with no `Referer` is processed. The `X-CSRF-TOKEN` header did not change the result: a missing token, an empty token, and a forged token were handled the same way as a token taken from the page.

A cross-origin `Referer` received HTTP 403 with the message `Access denied.` A same-origin `Referer`, and a request with no `Referer`, received HTTP 200. Calling `authenticate` with an email and a password that were not valid produced HTTP 200 and the error `These credentials do not match our records.` That shows the login method ran. It does not show a completed login.

ZAP separately reported that the login form HTML did not contain a conventional hidden CSRF field name. The dynamic test is the stronger evidence: a CSRF meta token exists, and the update endpoint did not validate it.

### Technical Evidence

From the 21 September dynamic test write-up:

| Request condition | Result |
|-------------------|--------|
| No `X-CSRF-TOKEN`, forged token, empty token, or valid token | HTTP 200 in each case |
| `Referer: https://evil.attacker.com` | HTTP 403, body message `Access denied.` |
| `Referer` set to the portal login origin | HTTP 200 |
| No `Referer` | HTTP 200 |
| No `Referer`, `updates` setting `data.email` and `data.password`, call `authenticate` | HTTP 200 and `These credentials do not match our records.` |

The same Referer behaviour was recorded on all three panels. Some repeated requests received HTTP 429, so a rate limit exists on this endpoint. The write-up states that a tampered Livewire snapshot was rejected with HTTP 419, and that unauthenticated `POST /livewire/upload-file` returned HTTP 401.

`SameSite=Lax` was present on `academy-website-session`. The test notes state that this stops a cross-site POST from carrying an existing session cookie. The login form does not need an existing session, so that control does not block this login case.

### Security Impact

**Demonstrated:** An unauthenticated client can invoke `authenticate` on the three panels without a validated CSRF token, by omitting `Referer`. A cross-origin `Referer` is blocked.

**Theoretical, not demonstrated:** If an attacker has a valid account and can induce a user to load an attacker page that suppresses `Referer`, the user’s browser can be logged into the attacker’s account (login CSRF). Actions the user then takes would occur in the attacker’s session. A completed login was not achieved. The preserved test used a password that the application rejected.

**Constrained:** Authenticated Livewire actions were not shown to be reachable cross-site, because of `SameSite=Lax`. Rate limiting reduces repeated attempts. It does not remove the single-request case.

### Attack Scenario

An attacker who already has a portal account hosts a page that sends `POST /livewire/update` with `Referrer-Policy: no-referrer`, a current login-component snapshot, the attacker’s email and password, and an `authenticate` call. A user who opens that page is logged into the attacker’s account if the password is accepted. The snapshot must be recent; the test notes state that a modified snapshot is rejected.

### Validation

Dynamically verified for the missing-Referer bypass and for invocation of `authenticate` with rejected credentials. Not verified as a completed account login. ZAP’s missing-token alert is supporting scanner evidence only. Nmap did not find a conventional CSRF issue on `10.0.255.254` (`http-csrf: Couldn't find any CSRF vulnerabilities`).

### Recommendation

1. Enforce Laravel’s CSRF middleware on `POST /livewire/update`. Reject requests whose token is missing, empty, or not bound to the session.
2. Treat a missing `Referer` as untrusted if a Referer check is kept as a secondary control. Return 403 in that case, as is already done for a foreign `Referer`.
3. Re-test all three panels. A request with no `Referer` and no valid CSRF token must not execute `authenticate`.
4. Keep `SameSite=Lax` or stricter on the session cookie.

### References

- CWE-352: https://cwe.mitre.org/data/definitions/352.html
- OWASP Cross-Site Request Forgery Prevention Cheat Sheet
- OWASP WSTG-SESS-05 (testing for CSRF)

---

### PT-003 — Database and remote-administration services exposed on the Windows host

**Severity:** Medium  
**Affected Asset:** 10.0.38.0  
**Affected Endpoint:** TCP 135, 139, 445, 3306, and 3389  
**Evidence Source:** `10.0.38.0/nmap/Port_10.0.38.0.nmap`, `Vulns_10.0.38.0.nmap`, `CVEs_10.0.38.0.nmap`  
**CWE:** CWE-284 (Improper Access Control)  
**CVSS:** Not scored. No authentication weakness was shown. A score would require the intended exposure of these ports and whether the assessment path matches normal user reachability.

### Description

The Windows host that serves the portal stack also accepts connections to RPC, NetBIOS, SMB, MariaDB, and Remote Desktop. Those services were reachable from the same position used to scan the website. MariaDB returned a version greeting before authentication. SMB vulnerability scripts failed during negotiation and did not produce a positive vulnerability result.

### Technical Evidence

```
80/tcp   open  http          Apache httpd 2.4.58 (OpenSSL/3.1.3 PHP/8.2.12)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
443/tcp  open  ssl/http      Apache httpd 2.4.58 ((Win64) OpenSSL/3.1.3 PHP/8.2.12)
445/tcp  open  microsoft-ds?
3306/tcp open  mysql         MariaDB 10.3.23 or earlier (unauthorized)
3389/tcp open  ms-wbt-server
```

Host script results:

```
smb-vuln-ms10-054: false
smb-vuln-ms10-061: Could not negotiate a connection
samba-vuln-cve-2012-1182: Could not negotiate a connection
```

Nmap’s `vulners` script, limited to CVSS 7.0 and above, did not attach CVE findings to these Windows services.

### Security Impact

**Demonstrated:** The ports are open and the database banner is readable without a login.

**Not demonstrated:** Database queries, SMB shares, RDP login, credential attacks, and the named SMB vulnerabilities. “Unauthorized” in the MariaDB line is Nmap’s description of an unauthenticated handshake, not proof that data can be read.

Exposure still matters because a weakness in the website sits on a host that also offers remote administration and direct database access.

### Attack Scenario

Not demonstrated. A credible follow-on would be an authenticated or unauthenticated attempt against MariaDB and RDP from the same network segment, only if the rules of engagement allow credential testing.

### Validation

Automatically detected. Service exposure is confirmed by multiple Nmap phases. Exploitation was not attempted in the preserved output. SMB vulnerability results are inconclusive because the scripts did not negotiate a session.

### Recommendation

1. Restrict 3306, 3389, 445, 139, and 135 to management networks. Do not leave them on the same reachable path as the public web ports if that is not required.
2. Confirm MariaDB requires authentication and is not bound beyond the application host.
3. If RDP is required, constrain it and keep it patched. This assessment did not identify the RDP build.
4. Re-scan from the web-user segment after filtering. The expected result is closed or filtered on these five ports.

### References

- CWE-284: https://cwe.mitre.org/data/definitions/284.html
- CIS benchmarks for Windows member servers, database listener exposure, and remote desktop

---

### PT-004 — Session cookies on sub-portal logins are missing the Secure attribute

**Severity:** Low  
**Affected Asset:** `https://portal.test.emrad.ng`  
**Affected Endpoint:** `/staff-login/login`, `/smart-academy/login`, `/academic-branch/login`  
**Evidence Source:** `portal-test-emrad-ng_f4af/vulnerabilities/vuln-0001.md`; ZAP alert “Cookie Without Secure Flag” on `GET https://portal.test.emrad.ng/smart-academy/`  
**CWE:** CWE-614  
**CVSS:** 3.1 (as recorded by the dynamic test). HSTS on the primary site is a mitigating control, and cookie leakage over HTTP was not shown. A matching conservative vector is `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N`.

### Description

The public site root sets `Secure` on both `XSRF-TOKEN` and `academy-website-session`. The three Filament login responses set the same cookie names without `Secure`. `academy-website-session` remains `HttpOnly` and `SameSite=Lax`. HSTS is present on the primary HTTPS responses with `max-age=31536000; includeSubDomains; preload`.

### Technical Evidence

Dynamic test notes, with cookie values removed:

```
# GET /
Set-Cookie: XSRF-TOKEN=[REDACTED]; Max-Age=7200; path=/; secure; samesite=lax
Set-Cookie: academy-website-session=[REDACTED]; Max-Age=7200; path=/; secure; httponly; samesite=lax

# GET /staff-login/login, /smart-academy/login, and /academic-branch/login
Set-Cookie: XSRF-TOKEN=[REDACTED]; Max-Age=7200; path=/; samesite=lax
Set-Cookie: academy-website-session=[REDACTED]; Max-Age=7200; path=/; httponly; samesite=lax
```

ZAP recorded `Set-Cookie: academy-website-session` without `Secure` on `https://portal.test.emrad.ng/smart-academy/`.

### Security Impact

**Demonstrated:** The attribute is inconsistent across routes on the same site.

**Not demonstrated:** Transmission of these cookies over HTTP, or session hijack. HSTS, if honoured by the browser, prevents later HTTP requests to the host. The practical risk is a first request, or a client that ignores HSTS.

The survey application in PT-001 is a separate cookie (`surveyapplication-session`) on a page that is already plaintext. This finding is only the Filament panel inconsistency.

### Attack Scenario

A user reaches a sub-portal login in a way that produces an HTTP request before HSTS applies. The session cookie is then readable on the network. This was not tested.

### Validation

Dynamically verified by comparing response headers. Corroborated by ZAP. Nikto’s “cookie without HttpOnly” results are a different attribute and are informational (see INFO-002).

### Recommendation

Set `SESSION_SECURE_COOKIE=true`, or `'secure' => true` in the session configuration used by each Filament panel. Re-request all three login URLs and the site root. Every `Set-Cookie` for these two names should include `Secure`.

### References

- CWE-614: https://cwe.mitre.org/data/definitions/614.html
- OWASP Session Management Cheat Sheet (cookie `Secure` flag)
- MDN: Set-Cookie `Secure` attribute

---

### PT-005 — HTTP TRACE is enabled on the Windows web service

**Severity:** Low  
**Affected Asset:** 10.0.38.0  
**Affected Endpoint:** `https://10.0.38.0:443`  
**Evidence Source:** `Vulns_10.0.38.0.nmap` (`http-trace: TRACE is enabled`); Nikto report `htm.htm`  
**CWE:** CWE-693 (Protection Mechanism Failure)  
**CVSS:** Not scored. Cross-site tracing was not demonstrated, and current browsers do not allow scripted `TRACE` in the way historically used for XST.

### Description

The Apache service on port 443 answered `TRACE`. Nikto reported the same behaviour and associated it with cross-site tracing. `TRACE` reflects the request, which can include cookies if a client can be made to issue it. That client behaviour was not shown.

### Technical Evidence

Nmap NSE against `10.0.38.0:443`:

```
|_http-trace: TRACE is enabled
```

Nikto against `https://10.0.38.0:443/`:

```
/: HTTP TRACE method is active and replies which suggests the host is vulnerable to XST.
OPTIONS: Allowed HTTP Methods: GET, HEAD.
```

`OPTIONS` itself listed only `GET` and `HEAD`. The `TRACE` finding still came from both tools.

### Security Impact

**Demonstrated:** The method is enabled and, according to both scanners, elicits a reply.

**Not demonstrated:** Cookie disclosure through a browser, or any account compromise. Severity stays low for that reason.

### Attack Scenario

Not demonstrated beyond the scanner probe. A historical XST scenario would require a browser that can issue cross-origin `TRACE` and a page that can read the reflected headers. That condition was not tested.

### Recommendation

Disable `TRACE` in Apache (`TraceEnable Off`). Confirm with a `TRACE` request that the server returns `405` or an equivalent rejection, on both port 80 and port 443.

### References

- CWE-693: https://cwe.mitre.org/data/definitions/693.html
- OWASP: HTTP Methods test guidance (disable unused methods, including `TRACE`)
- Apache `TraceEnable` documentation

---

### PT-006 — Content Security Policy permits unsafe script execution

**Severity:** Low  
**Affected Asset:** `https://portal.test.emrad.ng` and `http://10.0.38.0`  
**Affected Endpoint:** HTML documents, including `/` and `/smart-academy/login`  
**Evidence Source:** Both 21 September ZAP reports; `NDA-.html` (7 September); dynamic test header notes  
**CWE:** CWE-693  
**CVSS:** Not scored. No cross-site scripting was confirmed, so confidentiality and integrity impact were not demonstrated. ZAP’s default Medium rating is not used.

### Description

Pages send a Content-Security-Policy, and several directives are restrictive (`default-src 'self'`, `object-src 'none'`, `frame-ancestors 'self'`, `base-uri 'self'`). The policy still allows inline script. The smart-academy login response also allows `unsafe-eval`. `img-src` allows any `https:` origin. `style-src` allows `'unsafe-inline'`.

A static image under `/storage/site/` was reported by ZAP without a CSP header. That is a gap on that response type, not a second vulnerability.

### Technical Evidence

ZAP evidence string (truncated in the report at the frame-src list) included:

```
default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self';
form-action 'self'; img-src 'self' data: blob: https:;
script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com
```

ZAP’s `unsafe-eval` instance was `GET https://portal.test.emrad.ng/smart-academy/login`, with the note `script-src includes unsafe-eval`.

The same `unsafe-inline` script policy and broad `img-src` were present on `GET http://10.0.38.0`.

Injection coverage for `/search` and the contact form is marked incomplete. No reflected payload result is stored.

### Security Impact

**Demonstrated:** The policy will not block inline script, and on the sub-portal it will not block `eval`.

**Not demonstrated:** An XSS vulnerability that would benefit from those exceptions. If one exists, this policy would not stop it. That is why the issue is recorded, and why it is not raised above Low.

### Attack Scenario

Not demonstrated. The scenario would be a separate injection bug in a page covered by this policy. The assessment did not confirm one.

### Validation

Automatically detected from response headers, and consistent between ZAP on 7 September and 21 September and the dynamic notes. Not validated as an exploitable XSS issue.

### Recommendation

1. Remove `'unsafe-inline'` and `'unsafe-eval'` from `script-src` where the application can use nonces or hashes.
2. Replace `img-src https:` with the image origins the site actually uses.
3. Apply the same policy to HTML error and login responses. Static images do not need a script policy, but HTML must not be served without one.
4. Re-test only after injection testing of `/search` and forms is finished, so the policy is not treated as a substitute for fixing an injection bug.

### References

- CWE-693: https://cwe.mitre.org/data/definitions/693.html
- OWASP Content Security Policy Cheat Sheet
- MDN: CSP `script-src`

---

### PT-007 — Portal content is available over unencrypted HTTP on the Windows host

**Severity:** Low  
**Affected Asset:** 10.0.38.0  
**Affected Endpoint:** `http://10.0.38.0/`  
**Evidence Source:** `NDA-.html` (ZAP, 7 September 2026)  
**CWE:** CWE-319  
**CVSS:** Not scored. The captured form is a site search form, not a password form. Password submission over HTTP was not shown on this host. PT-001 covers the password form on the other host.

### Description

ZAP received application HTML from `http://10.0.38.0` with HTTP 200, rather than a redirect to HTTPS. The page included the portal content-security policy and a search form that posts to `https://portal.test.emrad.ng/search`. Serving the document over HTTP allows a network observer to modify it before the browser follows the HTTPS action.

Nikto confirmed that HTTPS on port 443 of the same host is also active, with a Let’s Encrypt certificate for `portal.test.emrad.ng`.

### Technical Evidence

ZAP alert “HTTP to HTTPS Insecure Transition in Form Post”:

```
GET http://10.0.38.0
Evidence: https://portal.test.emrad.ng/search
Context: <form method="GET" action="https://portal.test.emrad.ng/search" ... name="q" ...>
```

The same HTTP response carried the Apache version banner and `X-Powered-By: PHP/8.2.12` (INFO-001) and set `XSRF-TOKEN` (INFO-002).

### Security Impact

**Demonstrated:** The site body is available without TLS on this host, and it contains a form whose action is HTTPS.

**Not demonstrated:** Modification of that page in transit, or theft of portal credentials through this form. The form method is GET and the field is a search query.

### Attack Scenario

Not demonstrated. An on-path attacker who can alter `http://10.0.38.0/` can change the HTML, including the form target, before the browser uses it.

### Validation

Automatically detected. The HTML body and form action are in the ZAP report. No man-in-the-middle test was performed.

### Recommendation

1. Redirect every HTTP request on `10.0.38.0` to HTTPS before returning application HTML.
2. Send HSTS on the HTTPS vhost.
3. Do not set session cookies on HTTP responses.
4. Re-test `GET http://10.0.38.0/`. The expected result is a redirect and an empty or absent body, with no `Set-Cookie`.

### References

- CWE-319: https://cwe.mitre.org/data/definitions/319.html
- OWASP Transport Layer Protection Cheat Sheet

---

## 9. Informational Findings

These items are visible in the evidence. They are not scored as vulnerabilities.

### INFO-001 — Product and version disclosure

| Asset | Evidence |
|-------|----------|
| 10.0.38.0 | `Server: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12` on `/sitemap.xml` and the site root (ZAP and Nmap). `X-Powered-By: PHP/8.2.12` (ZAP and Nikto). |
| 10.0.255.254 | `Server: nginx` without a version. OpenSSH banner `OpenSSH 10.0p2 Ubuntu 5ubuntu5.4`. |
| Portal | Filament 3.3.54.0 in asset URLs. Livewire script publicly reachable at `/livewire/livewire.min.js` according to the test notes. |

**Recommendation:** Remove `X-Powered-By` and the version tokens from the Apache `Server` header on `10.0.38.0`. Version hiding is not a control by itself.

### INFO-002 — `XSRF-TOKEN` is not HttpOnly

ZAP, Nikto, and the dynamic header samples all show `XSRF-TOKEN` without `HttpOnly`, including on the portal root where `Secure` is set. `academy-website-session` and `surveyapplication-session` are `HttpOnly`.

Laravel’s JavaScript reads `XSRF-TOKEN` in order to send the CSRF header. The missing flag matches that design. It is not, by itself, the CSRF bypass in PT-002. Nikto reported the cookie on URLs such as `/ng.zip` and `/portal.test.emrad.ng.tar.bz2`; those paths were not shown to be downloadable archives. The cookie observation is what those responses support.

### INFO-003 — `robots.txt` names restricted areas

Nmap and the dynamic notes record:

```
Disallow: /smart-academy/
Disallow: /academic-branch/
Disallow: /staff-login/
Disallow: /search
Sitemap: https://www.nda.edu.ng/sitemap.xml
```

`Disallow` is not an access control. The panels still redirected unauthenticated users to login in the tests that were recorded. The sitemap URL links the test host to `www.nda.edu.ng`. That production name was not scanned.

### INFO-004 — Third-party stylesheets are loaded without Subresource Integrity

ZAP reported a stylesheet request to `https://fonts.googleapis.com` without an `integrity` attribute, on both the portal and `http://10.0.38.0`. This is a defence-in-depth gap. Compromise of that third party was not tested.

### INFO-005 — HSTS is not uniform across every URL

Primary HTTPS HTML responses included `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`. ZAP reported the header missing on `https://portal.test.emrad.ng/robots.txt`. Nikto reported it missing on port 80 responses, which is expected when the response is HTTP: browsers ignore HSTS on plaintext responses. The cadet login response in PT-001 also lacked HSTS.

**Status:** The portal HTML control is present. The `robots.txt` exception should be checked. It is not raised as a separate vulnerability.

### INFO-006 — HTML comment refers to a removed admin link

ZAP matched the comment `<!-- Admin Login removed from mobile menu -->` on `https://portal.test.emrad.ng/`. The comment confirms that an admin link was removed from one menu. It does not show that an admin function is exposed. The known panel URLs are already in `robots.txt`.

### INFO-007 — Public build and health endpoints

Test notes record `GET /up` returning an application-up message, and `GET /build/manifest.json` returning the Vite manifest (`app-CHjsmJMB.js`, `app-DPVzrR3Z.css`, an Alpine bundle). The JavaScript bundle was reviewed in that test and no embedded secrets were recorded. Source maps for that bundle were recorded as not found.

**Recommendation:** If `/up` is not required for an external monitor, limit it. The manifest is normal for a Vite build; it is useful to an attacker only as a file index.

---

## 10. False Positives / Unverified Findings

| Finding | Tool | Reason Not Confirmed | Recommended Action |
|---------|------|----------------------|--------------------|
| OpenSSH CVEs CVE-2026-60002 (9.4), CVE-2026-35414 (8.1), CVE-2026-35386 (8.1), CVE-2026-35385 (8.1), CVE-2026-60000 (7.5), CVE-2026-59999 (7.5) | Nmap `vulners` against CPE `cpe:/a:openbsd:openssh:10.0p2` | Version match only. The banner is the Ubuntu package `5ubuntu5.4`. No exploit was run and no patch-level comparison was saved. | Compare the package changelog with those CVE advisories. Do not treat the list as confirmed until that check is done. |
| Slowloris denial of service, state “LIKELY VULNERABLE”, CVE-2007-6750 | Nmap `http-slowloris-check` on `10.0.38.0` ports 80 and 443 | Heuristic only. A denial-of-service test was not performed. CVE-2007-6750 is a disputed issue and does not by itself prove this Apache build is exploitable. | If availability testing is in scope, run a controlled test against a non-production window. Otherwise close this as unverified. |
| Possible CSRF on `global-search` | Nmap `http-csrf` on `10.0.38.0:443` | The form is a site search (`GET` or search action to `/search`). No state change was shown. This is not PT-002. | No change unless the search form is later shown to change server state. |
| Absence of a hidden CSRF field on the Filament login form | ZAP | The dynamic test found a CSRF meta token and showed that the real gap is server-side validation on `/livewire/update` (PT-002). The ZAP description is an incomplete view of the same form. | Track under PT-002 only. |
| Big redirect / sensitive information leak | ZAP, including `GET https://portal.test.emrad.ng/smart-academy/` | The `Location` value shown is `https://portal.test.emrad.ng/smart-academy/login` (48 characters). That is an authentication redirect, not a secret in the URL. | No remediation. |
| Unix timestamp disclosure `1732584194` (2024-11-26) | ZAP, Filament `support.js?v=3.3.54.0` | The value sits in a published JavaScript asset and matches a build or library timestamp. No sensitive record was tied to it. | No remediation. |
| User-controllable HTML attribute on `/search?q&scope=branch` | ZAP, informational, low confidence | ZAP observed the `scope` value reflected into a button `id`. No payload was confirmed. Injection testing of `/search` was not completed. | Finish the planned XSS test. Do not record this as XSS now. |
| User-Agent fuzzer | ZAP on `http://10.0.255.254/` and `http://10.0.38.0/` | The preserved IP result is the normal cadet login page for one browser identity. A meaningful behaviour difference was not documented. | No remediation from this alert. The page itself is PT-001. |
| Suspicious comments (3,057 ZAP instances on the later portal scan) | ZAP | Volume is consistent with script and markup noise. The one reviewed instance is INFO-006. | Do not treat the count as 3,057 vulnerabilities. |
| Retrieved from cache / re-examine cache-control | ZAP | Cache hits in the report include the out-of-scope Firefox settings host. `robots.txt` cache guidance is not a vulnerability. | Ignore for this application, except to keep authenticated pages `no-store`. The cadet login already sent `Cache-Control: no-cache, private`. |
| Cross-domain misconfiguration (`Access-Control-Allow-Origin: *`) | ZAP | The instance site is `firefox.settings.services.mozilla.com`, not an in-scope host. | Exclude. |
| Nikto banner change to `Mikrotik HttpProxy` on `http://127.0.0.1:2301/` | Nikto, `nda-new.htm` | This is Nikto’s proxy probe. A banner change does not prove an open proxy. No successful proxied request is stored. Port 53’s `Mikrotik dnsd` label was also not repeated by the follow-up Nmap scan. | If a proxy is suspected, test explicitly with an out-of-band URL. Until then, inconclusive. |
| Multiple default index names, `/css/`, `/js` | Nikto, `10.0.255.htm` | Directory presence only. No sensitive file content was recorded. | No action from these lines alone. |
| Drupal CVE-2014-3704 script error | Nmap on `10.0.255.254` | `http-vuln-cve2014-3704` exited with a script error. The application is Laravel, not Drupal. | Ignore. |
| SMB MS10-061 and CVE-2012-1182 | Nmap on `10.0.38.0` | Scripts failed while negotiating. `smb-vuln-ms10-054` returned false. | Re-test SMB only if a negotiation can be completed. Do not report those CVEs as present. |
| Nuclei findings | `NDAnuclei.json` | File content is `[]`. | Re-run if a template scan was intended, and keep the raw output. |
| Cross-domain JavaScript inclusion | ZAP on `http://10.0.38.0` | The script URL is `https://portal.test.emrad.ng/build/assets/app-Dg7WsBVl.js`, the same application over HTTPS. | Covered operationally by PT-007 (do not serve the page over HTTP). Not a separate trust-boundary bug. |

---

## 11. Security Controls Observed

The following controls are visible in the evidence. They were not all tested to exhaustion.

| Control | Where observed | Limit of the observation |
|---------|----------------|--------------------------|
| HTTPS on the named portal | `https://portal.test.emrad.ng` and `https://10.0.38.0` | `http://10.0.255.254/` and `http://10.0.38.0/` still serve application HTML (PT-001, PT-007). |
| HSTS with `includeSubDomains` and `preload` | Primary HTTPS responses for the portal | Not seen on the cadet login response or, per ZAP, on `/robots.txt`. |
| `X-Frame-Options: SAMEORIGIN` and `X-Content-Type-Options: nosniff` | Portal and cadet login | Present in captured responses. Clickjacking was not separately tested. |
| `SameSite=Lax` on session cookies | `academy-website-session`, `surveyapplication-session` | Limits cross-site use of an existing session. Does not fix PT-002’s login case. |
| `HttpOnly` on session cookies | Both applications | Not set on `XSRF-TOKEN` (INFO-002). |
| `Secure` on portal root cookies | `GET /` | Absent on the three sub-portal logins (PT-004) and on the cadet app (PT-001). |
| Frame, object, and base URI restrictions in CSP | Portal CSP | Undermined for script by `unsafe-inline` and, on a sub-portal, `unsafe-eval` (PT-006). |
| Login error text does not distinguish unknown users | Dynamic notes for staff login: the same “credentials do not match our records” message | A full enumeration matrix and lockout test were not completed. |
| Unauthenticated panel routes redirect to login | `/smart-academy/users`, `/academic-branch/users`, and similar paths in the notes | IDOR inside an authenticated session was not tested. |
| Sensitive paths not served | `/.env`, `/.git/HEAD`, `/.git/config` recorded as 403. Telescope, Horizon, Debugbar, `phpinfo.php`, and `server-status` recorded as 404. | Wordlists were not exhaustive. `ffuf` output is not in the project. |
| Livewire snapshot checksum | Tampered snapshot received HTTP 419 | Applies to the snapshot blob. It did not stop the `updates` plus `authenticate` case in PT-002. |
| Unauthenticated Livewire upload rejected | `POST /livewire/upload-file` recorded as HTTP 401 | Authenticated upload rules were not tested. |
| Arbitrary Livewire method names | Non-existent methods produced a generic HTTP 500, without stack traces, in the test notes | Only the login component was in scope for that check. |
| Rate-limit headers | Portal `/search` (`X-RateLimit-Limit: 40` in the test notes). Nikto on `10.0.38.0` saw limit 360 and remaining 357. Livewire received HTTP 429 after repeated calls. | Login lockout policy was not fully measured. |
| Small TCP footprint on 10.0.255.254 | Four open ports in a full TCP scan; remaining ports filtered | Port 22 and port 53 are still open. UDP was inconclusive. |
| Let’s Encrypt certificate on 10.0.38.0:443 | Nikto issuer `YE2`, TLS 1.3 cipher `TLS_AES_256_GCM_SHA384` | Chain and protocol downgrade were not fully tested. `sslscan` output is absent. |

---

## 12. Risk Summary

Counts are the deduplicated findings in Sections 8 and 9. Unverified scanner rows in Section 10 are not included.

| Severity | Number of Findings |
|----------|--------------------|
| Critical | 0 |
| High | 1 |
| Medium | 2 |
| Low | 4 |
| Informational | 7 |

---

## 13. Remediation Plan

### Immediate Remediation

These items expose credentials or authentication controls on evidence already collected.

1. **PT-001.** Remove plaintext login from `http://10.0.255.254/`. Require HTTPS, set `Secure` on the survey cookies, and send HSTS.
2. **PT-002.** Validate the CSRF token on `POST /livewire/update` for all three panels, and reject requests that omit `Referer` if that header remains part of the check.
3. **PT-003.** Limit MariaDB (3306) and RDP (3389) on `10.0.38.0` to the administration path. Review SMB and RPC (445, 139, 135) in the same change. No exploit is required to justify closing a database port that is reachable beside the website.

### Short-Term Remediation

4. **PT-004.** Set the `Secure` flag on sub-portal cookies so it matches the site root.
5. **PT-007.** Redirect `http://10.0.38.0` to HTTPS and stop returning the portal document on port 80.
6. **PT-005.** Disable `TRACE` on Apache.
7. Finish the tests that the 21 September run left open: injection on `/search` and `/contact`, login rate limiting, and authenticated access control on the Filament resources. Do not treat those areas as clear.

### Hardening / Long-Term Improvements

8. **PT-006.** Tighten CSP once inline script can be moved to nonces or hashes.
9. **INFO-001.** Remove PHP and Apache version tokens from `10.0.38.0`.
10. Confirm the OpenSSH Ubuntu package against the CVE list in Section 10 before any emergency patch cycle based solely on the Nmap `vulners` output.
11. Align the two hosts. They presented the same hostname on 7 September and 21 September with different operating systems, web servers, and certificates. Decommission or isolate whichever host is not the intended origin.
12. Keep authenticated file-upload and IDOR testing on the schedule before this portal is treated as production.

No calendar dates are stated here. None were specified in the project materials.

---

## 14. Retest Recommendations

| ID | Retest |
|----|--------|
| PT-001 | `GET http://10.0.255.254/` and `POST http://10.0.255.254/login` must not return a password form. The HTTPS replacement must set `Secure` and HSTS. Repeat with the hostname users will actually use. |
| PT-002 | For each of the three panels, send `POST /livewire/update` with no `Referer` and with a missing, empty, and incorrect CSRF token. All three must be rejected. A foreign `Referer` must remain rejected. A valid same-origin token must still allow a normal login. Confirm HTTP 419 still occurs for a tampered snapshot. |
| PT-003 | From the same segment used on 7 September, TCP connect to 135, 139, 445, 3306, and 3389. Expected state is filtered or closed, unless a documented management path remains. |
| PT-004 | Compare `Set-Cookie` on `/`, `/staff-login/login`, `/smart-academy/login`, and `/academic-branch/login`. `Secure` must be present on both cookie names on every response. |
| PT-005 | `TRACE / HTTP/1.1` to `10.0.38.0` ports 80 and 443 must not echo the request. |
| PT-006 | Fetch `/` and each login page and confirm `script-src` no longer contains `'unsafe-inline'` or `'unsafe-eval'`, if that is the chosen end state. |
| PT-007 | `GET http://10.0.38.0/` must redirect to HTTPS and must not include the search form or a session `Set-Cookie`. |
| Unverified OpenSSH CVEs | Record `apt` policy or the package changelog for `openssh-server` and map it to the six CVE IDs. Close or patch from that evidence. |
| Unverified Slowloris | Do not retest with a load tool unless availability testing is explicitly authorized. |
| Incomplete portal tests | Repeat `/search` and contact-form injection, login lockout, and authenticated IDOR with test accounts. Those items are gaps, not passes. |

---

## 15. Conclusion

The materials cover two internal hosts and one HTTPS portal, tested on 7 September 2026 and 21 September 2026 with Nmap, Nikto, OWASP ZAP, an empty Nuclei results file, and a dynamic portal test.

One high-severity condition is confirmed at the HTTP layer: the cadet survey on `http://10.0.255.254/` submits passwords without TLS. One medium-severity authentication issue is confirmed on the portal: Livewire’s update endpoint can be driven without a valid CSRF token when `Referer` is omitted, and `authenticate` was observed to run. A completed login with an attacker session was not observed. The Windows host additionally exposes MariaDB and Remote Desktop beside the website; those services were not compromised.

Four low-severity configuration issues remain: sub-portal cookies without `Secure`, `TRACE` on Apache, a CSP that allows inline script, and portal HTML on `http://10.0.38.0`.

The OpenSSH CVE list, the Slowloris result, and the search-form CSRF hint from Nmap are not confirmed. Injection testing, authenticated access control, and file-upload rules after login were not finished. Those areas should be retested with the fixes above, rather than inferred from the clean results on sensitive-file probes and Livewire checksum checks.

---

## 16. Appendix

### A. Evidence index

| File | What it supports |
|------|------------------|
| `10.0.255.254/nmap/Port_10.0.255.254.nmap` | Open ports 22, 80, 443 on 21 September 2026, 12:29 |
| `10.0.255.254/nmap/Full_10.0.255.254.nmap` | Full TCP scan; adds port 53; 65,531 filtered |
| `10.0.255.254/nmap/Script_10.0.255.254.nmap` | OpenSSH and nginx versions, page titles, robots, certificate |
| `10.0.255.254/nmap/Vulns_10.0.255.254.nmap` | Negative XSS/CSRF NSE results; `Mikrotik dnsd` on port 53 |
| `10.0.255.254/nmap/CVEs_10.0.255.254.nmap` | Unverified OpenSSH `vulners` CVEs |
| `10.0.255.254/nmap/UDP_10.0.255.254.nmap` | No confirmed UDP services |
| `10.0.255.254/nmap/Full_Extra_10.0.255.254.nmap` | Port 53 rescan without a repeated version |
| `10.0.255.254/nmapAutomator_10.0.255.254_all.txt` | Combined Nmap phases for this host |
| `10.0.38.0/nmap/Port_10.0.38.0.nmap` | Ports 80, 135, 139, 443, 445, 3306, 3389 on 7 September 2026 |
| `10.0.38.0/nmap/Vulns_10.0.38.0.nmap` | Banners, TRACE, Slowloris heuristic, search-form CSRF hint, SMB script errors |
| `10.0.38.0/nmap/CVEs_10.0.38.0.nmap` | Service versions; no `vulners` CVE rows |
| `NDA-.html` | ZAP 2.17.0 report, 7 September 2026, site `http://10.0.38.0` |
| `NDA-ZAP-Report-.html` | ZAP report, 21 September 2026, 13:09, site `https://portal.test.emrad.ng` |
| `10.0.255.254-ZAP-Report-.html` | ZAP report, 21 September 2026, 13:21, including `http://10.0.255.254/` |
| `htm.htm` | Nikto, `https://10.0.38.0:443` |
| `10.0.255.htm`, `nda-new.htm`, `ndaold.htm` | Nikto, port 80 on the nginx host |
| `NDAnuclei.json` | Empty Nuclei result array |
| `portal-test-emrad-ng_f4af/vulnerabilities/vuln-0001.md` | Cookie `Secure` flag comparison |
| `portal-test-emrad-ng_f4af/vulnerabilities/vuln-0002.md` | Livewire CSRF tests |
| `portal-test-emrad-ng_f4af/findings.sarif` | Strix SARIF export of those two results |
| `portal-test-emrad-ng_f4af/penetration_test_report.md` | Concurrent automated report; findings were re-evaluated for this document |
| `portal-test-emrad-ng_f4af/strix.log` | Strix run start, 21 September 2026 |
| `zap32x32.png` and the `normalize/` and `themes/` directories | ZAP report styling only. Not test evidence. |

No finding screenshots are stored in the project. The ZAP logo file is not a figure for this report.

### B. ZAP alert types, in-scope hosts only

Default ZAP ratings are listed so they can be compared with this report. Mozilla hosts are omitted.

**`https://portal.test.emrad.ng` (21 September 2026, both ZAP HTML reports)**

| ZAP alert | ZAP risk | Disposition in this report |
|-----------|----------|----------------------------|
| CSP: Wildcard Directive (`img-src`) | Medium | PT-006 |
| CSP: script-src unsafe-inline | Medium | PT-006 |
| CSP: script-src unsafe-eval | Medium | PT-006 |
| CSP: style-src unsafe-inline | Medium | PT-006 |
| CSP header not set (storage PNG) | Medium | Noted under PT-006; static object |
| Absence of Anti-CSRF Tokens | Medium | Merged into PT-002 as incomplete scanner evidence |
| Sub Resource Integrity Attribute Missing | Medium | INFO-004 |
| Cookie Without Secure Flag | Low | PT-004 |
| Cookie No HttpOnly Flag | Low | INFO-002 |
| Strict-Transport-Security Header Not Set (`/robots.txt`) | Low | INFO-005 |
| Big Redirect Detected | Low | Section 10 |
| Timestamp Disclosure - Unix | Low | Section 10 |
| X-Content-Type-Options Header Missing | Low | Instance was the Firefox settings host, not the portal |
| Suspicious Comments | Informational | INFO-006 |
| Modern Web Application | Informational | Not a finding |
| Re-examine Cache-control Directives | Informational | Section 10 |
| Session Management Response Identified | Informational | Supports cookie inventory |
| User Controllable HTML Element Attribute | Informational | Section 10 |

ZAP recorded zero High alerts for the portal.

**`http://10.0.255.254` (21 September 2026)**

| ZAP alert | ZAP risk | Disposition |
|-----------|----------|-------------|
| User Agent Fuzzer | Informational | The stored body is the cadet login page. Used as evidence for PT-001. The fuzzer alert itself is Section 10. |

**`http://10.0.38.0` (7 September 2026)**

| ZAP alert | ZAP risk | Disposition |
|-----------|----------|-------------|
| HTTP to HTTPS Insecure Transition in Form Post | Medium | PT-007 |
| CSP wildcard, unsafe-inline script, unsafe-inline style | Medium | PT-006 |
| Sub Resource Integrity Attribute Missing | Medium | INFO-004 |
| Server version in `Server` header | Low | INFO-001 |
| `X-Powered-By: PHP/8.2.12` | Low | INFO-001 |
| Cookie No HttpOnly Flag | Low | INFO-002 |
| Cross-Domain JavaScript Source File Inclusion | Low | Section 10 |
| Big Redirect, suspicious comments, modern web application, session cookie, user-agent fuzzer | Low or informational | Not separate findings |

### C. Negative results worth retaining

| Check | Result |
|-------|--------|
| Nmap DOM XSS, stored XSS, and CSRF on `10.0.255.254:80` and `:443` | No issue reported. Two unrelated NSE scripts errored (Drupal CVE-2014-3704, ASP.NET debug). |
| Nmap DOM XSS, stored XSS on `10.0.38.0:80` | No issue reported. |
| `/.env`, `.git`, debug front ends | 403 or 404 in the dynamic notes. |
| Livewire snapshot tamper | HTTP 419. |
| Unauthenticated `/livewire/upload-file` | HTTP 401. |
| Nuclei | No findings in the saved file. |
| Nmap `vulners` on `10.0.38.0` | No CVE rows at the configured CVSS 7.0 floor. |

### D. Out of scope scanner noise

ZAP site lists include `https://firefox.settings.services.mozilla.com`, `https://firefox-settings-attachments.cdn.mozilla.net`, and `https://content-signature-2.cdn.mozilla.net`. Alerts on those hosts, including a CORS wildcard, were not produced by the NDA applications.

### E. Redaction

Session cookies, the survey CSRF token, and the portal CSRF token appear in raw tool output. They are replaced with `[REDACTED]` in this report. The form placeholder `30292@nda.edu.ng` is retained because it is visible placeholder text, not a demonstrated credential.
