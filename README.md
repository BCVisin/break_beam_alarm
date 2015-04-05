# Break Beam Alarm

A dual laser break beam sensor system. 

###Details

I needed to set up an alarm system on 2 doors that lead out to the pool area so we will be notified if our children walked outside.  I didn't like the door alarm systems like this http://amzn.com/B0046786U4 since they don't work on the sliding door and the screen door. I wanted a system that checked to see if anyone crossed the door threshold.  A break beam system was in order. I thought the Pi would be a great at this and it would be a fun little project.

I am using the following hardware:
 1. Raspberry Pi A+ - The brains http://amzn.com/B00PEX05TO
 2. Edimax EW-7811Un 150Mbps 11n Wi-Fi USB Adapter - To connect the Pi to the network http://amzn.com/B003MTTJOY
 3. Kingston Digital 8 GB microSDHC - The Pi's memory http://amzn.com/B004S1PNE0
 4. Anker 10000mAh Battery Power Bank - In case of power outage to keep the system running http://amzn.com/B009USAJCC
 5. 2x Laser Diode - LASERS (need I say more?) https://www.adafruit.com/products/1054
 6. 2x Photo Cel (CdS photoresistor) - To detect the light changes when the laser beam is broken, https://www.adafruit.com/products/161
 7. 3x Square Buttons - Tactile reset buttons https://www.adafruit.com/products/1010
 8. USB Powered Speakers - To play various alarm sounds https://www.adafruit.com/products/1363
 9. MCP3008 - 8-Channel 10-Bit ADC - http://www.adafruit.com/products/856
 10. Various resistors for LEDs and the photo cel

![Image of Test Setup](https://raw.githubusercontent.com/BCVisin/break_beam_alarm/master/photos/test_setup_3.jpg)

###Requirements

 - A laser sensor across 2 door frame
 - 2 bypass buttons located on the upper part of the wall by the door so the kids can't reach it
 - When either beam is broken for the first time, it sounds an alarm and turns on an LED
 - When either beam is broken again (before being reset) it sounds a second (different) alarm and truns on a different LED
 - When either bypass button is pushed it will silense and reset the alarms
 - When either bypass button is pushed it will give a grace period (5 seconds?) to pass through the beams without alarms being triggered
 - Ability to run neither, one or the other, or both laser sensors at any give time

###Notes

The script MUST be ran as root since it needs access to the Pi's GPIO ports.
