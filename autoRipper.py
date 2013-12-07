#!/usr/bin/env python

import subprocess
import time
import pygame
import datetime
import argparse

RIPITDIRTEMPLATE = "'\"/$artist/$album\"'"

class AutoRipper():
    def __init__(self,cdDrive,outputPath,timeout):
        self.cdDrive = cdDrive
        self.outputPath = outputPath
        self.timeout = timeout
        self.cdDrive.init()

    def start(self):
        print "AutoRipper - Waiting for Audio Disk"
        #loop until a disk hasnt been inserted within the timeout
        lastTimeDiskFound = datetime.datetime.now()
        while (lastTimeDiskFound + datetime.timedelta(0,self.timeout)) > datetime.datetime.now():
            #is there a disk in the drive?
            if self.cdDrive.get_empty() == False:
                # Disk found
                # is it an audio cd?
                if self.cdDrive.get_track_audio(0) == True:
                    print "AutoRipper - Audio disk found, starting ripit."
                    #run ripit
                    # getting subprocess to run ripit was difficult
                    #  due to the quotes in the --dirtemplate option
                    #   this works though!
                    ripit = subprocess.Popen("ripit --outputdir " + self.outputPath + " --dirtemplate=" + RIPITDIRTEMPLATE + " --nointeraction", shell=True)
                    ripit.communicate()
                    # rip complete - eject disk
                    print "AutoRipper - rip complete, ejecting"
                    # use eject command rather than pygame.cd.eject as I had problems with my drive
                    subprocess.call(["eject"])
                else:
                    print "AutoRipper - Disk inserted isnt an audio disk."
                    subprocess.call(["eject"])
                lastTimeDiskFound = datetime.datetime.now()
                print "AutoRipper - Waiting for disk"
            else:
                # No disk - eject the tray
                subprocess.call(["eject"])
            # wait for a bit, before checking if there is a disk
            time.sleep(5)

        # timed out, a disk wasnt inserted
        print "AutoRipper - timed out waiting for a disk, quitting"
        # close the drawer
        subprocess.call(["eject", "-t"])
        #finished - cleanup
        self.cdDrive.quit()

if __name__ == "__main__":

    print "StuffAboutCode.com Raspberry Pi Auto CD Ripper"

    #Command line options
    parser = argparse.ArgumentParser(description="Auto CD Ripper")
    parser.add_argument("outputPath", help="The location to rip the CD to")
    parser.add_argument("timeout", help="The number of seconds to wait for the next CD")
    args = parser.parse_args()

    #Initialize the CDROM device
    pygame.cdrom.init()

    # make sure we can find a drive
    if pygame.cdrom.get_count() == 0:
        print "AutoRipper - No drives found!"
    elif pygame.cdrom.get_count() > 1:
        print "AutoRipper - More than 1 drive found - this isnt supported - sorry!"
    elif pygame.cdrom.get_count() == 1:
        print "AutoRipper - Drive found - Starting"
        autoRipper = AutoRipper(pygame.cdrom.CD(0),args.outputPath,int(args.timeout))
        autoRipper.start()

    #clean up
    pygame.cdrom.quit()
