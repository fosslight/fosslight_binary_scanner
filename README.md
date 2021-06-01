# FOSSLight Binary

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
- FOSSLight Binary needs a Python 3.6+.    
- To use the function to extract OSS information (OSS name, OSS version, license) from Binary DB, see the [database setting guide][db_guide].

[db_guide]: https://github.com/fosslight/fosslight_binary/blob/main/docs/SETUP_DATABASE.md

## 🎉 How to install
It can be installed using pip3. It is recommended to install it in the [python 3.6 + virtualenv](https://github.com/fosslight/fosslight_source/blob/main/docs/Guide_virtualenv.md) environment.

```
$ pip3 install fosslight_binary
```

## 🚀 How to run
````
$ fosslight_bin -p [path_to_analyze]
````    
### About parameters

| Parameter  | Argument | Description |
| ------------- | ------------- | ------------- |
| h | None | Print help message. | 
| p | String | Path to detect binaries. | 
| o | String | Output directory. | 
| f | String | Output file name. | 
| d | String | DB Connection Information. (ex. postgresql://username:password@host:port/database_name) | 

## 🧐 How it works
1. Extract binaries.
    1-0. Excluding Linked Files from binaries.    
    1-1. Except when the extension is ['png', 'gif', 'jpg', 'bmp', 'jpeg', 'qm', 'xlsx', 'pdf', 'ico', 'pptx', 'jfif', 'docx',
                                   'doc', 'whl', 'xls', 'xlsm', 'ppt', 'mp4', 'pyc', 'plist']            
    1-2. Except when the file type is ['data','timezone data', 'apple binary property list']    
    1-3. Except when the directory is ['.git']    
    1-4. Check "Exclude"    
        - binary is ['fosslight_bin', 'fosslight_bin.exe']     
        - directory is ["test", "tests", "doc", "docs"]     
    1-5. If the -a option is present, output as binary only when the relevant information is included in the file command result.      
2. Extract checksum and tlsh for each binary.     
3. Load OSS information from Binary DB.      
4. Create binary.txt file.          
5. Create excel & csv file.     

## 📁 Result

```
$ tree
.
├── binary.txt
├── fosslight_bin_log_2021-06-01_20-16-46.txt
├── OSS-Report_2021-06-01_20-16-46.csv
└── OSS-Report_2021-06-01_20-16-46.xlsx

```
- OSS-Report_[datetime].xlsx : FOSSLight binary result in OSS Report format.
- OSS-Report_[datetime].csv : FOSSLight binary result in csv format. (Except Windows)
- fosslight_bin_log_[datetime].txt : The execution log.
- binary.txt : The checksum and tlsh values for each binary are printed.

## 💻 Development
### How to make an executable  
````  
$ pip install .  
$ pyinstaller --onefile cli.py
````
### How to test
````  
$ pip install requiremets-dev.txt
$ tox
````

## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [Git Repository][repo]. Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[repo]: https://github.com/fosslight/fosslight_binary/issues

## 📄 License

FOSSLight Binary is Apache-2.0, as found in the [LICENSE][l] file.

[l]: https://github.com/fosslight/fosslight_binary/blob/main/LICENSE
