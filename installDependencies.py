import sys
import subprocess

installDependencyErrors = 0
installDependencyMessage = ""

# List of packages to install with pip
dependenciesInstall = ["opencv-python", "mss", "pyautogui", "numpy", "pynput", "ttkthemes", "requests", "discord", "pytesseract"]

# List of packages to update with pip
dependenciesUpdate = ["pyscreeze"]

# Make sure pip is updated
print("Checking pip is updated...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
except:
    error = "ERROR: Unable to update pip."
    print(error)
    installDependencyMessage += f"    - {error}\n"
    installDependencyErrors += 1

# Install packages
for dependency in dependenciesInstall:
    print(f"\nInstalling {dependency}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
    except:
        error = f"ERROR: Unable to install {dependency}."
        print(error)
        installDependencyMessage += f"    - {error}\n"
        installDependencyErrors += 1

# Update packages
for dependency in dependenciesUpdate:
    print(f"\nUpdating {dependency}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", dependency])
    except:
        error = f"ERROR: Unable to update {dependency}."
        print(error)
        installDependencyMessage += f"    - {error}\n"
        installDependencyErrors += 1


if installDependencyErrors == 0:
    # Print finished with no errors
    print("\n\nCompleted installing the GachaLogBot Python Dependencies successfully.\n\nYou can now run the main program with:\n    python main.py\n\nOr by double clicking on StartGachaLogBot.bat\n")
    input("Press Enter to close this window...")
else:
    # Report the errors found
    print("\n\nFailed to install the GachaLogBot Python Dependencies.\n\nEncountered the following errors:")
    print(installDependencyMessage)
    print("You must fix these errors to use the GachaLogBot.\n")
    input("Press Enter to close this window...")

