# Changelog

## v4.1.1 (10/03/2022)
## Changes
## 🐛 Hotfixes

- Add error exception handling when checking file type  @soimkim (#51)

## 🔧 Maintenance

- If fetching the binary list fails, exit the program. @soimkim (#52)

---

## v4.1.0 (10/03/2022)
## Changes
## 🐛 Hotfixes

- Fix the bug where results could not be generated due to OWASP error @soimkim (#49)

## 🔧 Maintenance

- Remove the fixed python version when running tox @soimkim (#48)
- Apply f-string format @bjk7119 (#47)

---

## v4.0.9 (24/02/2022)
## Changes
## 🔧 Maintenance

- Add error handle for dependency-check running @bjk7119 (#45)
- Modify LicenseRef-3rd_party_licenses.txt @bjk7119 (#46)
- Set CVE valid time to 24 hours @bjk7119 (#44)

---

## v4.0.8 (14/02/2022)
## Changes
## 🐛 Hotfixes

- Fix to make executable file including 'dependency-check' package @bjk7119 (#43)

## 🔧 Maintenance

- Change the log level related to the output file @soimkim (#39)

---

## v4.0.7 (10/02/2022)
## Changes
## 🔧 Maintenance

- Modify to print output file name @bjk7119 (#37)
- Return a list of successes and results @soimkim (#36)

---

## v4.0.6 (08/02/2022)
## Changes
## 🐛 Hotfixes

- Fix to make executable file with latest version @bjk7119 (#35)
- Fix to local variable assignment issue - extended header @bjk7119 (#33)

---

## v4.0.5 (21/01/2022)
## Changes
## 🚀 Features

- Add vulnerability  column for jar file analysis result @bjk7119 (#30)

---

## v4.0.4 (06/01/2022)
## Changes
## 🐛 Hotfixes

- Do not print comment if there is no information from OWASP @bjk7119 (#29)
- Print the extension to the output file of the result log @soimkim (#27)
- Fix the bug where there is no start time @bjk7119 (#25)

## 🔧 Maintenance

- Remove remained code related to  -a option @bjk7119 (#26)

---

## v4.0.3 (04/01/2022)
## Changes
- Add the -v option to print version @soimkim 
- Delete -a option @bjk7119 (#22)

## 🚀 Features
- Apply OWASP dependency-check to analyze jar file @bjk7119 (#24)


---

## v4.0.2 (21/10/2021)
## Changes
## 🚀 Features

- Add format('-f') option and modify output('-o') option @dd-jy (#20)

## 🔧 Maintenance

- Add format('-f') option and modify output('-o') option @dd-jy (#20)

---

## v4.0.1 (12/10/2021)
## Changes
## 🐛 Hotfixes

- Fix a bug related to printing empty column @soimkim (#19)

---

## v4.0.0 (30/09/2021)
## Changes
## 🔧 Maintenance

- Update documentation @soimkim (#17)
- Add badges to README @soimkim (#16)

---

## v3.5.1 (29/09/2021)
Pre-release.