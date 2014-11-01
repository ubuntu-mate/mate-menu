This is MateMenu, a fork of [MintMenu](https://github.com/linuxmint/mintmenu).

  * MateMenu removes the Mint specific search options.
  * Any features that are dependant on Ubuntu Software Center and/or
  Synaptic are only presented in the menus when the required
  applications are installed and execution via `gksu` and `sudo` has
  been replaced with PolicyKit.
  * File, directory and package names have been changed to prevent
  conflicts and I've brought in some components from [mint-common](https://github.com/linuxmint/mint-common)
  so that the MateMenu package can stand alone.

Personally I'm not the least bit interested in using the MateMenu but I 
see that it is regularly requested in the Ubuntu MATE community. So 
consider MateMenu a gift from me, to you :-)

Anyone interested in testing MateMenu I've made packages for Trusty and
Utopic, which you can install from the following PPA:

  * https://launchpad.net/~ubuntu-mate-dev/+archive/ubuntu/ppa
