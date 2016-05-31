from asn1der import *

try:
    from ucollections import OrderedDict
except:
    from collections import OrderedDict
    
try:
    const(1)
except:
    def const(v):
        return v

ERR_NOERROR = const(0x00)
ERR_TOOBIG = const(0x01)
ERR_NOSUCHNAME = const(0x02)
ERR_BADVALUE = const(0x03)
ERR_READONLY = const(0x04)
ERR_GENERR = const(0x05)

TRAP_COLDSTART = const(0x0)
TRAP_WARMSTART = const(0x10)
TRAP_LINKDOWN = const(0x2)
TRAP_LINKUP = const(0x3)
TRAP_AUTHFAIL = const(0x4)
TRAP_EGPNEIGHLOSS = const(0x5)

TypeNames.extend([
        'IPAddr',
        'Counter', 
        'Guage', 
        'TimeTicks',
        'Opaque',
        'NsApAddr',
        'GetRequest',
        'GetNextRequest',
        'GetResponse',
        'SetRequest',
        'Trap'
    ])

TypeCodes.extend([
        0x40,
        0x41, 
        0x42, 
        0x43,
        0x44,
        0x45,
        0xa0,
        0xa1,
        0xa2,
        0xa3,
        0xa4
    ])


class SnmpIPAddr(Asn1DerBaseClass, str):
    typecode = TypeCodes[TypeNames.index('IPAddr')]

    @staticmethod
    def from_bytes(b, t=TypeCodes[TypeNames.index('IPAddr')]):
        ptr = super().from_bytes(b, t=t)
        v = ''
        while ptr < len(b):
            v += '.' + str(b[ptr]) if v!='' else str(b[ptr])
            ptr += 1
        return SnmpIPAddr(v)

    def _to_bytes(self):
        b = bytes()
        for i in self.split('.'):
            b = b + bytes([int(i)])
        return b


class SnmpCounter(Asn1DerInt):    
    typecode = TypeCodes[TypeNames.index('Counter')]
    
    @staticmethod
    def from_bytes(b, t=TypeCodes[TypeNames.index('Counter')], c=SnmpCounter):
        return SnmpCounter( bytes2int(b) )


class SnmpGuage(Asn1DerInt):    
    typecode = TypeCodes[TypeNames.index('Guage')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Guage')]):
        super().frombytes(b, t=t)
        return SnmpGuage( bytes2int(b) )


class SnmpTimeTicks(Asn1DerInt):    
    typecode = TypeCodes[TypeNames.index('TimeTicks')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('TimeTicks')]):
        super().frombytes(b, t=t)
        return SnmpTimeTicks( bytes2int(b) )

class SnmpOpaque(): #not implemented, pending realworld case
    pass 

class SnmpNsApAddr(): #not implemented, pending realworld case
    pass

class SnmpGetRequest(Asn1DerSeq):
    typecode = TypeCodes[TypeNames.index('GetRequest')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('GetRequest')]):
        super().frombytes(b, t=t)
        return SnmpGetNextRequest( bytes2getrequest(b) )
    

class SnmpGetNextRequest(Asn1DerSeq):
    typecode = TypeCodes[TypeNames.index('GetNextRequest')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('GetNextRequest')]):
        super().frombytes(b, t=t)
        return SnmpGetNextRequest( bytes2getrequest(b) )


class SnmpGetResponse(Asn1DerSeq):
    typecode = TypeCodes[TypeNames.index('GetResponse')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('GetResponse')]):
        super().frombytes(b, t=t)
        return SnmpGetNextRequest( bytes2getrequest(b) )


class SnmpSetRequest(Asn1DerSeq):
    typecode = TypeCodes[TypeNames.index('SetRequest')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('SetRequest')]):
        super().frombytes(b, t=t)
        return SnmpGetNextRequest( bytes2getrequest(b) )

    
class SnmpTrap(Asn1DerSeq):
    typecode = TypeCodes[TypeNames.index('Trap')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Trap')]):
        super().frombytes(b, t=t)
        return SnmpGetNextRequest( bytes2getrequest(b) )


TypeClasses.extend([
        SnmpIPAddr,
        SnmpCounter, 
        SnmpGuage, 
        SnmpTimeTicks,
        SnmpOpaque,
        SnmpNsApAddr,
        SnmpGetRequest,
        SnmpGetNextRequest,
        SnmpGetResponse,
        SnmpSetRequest,
        SnmpTrap
    ])
