# Break Beam Alarm

A dual laser break beam sensor system. 

###Details

We needed to set up an alarm system on 2 doors that lead out to the pool area so we would be notified if our children walked outside.  I didn't like the door alarm systems since the don't work on the sliding door and the screen door.  I wanted a system that checked to see if anyone crossed the door threshold.  A break beam system was in order.

I am using the following hardware:
 1. Raspberry Pi A+ http://amzn.com/B00PEX05TO
 2. Edimax EW-7811Un 150Mbps 11n Wi-Fi USB Adapter http://amzn.com/B003MTTJOY
 3. Kingston Digital 8 GB microSDHC http://amzn.com/B004S1PNE0
 4. Anker 10000mAh Battery Power Bank http://amzn.com/B009USAJCC
 5. 2x Laser Diode https://www.adafruit.com/products/1054
 6. 2x Photo Cel (CdS photoresistor) https://www.adafruit.com/products/161
 7. 3x Square Buttons https://www.adafruit.com/products/1010
 8. USB Powered Speakers https://www.adafruit.com/products/1363
 9. Various resistors for LEDs and the photo cel

###Requirements

 - A laser sensor across 2 door frame
 - 2 bypass buttons located on the upper part of the wall by the door so the kids can't reach it
 - When either beam is broken for the first time, it sounds an alarm and turns on an LED
 - When either beam is broken again (before being reset) it sounds a second (different) alarm and truns on a different LED
 - When either bypass button is pushed it will silense and reset the alarms
 - When either bypass button is pushed it will give a grace period (5 seconds?) to pass through the beams without alarms being triggered
 - Ability to run neither, one or the other, or both laser sensors at any give time
