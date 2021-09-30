<!--
Copyright (c) 2021 LG Electronics
SPDX-License-Identifier: Apache-2.0
 -->
# FOSSLight Binary Scanner
<img src="https://img.shields.io/pypi/l/fosslight_binary" alt="FOSSLight Binary is released under the Apache-2.0." /> <img src="https://img.shields.io/pypi/v/fosslight_binary" alt="Current python package version." /> <img src="https://img.shields.io/pypi/pyversions/fosslight_binary" /> [![REUSE status](https://api.reuse.software/badge/github.com/fosslight/fosslight_binary_scanner)](https://api.reuse.software/info/github.com/fosslight/fosslight_binary_scanner)

```note
It searches for a binary and outputs OSS information    
if there is an identical or similar binary from the Binary DB.
```


## Contents

- [Prerequisite](#-prerequisite)
- [How to install](#-how-to-install)
- [How to run](#-how-to-run)
- [Result](#-result)
- [Development](#-development)
- [How it works](#-how-it-works)
- [How to report issue](#-how-to-report-issue)
- [License](#-license)


## 📋 Prerequisite
- FOSSLight Binary Scanner needs a Python 3.6+.    
- To use the function to extract OSS information (OSS Name, OSS Version, License) from Binary DB, see the [database setting guide][db_guide].

[db_guide]: https://github.com/fosslight/fosslight_binary/blob/main/docs/SETUP_DATABASE.md

## 🎉 How to install
It can be installed using pip3. It is recommended to install it in the [python 3.6 + virtualenv](https://fosslight.org/fosslight-guide-en/scanner/etc/guide_virtualenv.html) environment.

```
$ pip3 install fosslight_binary
```

## 🚀 How to run
````
$ fosslight_binary -p [path_to_analyze]
````    
### About parameters

| Parameter  | Argument | Description |
| ------------- | ------------- | ------------- |
| h | None | Print help message. | 
| p | String | Path to detect binaries. | 
| o | String | Output directory. | 
| f | String | Output filename. | 
| a | String | Target architecture to output. (ex. x86-64, ARM) | 
| d | String | DB Connection Information. (ex. postgresql://username:password@host:port/database_name) | 

## 🧐 How it works
1. Extract binaries.    
    1-0. Excluding linked files and FIFO files from binaries.    
    1-1. Except when the extension is ['png', 'gif', 'jpg', 'bmp', 'jpeg', 'qm', 'xlsx', 'pdf', 'ico', 'pptx', 'jfif', 'docx',
                                   'doc', 'whl', 'xls', 'xlsm', 'ppt', 'mp4', 'pyc', 'plist']            
    1-2. Except when the file type is ['data','timezone data', 'apple binary property list']    
    1-3. Except when the directory is ['.git']    
    1-4. Check "Exclude"     
        - binary is ['fosslight_bin', 'fosslight_bin.exe']     
        - directory is ["test", "tests", "doc", "docs"]     
    1-5. With the -a option, output as binary only when the relevant information is included in the file command result.      
2. Extract checksum and tlsh for each binary.     
3. Load OSS information from Binary DB.      
4. Create binary.txt file.          
5. Create excel & csv file.     

## 📁 Result

```
$ tree
.
├── binary_20210601_201646.txt
├── fosslight_bin_log_20210601_201646.txt
├── FOSSLight-Report_20210601_201646_BIN.csv
└── FOSSLight-Report_20210601_201646.xlsx

```
- FOSSLight-Report_[datetime].xlsx : FOSSLight binary result in FOSSLight Report format.
- FOSSLight-Report_[datetime]_BIN.csv : FOSSLight binary result in csv format. (Except Windows)
- fosslight_bin_log_[datetime].txt : The execution log.
- binary_[datetime].txt : The checksum and tlsh values for each binary.

## 💻 Development
### How to make an executable  
````  
$ pip install .  
$ pyinstaller --onefile cli.py -n cli --additional-hooks-dir=hooks
````
### How to test
````  
$ pip install requiremets-dev.txt
$ tox
````

## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [Git Repository][repo]. Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[repo]: https://github.com/fosslight/fosslight_binary_scanner/issues

## 📄 License

FOSSLight Binary Scanner is Apache-2.0, as found in the [LICENSE][l] file.

[l]: https://github.com/fosslight/fosslight_binary_scanner/blob/main/LICENSE
