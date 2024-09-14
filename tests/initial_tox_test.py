import os
import subprocess

def run_command(command): #리눅스 명령어 실행
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    success = result.returncode == 0
    output = result.stdout if success else result.stderr
    return success, output

def test_test_run_environment(): #테스트 환경 tox.ini
    # Given
    run_command("rm -rf test_result")
    os.makedirs("test_result", exist_ok=True)

    # When
    csv_success, _ = run_command("fosslight_bin -p tests -o test_result -f csv")
    exclude_success, _ = run_command("fosslight_bin -p tests -e test commons-logging-1.2.jar -o test_result/exclude_result.csv -f csv")
    files_in_result = run_command("ls test_result/")[1].split()
    txt_success, txt_output = run_command("bash -c 'find test_result -type f -name \"fosslight_binary*.txt\"'")

    # Then
    csv_files = [f for f in files_in_result if f.endswith('.csv')]
    txt_files = txt_output.split()
    success = csv_success and exclude_success and len(csv_files) > 0 and len(txt_files) > 0
    assert success is True, "Test Run Environment: CSV and TXT files not properly created"

def test_release_environment(): #릴리즈 환경 tox.ini
    # Given
    os.makedirs("test_result", exist_ok=True)

    # When
    help_success, _ = run_command("fosslight_bin -h")
    csv_success, _ = run_command("fosslight_bin -p tests -o test_result/result.csv -f csv")
    exclude_csv_success, _ = run_command("fosslight_bin -p tests -e test commons-logging-1.2.jar -o test_result/exclude_result.csv -f csv")
    json_success, _ = run_command("fosslight_bin -p tests -o test_result/result.json -f opossum")
    files_in_result = run_command("ls test_result/")[1].split()
    
    # Then
    required_files = ['result.csv', 'exclude_result.csv', 'result.json']
    files_exist = all(f in files_in_result for f in required_files)
    success = help_success and csv_success and exclude_csv_success and json_success and files_exist
    assert success is True, "Release Environment: Required files not found or failed to execute"