GRIFFIN-SOH
===========

###Emergency Scripts
`/ShellScripts` contain two scripts for managing shack temperature alarms:
 - `emailWarning.sh` sends an email to the address written at the end of the command
 - `VMEshutdown.sh` shuts down VMEs 1-7, if they were correctly named `VME-01` - `VME-07`


###VME Setup
Everything in `VME/` is from K. Olchanski unless otherwise noted - thanks!

The VME frontend of choice is located in `VME/frontends/fewiener`.  The easiest thing to do is make 7 copies of this directory as `VME-1` to `VME-7`;
EDIT from Adam Jan 2015: /*Rather than creating 7 different directories we have created 7 versions of the executable file only. They reside in the frontends folder of the 'VME' folder.*/
 then:

 - change each `FE_NAME` and `EQ_NAME` to something appropriate, like `grifvps0x` and `VME-0x` respectively
 - `make` in each directory
 - run all the frontends; they will immediately fail, you'll have to write the hostname of the VME crate into the ODB under `/Equipment/VME-0x/Settings/Hostname`
 - run the frontends again; if all is well they should stay up
 - set `/Equipment/VME-0x/Settings/EnableControl` and `mainSwitch` (same path) both to 1.

VME x can now be toggled on/off by flipping the bit at `/Equipment/VME-0x/Settings/mainSwitch`.

###Epics & Agilent frontends
As found in `epics` and `39470A2`; should run mostly out of the box.

###`Alarms` configuration
An example of how to configure the `Alarms` ODB directory is recorded in `alarmConfig`.

###Troubleshooting
You'll need to give the midas user permissions to access the serial connection to the agilent; something like 
`sudo usermod -a -G dialout grifsoh`

where `dialout` is the group of the serial port as listed in `/dev`


####Notes
39470A2 has been taken from old tigsoh01

epics directory checked out from standard tigress daq svn

Makefile.inc copied from tigress daq svn r96


