# Changelog

## v4.1.25 (18/08/2023)
## Changes
## 🔧 Maintenance

- Merge OSS info result to one row @bjk7119 (#99)
- Add test binaries @bjk7119 (#96)
- Update the minimum version of fl util @dd-jy (#98)
- Change the default path to find sbom-info.yaml @dd-jy (#97)

---

## v4.1.24 (02/06/2023)
## Changes
## 🔧 Maintenance

- Update the minimum version of fl util @dd-jy (#98)
- Change the default path to find sbom-info.yaml @dd-jy (#97)

---

## v4.1.23 (19/05/2023)
## Changes
## 🚀 Features

- Add to correct with sbom-info.yaml @dd-jy (#95)

## 🐛 Hotfixes

- Update the ubuntu version for deploy action @dd-jy (#92)
- Bug fix to print jar analysis @bjk7119 (#91)

## 🔧 Maintenance

- Change priority for report @bjk7119 (#94)
- Exclude .dat file to analyze @bjk7119 (#93)

---

## v4.1.22 (27/03/2023)
## Changes
## 🚀 Features

- Add simple mode (-s option) @soimkim (#89)

## 🐛 Hotfixes

- Fix the bug that does not print excel @soimkim (#90)
- Set comment if occurs exception when finding bin @bjk7119 (#87)

---

## v4.1.21 (23/02/2023)
## Changes
## 🔧 Maintenance

- Add the package name to opossum result file @bjk7119 (#88)
- Add the pkg name to log and result file @bjk7119 (#86)

---

## v4.1.20 (17/02/2023)
## Changes
## 🐛 Hotfixes

- Modify typo of set_comment in BinaryItem @bjk7119 (#85)

---

## v4.1.19 (17/02/2023)
## Changes
## 🐛 Hotfixes

- Add error handling to find file path @bjk7119 (#84)

---

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
