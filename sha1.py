#! /usr/bin/python
#coding: UTF-8
import argparse


def writeFile(fname, code):
    try:
        with open(fname, 'wb') as f:
		    f.write(''.join(code))
    except IOError:
        exit('No such file or directory ' + fname)


def readFile(fname):
    try:
        with open(fname, 'rb') as f:
            text = f.read()
    except IOError:
        exit('No such file or directory ' + fname)
    return text		

	
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('inFile')
    parser.add_argument('outFile')
    return parser.parse_args()	
		

# циклический сдвиг влево на n бит
def rotateLeft(x, n): 
    return ((x << n) | (x >> (32-n))) & 0xFFFFFFFF 		
		
# Выравнивание потока и добавление длины сообщения
def alignment(msg):
    msg_len = len(msg) * 8
    msg.append(0x80)
    while len(msg)% 64 != 56:
	    msg += [0]  
    for i in range(7, -1, -1):
        msg.append(msg_len >> i * 8)
        print "data ", msg		  
    return msg			
		
def rounds(buf, x):
    w = x
    w.extend([0]*80)
    # 16 слов по 32-бита дополняются до 80 32-битовых слов:	
    for i in range(16, 80):
        w[i] = rotateLeft((w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]), 1)
		
    # Инициализация хеш-значений этой части:
    a, b, c, d, e =  buf[0],  buf[1],  buf[2],  buf[3],  buf[4]

    #Главный цикл
    for i in range(0, 80):
        if 0 <= i <= 19:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif 20 <= i <= 39:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif 40 <= i <= 59:
            f = (b & c) | (b & d) | (c & d) 
            k = 0x8F1BBCDC
        elif 60 <= i <= 79:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        temp = rotateLeft(a, 5) + f + e + k + w[i] & 0xffffffff
        e = d
        d = c
        c = rotateLeft(b, 30)
        b = a
        a = temp

    buf[0] += a & 0xffffffff
    buf[1] += b & 0xffffffff
    buf[2] += c & 0xffffffff
    buf[3] += d & 0xffffffff
    buf[4] += e & 0xffffffff

    return buf
	
	
def main():
    print "sha1"
    data = ""
    args = getArgs()
    data = readFile(args.inFile)	
    data = [ord(i) for i in data]
	
    # Шаг 1 Выравнивание потока
    # Шаг 2 Добавление длины сообщения
    data = alignment(data)
	
    # Шаг 3 Инициализация буфера
    buf = [0] * 5
    buf[0] = 0x67452301
    buf[1] = 0xefcdab89
    buf[2] = 0x98badcfe
    buf[3] = 0x10325476
    buf[4] = 0xc3d2e1f0
	
	# поток байт  разбиваем на поток слов
    data_words = []
    for i in range(len(data) / 4): 
        q = 0
        for j in range(4):
            q |= data[i * 4 + j] << (3 - j)* 8
        data_words.append(q)
	
    # Шаг 4 Вычисление в цикле
    # разбиваем поток на блоки по 16 слов   
    for i in range(0, len(data_words), 16):
	    # i-ый блок заносится в х 
        x = data_words[i:i+16]
        buf = rounds(buf, x)
			
    # Шаг 5 Результат вычислений 

    res = ""
    for i in buf:
        res += "{:08x}".format(i)
    print "hash: ", res
    writeFile(args.outFile, res)
	
	
if __name__ == "__main__":
    main()	
