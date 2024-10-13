# Changelog

## v5.1.1 (13/10/2024)
## Changes
## 🚀 Features

- Apply simple mode @bjk7119 (#130)

---

## v5.1.0 (08/10/2024)
## Changes
## 🚀 Features

- Support spdx @dd-jy (#126)

## 🔧 Maintenance

- Refactor existing tox test to pytest @s-cu-bot (#123)

---

## v5.0.0 (06/09/2024)
## Changes
## 🔧 Maintenance

- Refactoring OSS Item classes @soimkim (#121)

---

## v4.1.33 (06/09/2024)
## Changes
## 🔧 Maintenance

- Limit installation to fosslight_util 1.4.* @soimkim (#120)
- Exclude specific file and folder @bjk7119 (#118)

---

## v4.1.32 (24/07/2024)
## Changes
## 🚀 Features

- Enable multiple input for -f option @JustinWonjaePark (#117)

---

## v4.1.31 (21/06/2024)
## Changes
- Bug fix to run executable on Windows @bjk7119 (#116)

## 🔧 Maintenance
- Modify to print binary DB result @bjk7119 (#115)

---

## v4.1.30 (10/06/2024)
## Changes
- Remove related to binary.txt @bjk7119 (#112)

## 🚀 Features

- Supports for excluding paths @SeongjunJo (#109)

## 🐛 Hotfixes

- Bug fix to print column @bjk7119 (#114)

## 🔧 Maintenance

- Modify column name @bjk7119 (#113)
- Update help message @SeongjunJo (#111)
- Change the cover message @dd-jy (#110)
- Analyze image and icon extension file @bjk7119 (#108)

---

## v4.1.29 (07/05/2024)
## Changes
## 🔧 Maintenance

- Print tlsh, sha1 if no oss info at report @bjk7119 (#106)

---

## v4.1.28 (26/04/2024)
## Changes
## 🚀 Features

- Add detection summary message (cover sheet) @dd-jy (#107)

---

## v4.1.27 (25/03/2024)
## Changes
## 🔧 Maintenance

- Change column name : checksum -> SHA1 @bjk7119 (#105)

---

## v4.1.26 (20/03/2024)
## Changes
## 🚀 Features

- Add TLSH and checksum column at report @bjk7119 (#104)

## 🐛 Hotfixes

- Exclude 'json' and 'js' file @bjk7119 (#103)

## 🔧 Maintenance

- Use common github actions @bjk7119 (#101)

---

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
