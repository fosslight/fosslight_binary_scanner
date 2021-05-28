# FOSSLight Binary

```note
It searches for a binary and outputs OSS information    
if there is an identical or similar binary from the Binary DB.
```

## How to install
````
$ pip install virtualenv  
$ virtualenv -p /usr/bin/python3.6 venv  
$ source venv/bin/activate  
$ pip install fosslight_binary
````

## How to run
````
$ fosslight_bin -p [path_to_analyze]
````    
### About parameters
- p : [Required] path_to_analyze
- a : [Optional] target_architecture
- o : [Optional] Output directory
- f : [Optional] Output file name

## How it works
### 1. Extract binaries.
1-0. Excluding Linked Files from binaries.    
1-1. Except when the extension is ['png', 'gif', 'jpg', 'bmp', 'jpeg', 'qm', 'xlsx', 'pdf', 'ico', 'pptx', 'jfif', 'docx',
                                   'doc', 'whl', 'xls', 'xlsm', 'ppt', 'mp4', 'pyc', 'plist']            
1-2. Except when the file type is ['data','timezone data', 'apple binary property list']    
1-3. Except when the directory is ['.git']    
1-4. Check "Exclude"    
    - binary is ['fosslight_bin', 'fosslight_bin.exe']     
    - directory is ["test", "tests", "doc", "docs"]     
1-5. If the -a option is present, output as binary only when the relevant information is included in the file command result.      
### 2. Extract checksum and tlsh for each binary.     
### 3. Load OSS information from Binary DB.      
### 4. Create binary.txt file.          
### 5. Create excel & csv file.     

## Development
### How to make an executable  
````  
$ pip install .  
$ pyinstaller --onefile cli.py --hidden-import cmath
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