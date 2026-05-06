---
title: "TAALED, TAALES, TAASSC set-up guide"
subtitle: "Using the Suite of Language Analysis Tools"
toc: true
---

# Overview

This guide will help you install and set up three powerful linguistic analysis tools:

- **TAALED** (Tool for the Automatic analysis of LExical Diversity) - Version 1.4.1
- **TAALES** (Tool for the Automatic analysis of Lexical Sophistication) - Version 2.2  
- **TAASSC** (Tool for the Automatic analysis of Syntactic Sophistication and Complexity) - Version 1.3.8

All three tools are Java applications that require proper Java installation and may need security settings adjustments to run properly on your system.

# Common Setup: Java Installation

## What is Java and Why Do You Need It?

Java is a programming platform that these linguistic analysis tools are built on. You need either the Java Development Kit (JDK) or Java Runtime Environment (JRE) installed on your computer to run these applications.

## Recommended Java Versions

For optimal compatibility with TAALED, TAALES, and TAASSC, we recommend:
- **Java 8 (JDK 1.8)** or **Java 11 (LTS)** for maximum compatibility
- **Java 17 (LTS)** or **Java 21 (LTS)** for newer systems

## Java Installation Instructions

### Option 1: Oracle JDK (Recommended for beginners)

**For Windows:**
1. Visit the [Oracle Java Downloads page](https://www.oracle.com/java/technologies/downloads/)
2. Select your operating system (Windows)
3. Download the installer (`.exe` file) for Java 11 or Java 17
4. Run the installer and follow the installation wizard
5. Accept the license agreement and complete installation

**For macOS:**
1. Visit the [Oracle Java Downloads page](https://www.oracle.com/java/technologies/downloads/)
2. Select macOS and download the `.dmg` file
3. Double-click the downloaded file and follow installation instructions
4. You may need to allow the installation in System Preferences > Security & Privacy

**For Linux (Ubuntu/Debian):**
1. Download the `.deb` package from Oracle's website, or
2. Use the terminal commands:
```bash
sudo apt update
sudo apt install default-jdk
```

### Option 2: OpenJDK (Free and Open Source)

**For Windows:**
1. Visit [Microsoft Build of OpenJDK](https://learn.microsoft.com/en-us/java/openjdk/download)
2. Download the Windows installer
3. Run the installer and follow the setup wizard

**For macOS:**
1. Install using Homebrew (recommended):

```bash
brew install openjdk@11
```
1. Or download from [OpenJDK website](https://openjdk.org/install/)

**For Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# Fedora/CentOS/RHEL
sudo yum install java-11-openjdk-devel
```

## Verifying Java Installation

After installation, verify Java is properly installed:

**Windows:**
1. Open Command Prompt (Press Win + R, type `cmd`, press Enter)
2. Type: `java -version`
3. You should see Java version information

**macOS/Linux:**
1. Open Terminal
2. Type: `java -version`
3. You should see Java version information

If you see version information, Java is successfully installed!

## Setting JAVA_HOME (Windows only)

If you encounter issues, you may need to set the JAVA_HOME environment variable:

1. Find your Java installation directory (usually `C:\Program Files\Java\jdk-[version]`)
2. Right-click "This PC" → Properties → Advanced System Settings
3. Click "Environment Variables"
4. Under "System Variables," click "New"
5. Variable name: `JAVA_HOME`
6. Variable value: Your Java installation path
7. Click "OK" to save
8. Find the "Path" variable, click "Edit"
9. Add a new entry: `%JAVA_HOME%\bin`
10. Click "OK" to save all changes

# TAALED Setup (Version 1.4.1)

## About TAALED

TAALED is an analysis tool designed to calculate a wide variety of lexical diversity indices. Homographs are disambiguated using part of speech tags, and indices are calculated using lemma forms. It processes plain text files and produces CSV output for analysis.

## Download and Installation

1. **Download TAALED 1.4.1:**
   - Visit: https://www.linguisticanalysistools.org/taaled.html
   - Click on "TAALED 1.4.1" download link
   - The file will be downloaded as a `.jar` or `.zip` file

2. **Extract the Files:**
   - If downloaded as `.zip`, extract all files to a folder (e.g., `TAALED_1.4.1`)
   - If downloaded as `.jar`, place it in a dedicated folder

3. **Running TAALED:**
   - Double-click the `.jar` file, or
   - Open Terminal/Command Prompt, navigate to the TAALED folder, and run:
   ```bash
   java -jar TAALED_1.4.1.jar
   ```

## Security Settings

### For macOS Users:

**Gatekeeper Security Warning:**
If you see "TAALED cannot be opened because it is from an unidentified developer":

1. **Method 1 - One-time Override:**
   - Right-click (Control+click) on the TAALED `.jar` file
   - Select "Open" from the context menu
   - Click "Open" in the security dialog

2. **Method 2 - System Preferences:**
   - Go to System Preferences > Security & Privacy > General
   - If you see "TAALED was blocked from use because it is not from an identified developer"
   - Click "Open Anyway"

3. **Method 3 - Terminal Command (Advanced):**
   ```bash
   sudo spctl --add /path/to/TAALED_1.4.1.jar
   ```

### For Windows Users:

**Windows Defender SmartScreen:**
If Windows blocks the application:

1. When you see "Windows protected your PC," click "More info"
2. Click "Run anyway" 
3. Or temporarily disable SmartScreen:
   - Settings > Update & Security > Windows Security > App & browser control
   - Set "Check apps and files" to "Warn" or "Off"

**Java Security Settings:**
1. Open Java Control Panel:
   - Windows: Control Panel > Java
   - Or search "Configure Java" in Start menu
2. Go to Security tab
3. Set Security Level to "Medium" (if available) or "High"
4. Click "Edit Site List" and add local file paths if needed

# TAALES Setup (Version 2.2)

## About TAALES

TAALES is a tool that measures over 400 classic and new indices of lexical sophistication, and includes indices related to a wide range of sub-constructs. It provides comprehensive index diagnostics and coverage output.

## Download and Installation

1. **Download TAALES 2.2:**
   - Visit: https://www.linguisticanalysistools.org/taales.html
   - Download the version appropriate for your system:
     - **Windows:** TAALES 2.2 for Windows (64-bit)
     - **macOS:** TAALES 2.2 for Mac (Note: Not compatible with Big Sur or later)
     - **Linux:** TAALES 2.2 for Linux

2. **Installation:**
   - **Windows:** Extract the downloaded `.zip` file to a folder
   - **macOS:** Mount the `.dmg` file and copy the application
   - **Linux:** Extract the `.tar.gz` file to a directory

3. **Running TAALES:**
   - **Windows/Linux:** Double-click the `.jar` file or run from command line
   - **macOS:** Double-click the application bundle

## Security Settings

### For macOS Users:

**Important Note:** TAALES 2.2 is not compatible with macOS Big Sur (11.0) or later versions. Use an older macOS version or consider alternatives.

Follow the same Gatekeeper bypass procedures as described in the TAALED section above.

### For Windows Users:

Follow the same security procedures as described in the TAALED section above.

**Additional Java Security Settings:**
1. After running TAALES for the first time, if you encounter security warnings:
2. Open Java Control Panel > Security
3. Add the TAALES installation directory to the Exception Site List:
   - Click "Edit Site List"
   - Click "Add"
   - Enter: `file:///path/to/taales/directory`
   - Click "OK"

# TAASSC Setup (Version 1.3.8)

## About TAASSC

TAASSC is an advanced syntactic analysis tool. It measures a number of indices related to syntactic development. Included are classic indices of syntactic complexity (e.g., mean length of T-unit) and fine-grained indices of phrasal (e.g., number of adjectives per noun phrase) and clausal (e.g., number of adverbials per clause) complexity.

## Download and Installation

1. **Download TAASSC 1.3.8:**
   - Visit: https://www.linguisticanalysistools.org/taassc.html
   - Download TAASSC version 1.3.8 for your operating system

2. **Installation:**
   - Extract the downloaded file to a dedicated folder
   - Ensure all files are in the same directory

3. **Running TAASSC:**
   - Double-click the main `.jar` file, or
   - Run from command line:
   ```bash
   java -jar TAASSC_1.3.8.jar
   ```

## Security Settings

Follow the same security setting procedures described for TAALED and TAALES above, adapting the file names and paths as needed.

# Common Issues and Troubleshooting

## Java Issues

**"Java not found" or "Java is not recognized":**
- Ensure Java is properly installed
- Check that JAVA_HOME is set correctly (Windows)
- Restart your computer after Java installation

**"Unsupported major.minor version" error:**
- This means the application requires a newer version of Java
- Install Java 8 or higher

## Security Issues

**Applications won't start due to security restrictions:**
- Follow the security bypass procedures for your operating system
- Consider temporarily lowering security settings during installation
- Add the application directories to your Java security exceptions

**macOS Gatekeeper repeatedly blocks applications:**
- Try the `sudo spctl --add` command for persistent permissions
- Consider signing the applications yourself (advanced users)

## Performance Issues

**Applications run slowly:**
- Increase Java memory allocation:
```bash
java -Xmx2g -jar application.jar
```
- Close other applications to free up system resources

**Large file processing issues:**
- For large text corpora, increase memory further:
```bash
java -Xmx4g -jar application.jar
```

# Best Practices

## File Organization

1. **Create dedicated folders** for each tool to avoid conflicts
2. **Keep input files organized** in clearly labeled directories
3. **Save output files** with descriptive names including date and tool used

## Security Management

1. **Only bypass security for trusted applications** from official sources
2. **Return security settings to default** after installation
3. **Keep Java updated** for security patches

## Citations

When using these tools in your research, please cite:

**For TAALED:**
Kyle, K., Crossley, S. A., & Jarvis, S. (2021). Assessing the validity of lexical diversity using direct judgements. Language Assessment Quarterly 18(2), pp. 154-170.

**For TAALES:**
Kyle, K. & Crossley, S. A. (2015). Automatically assessing lexical sophistication: Indices, tools, findings, and application. TESOL Quarterly 49(4), pp. 757-786.

Kyle, K., Crossley, S. A., & Berger, C. (2018). The tool for the analysis of lexical sophistication (TAALES): Version 2.0. Behavior Research Methods 50(3), pp. 1030-1046.

**For TAASSC:**
Kyle, K. (2016). Measuring syntactic development in L2 writing: Fine grained indices of syntactic complexity and usage-based indices of syntactic sophistication (Doctoral Dissertation).

# Additional Resources

- **Official Documentation:** Check each tool's website for user manuals and updates
- **Community Support:** Look for user forums and FAQ sections on the official websites
- **Alternative Tools:** Consider web-based alternatives if local installation proves problematic

# Support

If you encounter issues not covered in this guide:

1. Check the official websites for updated documentation
2. Look for community forums and user groups
3. Contact the tool developers through their official channels
4. Consider using older versions if compatibility issues persist

---

*Last updated: January 2025*
