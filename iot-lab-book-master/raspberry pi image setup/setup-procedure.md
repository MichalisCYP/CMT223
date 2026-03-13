

# GrovePi Legacy 32-bit Image Setup Guide

> **Note**  
> This legacy image still receives security updates.  
> The *latest* 64-bit OS image **cannot** be used because its newer kernel driver is incompatible with the GrovePi firmware-flashing process and with low-level I²C tools that rely on older kernel behaviour.



## 1  System Preparation

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y git libncurses5 libusb-0.1-4 unzip
````

Enable **I²C** using **`sudo raspi-config`** if it is not already enabled, **then reboot**:

```bash
sudo reboot
```

---

## 2  Clone Dexter Libraries

> **Do *not* run the curl installer from the repo yet!**

```bash
mkdir -p ~/Dexter/lib
cd ~/Dexter/lib
git clone https://github.com/DexterInd/AVRDUDE.git
git clone https://github.com/DexterInd/GrovePi.git
```

---

## 3  Install AVRDUDE

```bash
cd ~/Dexter/lib/AVRDUDE/avrdude
sudo dpkg -i avrdude_5.10-4_armhf.deb
```

---

## 4  Flash GrovePi Firmware

```bash
cd ~/Dexter/lib/GrovePi/Firmware
sudo ./firmware_update.sh
```

Verify that **`/dev/i2c-1`** exists:

```bash
ls /dev/i2c-*
# You should see: /dev/i2c-1
```

---

## 5  Run GrovePi Update Script

(Errors are expected and safe to ignore)

```bash
curl -kL dexterindustries.com/update_grovepi | bash
```

---

## 6  Clone DI\_Sensors and Set `PYTHONPATH`

```bash
git clone https://github.com/DexterInd/DI_Sensors.git
echo 'export PYTHONPATH=$PYTHONPATH:/home/pi/DI_Sensors/Python' >> ~/.bashrc
source ~/.bashrc
```

---

## 7  Fix Missing **di\_i2c** Dependency

```bash
cd /usr/local/lib/python3.9/dist-packages
sudo unzip grovepi-1.4.1-py3.9.egg -d grovepi_unzipped
sudo cp /home/pi/Dexter/lib/Dexter/RFR_Tools/miscellaneous/di_i2c.py grovepi_unzipped/
sudo rm grovepi-1.4.1-py3.9.egg
sudo mv grovepi_unzipped grovepi
```

---

## 8  Re-install GrovePi Python Library

```bash
cd ~/GrovePi/Software/Python
cp /home/pi/Dexter/lib/Dexter/RFR_Tools/miscellaneous/di_i2c.py .
sudo python3 setup.py install
```

---

## 9  Install Python Dependencies

```bash
sudo apt install -y python3-pip unzip
sudo pip3 install python-periphery
sudo pip3 install wiringpi
```

---

## 10  Verify Installation

```bash
python3 -c "import grovepi; print(grovepi.version())"
# Expected output: 1.4.0
```

Check I²C address map:

```bash
sudo i2cdetect -y -a 1
```

Typical output:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00: -- -- -- -- 04 -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

---

## Contact

Any questions?
Email **[kayanh@cardiff.ac.uk](mailto:kayanh@cardiff.ac.uk)** or message via **Microsoft Teams**.


