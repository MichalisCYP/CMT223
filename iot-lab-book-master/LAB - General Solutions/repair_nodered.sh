#/bin/sh

node-red-stop
wget https://nodejs.org/download/release/latest-v19.x/node-v19.9.0-linux-armv7l.tar.gz
tar -xzf node-v19.9.0-linux-armv7l.tar.gz
sudo cp -R node-v19.9.0-linux-armv7l/* /usr/local/
sudo ln -s /usr/local/bin/node /usr/bin/node
sudo ln -s /usr/local/bin/npm /usr/bin/npm
sudo npm uninstall -g node-red
sudo npm install -g --unsafe-perm node-red
sudo npm install node-red-node-serialport
echo "Process completed, now run NodeRed and node-red-node-serialport if not shown in the palette."
