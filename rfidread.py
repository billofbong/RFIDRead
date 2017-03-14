#!/usr/bin/python2
import serial
import re, os, time

BITRATE = 9600
register = False
lfile = open("roll") #roll file
index = open("/var/www/html/index.html", "r+") #html homepage
today = open("/var/www/html/" + time.strftime("%Y-%m-%d") + ".html", "w+") #today's file
roll = {} #roll dict

for line in lfile:
    line = line.strip("\n") #remove newline from each
    roll[line] = False #fill the roll dict with the stripped strings with false as the vaulue

sortedRoll = sorted(roll) #make a sorted list from the roll dict
today_write = False #has today been written already?
def writeToday(tfile, rollDict, sortedDict):
    #write html
    tfile.write("<style>table{border-collapse:collapse;}td,th{border:1px solid #dddddd;text-align:left;padding:8px;}tr:nth-child(even) {background-color: #dddddd;})</style>")
    tfile.write("<table>")
    tfile.write("<tr style=\"position:fixed;top:0;background:#FFF;\"><th>Student</th><th>Signed in</th></tr>")
    for item in sortedDict: #use sortedDict in order to get alphabetical order in the table
        tfile.write("<tr><td>" + item + "</td><td>" + str(rollDict[item]) + "</td>") #the values in the dict don't matter
    tfile.write("</table>")
    today.flush() #make sure to write to the file immediately
def deleteContent(pfile): #quick function to delete everything from a file
    pfile.seek(0) #do to start of the file
    pfile.truncate() #delete everything after that
writeToday(today, roll, sortedRoll) #write the table with the preliminary data
for line in index: #check if today's date has been written in the homepage already
    if time.strftime("%Y-%m-%d") in line:
        today_write = True
if not today_write: #write today's date
    index.write("<a href = \"" + time.strftime("%Y-%m-%d") + ".html\">" + time.strftime("%Y-%B-%d") + "</a><br>")
index.close() #make sure to write to the file immediately

if __name__ == '__main__': #make sure this file was run directly
    buffer = '' #init buffer
    ser = serial.Serial('/dev/ttyUSB0', BITRATE, timeout=0) #init serial
    rfidPattern = re.compile(b'[\W_]+') #use regex to match strings that start with b' then any letter then ends with '

    while True:
      # Read data from RFID reader
      cfile = open("cards", "r+") #open cards file
      CARDS = cfile.read().split("\n") #init CARDS list as the cards file split by newlines
      buffer = buffer + ser.read(ser.inWaiting()) #wait for serial information to be sent then add it to buffer
      if '\n' in buffer:
        lines = buffer.split('\n') #split buffer by newline
        last_received = lines[-2] #get the 2nd to last item in lines
        match = rfidPattern.sub('', last_received) #get the string from the regex query
        if match: #if match exists
          if match in CARDS: #if match exists in the CARDS list
            commaSplit = CARDS[CARDS.index(match) - 1].split(',') #split the tied to the rfid card by comma
            commaSplit.reverse() #reverse the list so the first name is first (and to avoid IndexErrors)
            print 'Card authorized. Welcome, ' + commaSplit[0] #print first name
            deleteContent(today) #delete everything from today's file
            roll[CARDS[CARDS.index(match) - 1]] = True #set the person's name's key's value to True LOL
            writeToday(today, roll, sortedRoll) #write the table with the new data  
          else: #if the card is not in the cards folder
            print 'Register this card:' 
            i = 1 
            for item in sortedRoll: #iterate through sortedroll
                print str(i) + ") " + item #print 1-the end of the list) Person's name
                i += 1
            print "0) Cancel"
            num = raw_input("Enter your number: ")
            if num == 0: #if cancel, go back to start
                continue
            i = 1
            for item in sortedRoll: #iterate through sortedRoll
                if int(num) == i: #if the raw_input matches with the number of the person
                    print("Registering card to " + item) #register the card
                    cfile.write(item + "\n" + match + "\n") #print the person's name then the card to the cards file, seperated by a newline
                i += 1
        # Clear buffer
        buffer = ''
        lines = ''
        cfile.close()
        

