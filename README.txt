Welcome to CircuitPython!
#############################

Visit the Metro M4 AirLift product page here for more info:
    https://adafruit.com/product/4000

To get started with CircuitPython, which comes built into your Metro, visit:
    https://learn.adafruit.com/welcome-to-circuitpython

#############################

The Metro has a small disk drive so we have disabled Mac OS X indexing
which could take up that valuable space.

So *please* do not remove the empty .fseventsd/no_log, .metadata_never_index
or .Trashes files!

#############################

The pre-loaded demo shows off what your Metro M4 AirLift can do with CircuitPython:

  * WiFi module will scan SSIDs and print them out every few seconds

  * The built in NeoPixel LED can show any color, it will swirl through the rainbow

  * Pin A0 is a true analog output, when buttons on D3 or D4 are pressed to
    ground audio files will play from the onboard storage to A0 (You'll need to
    wire up a speaker or headphones to hear it!

  * Pin A1 is an analog input, the REPL will display the voltage on this pin
    (0-3.3V is the max range)

  * Pin D2, D3 and D4 are digital inputs with pull-ups, you can touch them to
    GND to activate button (or wire up a tactile button or switch!)
    - If you update main.py to uncomment the relevant lines, D2 will act as a
       mini keyboard and emulate an 'a' key-press whenever D2 is grounded.
    - When D3 and D4 are grounded, audio files will play out of A0

  * Pin D5 can be connected to a servo which will sweep back and forth. Power
    the servo from 5V and GND.

  * Pin D6 is a NeoPixel output, you can wire up a strip of NeoPixels to this
    pin (power from USB and GND). The first 16 NeoPixel will rainbow swirl

For more details on how to use CircuitPython, visit
   https://adafruit.com/product/4000
and check out all the tutorials we have!

#############################
CircuitPython Quick Start:

Changing the code is as easy as editing main.py in your favorite text editor.

Our recommended editor is Mu, which is great for simple projects, and comes
with a built in REPL serial viewer! It is available for Mac, Windows & Linux
https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor

After the file is saved, CircuitPython will automatically reload the latest
code. Try enabling the single-button keyboard!
         (HINT: look for the "# optional! uncomment below..." text)

Connecting to the serial port will give you access to sensor information,
better error messages and an interactive CircuitPython (known as the REPL).
On Windows we recommend Mu, Tera Term or PuTTY.
On Mac OSX and Linux, use Mu or 'screen' can be used from a terminal.
