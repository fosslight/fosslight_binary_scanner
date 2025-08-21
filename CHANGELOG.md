# Changelog

## v5.1.9 (21/08/2025)
## Changes
## 🚀 Features

- Exclude package dirs with directory name @dd-jy (#153)

## 🔧 Maintenance

- Copy OSS info for same checksum file @bjk7119 (#149)
- Exclude cases with only oss_ver in jar analysis @bjk7119 (#152)

---

## v5.1.8 (17/07/2025)
## Changes
## 🐛 Hotfixes

- Remove SQL injection vulnerability @bjk7119 (#150)

## 🔧 Maintenance

- Change the minimum Python version to 3.10 @bjk7119 (#151)
- Remove the duplicated comment @bjk7119 (#146)
- Fix workflow waring message @bjk7119 (#145)

---

## v5.1.7 (25/05/2025)
## Changes
## 🔧 Maintenance

- Modify when exceeding the max. url length @bjk7119 (#144)

---

## v5.1.6 (09/05/2025)
## Changes
## 🔧 Maintenance

- Handling of exceeding  max. url length @bjk7119 (#143)
- Import exclude path fct. from FL util @bjk7119 (#142)

---

## v5.1.5 (11/02/2025)
## Changes
## 🐛 Hotfixes

- Fix to print excel file by default @bjk7119 (#141)

---

## v5.1.4 (20/01/2025)
## Changes
- Decode vul. url @bjk7119 (#140)

## 🔧 Maintenance

- Remove duplicates from OSS information loaded from Binary DB @bjk7119 (#139)

---

## v5.1.3 (03/01/2025)
## Changes
## 🔧 Maintenance

- Convert 'TNULL' to '0' value @bjk7119 (#138)

---

## v5.1.2 (05/12/2024)
## Changes
## 🚀 Features

- Support cycloneDX format @dd-jy (#136)

## 🐛 Hotfixes

- Fix to exclude path @bjk7119 (#132)

## 🔧 Maintenance

- Fix the notice screen @ethanleelge (#134)
- Print option name with error msg @bjk7119 (#131)

---

## v5.1.1 (13/10/2024)
## Changes
## 🚀 Features

- Apply simple mode @bjk7119 (#130)

---

## v5.1.0 (08/10/2024)
## Changes
## 🚀 Features

- Support spdx (only Linux) @dd-jy (#126)

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
