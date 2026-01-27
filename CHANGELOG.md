# Changelog

## v5.1.18 (27/01/2026)
## Changes
## 🔧 Maintenance

- Use hidden dir for intermeditate to fix scan count @bjk7119 (#174)

---

## v5.1.17 (23/01/2026)
## Changes
## 🔧 Maintenance

- Remove unnecessary abspath @bjk7119 (#173)
- Replace default exclusion to FL_Util @soimkim (#172)

---

## v5.1.16 (16/01/2026)
## Changes
## 🔧 Maintenance

- Add function for getting excluded path @bjk7119 (#171)
- Fix yarn.lock detection issue @bjk7119 (#170)

---

## v5.1.15 (24/12/2025)
## Changes
## 🔧 Maintenance

- Update supported format @dd-jy (#169)

---

## v5.1.14 (28/11/2025)
## Changes
## 🔧 Maintenance

- Improve Java version detection logic @bjk7119 (#168)

---

## v5.1.13 (26/11/2025)
## Changes
## 🔧 Maintenance

- Use double quotes for -e option @bjk7119 (#167)
- Skip jar analysis when Java <11 @bjk7119 (#166)

---

## v5.1.12 (04/11/2025)
## Changes
## 🔧 Maintenance

- Add dependency-check license to 3rd party lic. @bjk7119 (#165)
- Modify to upload release assets @bjk7119 (#164)

---

## v5.1.11 (03/11/2025)
## Changes
## 🔧 Maintenance

- Additional Modify publish-release.yml to release in PYPI @bjk7119 (#161)
- Modify publish-release.yml to release in PYPI @bjk7119 (#160)
- Add dependency-check script file @bjk7119 (#158)

---

## v5.1.10 (22/10/2025)
## Changes
## 🔧 Maintenance

- Use Dependency-check v12.1.7 to analyze .jar @bjk7119 (#156)
- Add network and DB connection status logging @bjk7119 (#154)

---

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
