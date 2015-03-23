#coding: UTF-8
import hashlib
import pytest
import sha1

def hash_sha1(data):
    h = hashlib.sha1()
    h.update(data)
    return  h.hexdigest()


def test_sha1():
    data = 'sha-1'
    assert hash_sha1(data) == sha1.calc_sha1(data)
	
#if __name__ == '__main__':
   # test_sha1()
