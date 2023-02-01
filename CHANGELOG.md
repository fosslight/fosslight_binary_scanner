# Changelog

## v4.1.18 (01/02/2023)
## Changes
## 🐛 Hotfixes

- Fix to get OSS info from pkg info @bjk7119 (#83)

---

## v4.1.17 (27/01/2023)
## Changes
## 🔧 Maintenance

- Add error handling to analyze jar file @bjk7119 (#82)

---

## v4.1.16 (19/01/2023)
## Changes
## 🔧 Maintenance

- Update package name for ARM Mac @soimkim (#81)
- Change package to get release package @bjk7119 (#80)
- Update version of packages for actions @bjk7119 (#79)

---

## v4.1.15 (02/01/2023)
## Changes
## 🔧 Maintenance

- Use allowlist_externals instead of whitelist_externals @soimkim (#78)

---

## v4.1.14 (18/11/2022)
## Changes
## 🔧 Maintenance

- Modify not to generate binary.txt if no binaries @dd-jy (#76)

---

## v4.1.13 (04/11/2022)
## Changes
## 🔧 Maintenance

- Print license text through notice parameter @dd-jy (#75)

---

## v4.1.12 (06/10/2022)
## Changes
## 🔧 Maintenance

- Modify OSS name from OWASP Result @bjk7119 (#74)
- Change yaml output file name @soimkim (#73)

---

## v4.1.11 (15/09/2022)
## Changes
## 🔧 Maintenance

- Change the output file name @soimkim (#72)

---

## v4.1.10 (13/09/2022)
## Changes
## 🔧 Maintenance

- Fix memory bug when checking file type @soimkim (#71)

---

## v4.1.9 (08/09/2022)
## Changes
## 🐛 Hotfixes

- Fix bug without -p option @bjk7119 (#70)

---

## v4.1.8 (07/09/2022)
## Changes
## 🔧 Maintenance

- Modify output file name for opossum @bjk7119 (#69)
- Remove unnecessary code - print type @bjk7119 (#67)
- Separate the function that checks binary @soimkim (#66)
- Modify help msg if invalid input @bjk7119 (#64)

---

## v4.1.7 (12/08/2022)
## Changes
## 🔧 Maintenance

- Remove the required option from the help message @soimkim (#63)

---

## v4.1.6 (04/08/2022)
## Changes
## 🔧 Maintenance

- Analyze the current path if path is null @soimkim (#62)
- If the result file is not created, do not output it to the log. @soimkim (#61)

---

## v4.1.5 (22/07/2022)
## Changes
## 🔧 Maintenance

- Add progress bar @bjk7119 (#60)
- Modify not to generate .jar analysis file @bjk7119 (#59)

---

## v4.1.4 (17/06/2022)
## Changes
## 🐛 Hotfixes

- Fix memory bug when checking file type on windows @soimkim (#58)

## 🔧 Maintenance

- update the minimum version of fosslight_util @dd-jy (#57)

---

## v4.1.3 (15/06/2022)
## Changes
## 🐛 Hotfixes

- Fix a bug where the current ar archive file is not considered binary. @soimkim (#56)

---

## v4.1.2 (15/06/2022)
## Changes
## 🚀 Features

- Add yaml format for FOSSLight Report @dd-jy (#54)

## 🔧 Maintenance

- Let the binary filter be used externally @soimkim (#55)
- Add a commit message checker @soimkim (#53)

---

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