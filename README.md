# cowin-slot-availability

This script will search for available CoVID-19 vaccination slots on CoWIN portal after every few seconds. As soon as a slot is available script will notify using a long beep sound.
Also sends an email if provided to be notified through an email.

### Inputs:
1. Date of Slot - This should be mandatorily in dd-mm-yyyy format
2. Age Group - This should be either 18 or 45. Putting any other value might result in invalid data.
3. State - State name for CoWin centre
4. District - Nearest district name for CoWin centre
5. Email Address

### Required Dependencies:
1. winsound
2. requests
3. datetime
4. time
5. smtplib
