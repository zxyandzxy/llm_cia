import subprocess

def run_jar(jar_path, *args):
    cmd = ['java', '-jar', jar_path] + list(args)

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_lines = result.stdout.decode().strip().splitlines()
        return output_lines
    except subprocess.CalledProcessError as e:
        return "An error occurred while running the jar file:", e.stderr.decode('utf-8', errors='ignore')
