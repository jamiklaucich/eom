from msl.equipment.resources import NKT
from msl.equipment.exceptions import NKTError 
from msl.equipment import (
    EquipmentRecord,
    ConnectionRecord,
    Backend,
)
class rf:
    def __init__(self, system, ID):
        self.system = system
        self.ID = ID

    @property
    def power(self):
        read = self.system.register_read_u8(self.ID, 0x30)
        return read

    @power.setter
    def power(self, val):
        read = self.system.register_write_read_u8(self.ID, 0x30, int(val))
        return read

    @property
    def wavelength(self, channel=0):
        read = self.system.register_read_u32(self.ID, hex(0x90+channel))
        return read

    @wavelength.setter
    def wavelength(self, wav, channel=0):
        read = self.system.register_write_read_u32(self.ID, 0x90, int(wav*1E3), 0)
        return read

    @property
    def channel_amplitude(self, channel=0):
        read = self.system.register_read_u16(self.ID, hex(0xB0+channel))
        return read

    @channel_amplitude.setter
    def channel_amplitude(self, amplitude, channel=0):
        read = self.system.register_write_read_u16(self.ID, hex(0xB0+channel), amplitude*10, 0)
        return read
    
class evo:
    def __init__(self, system, ID):
        self.system = system
        self.ID = ID

    def module_status(self):
        print('Module Status: {!r}'.format(self.system.get_port_status()))
        print('The following modules are available in the device:')
        for module, DEVICE_ID in self.system.get_modules().items():
            print('  ModuleType={} DeviceID={}'.format(module, DEVICE_ID))
            print('    Status bits: {}'.format(self.system.device_get_status_bits(DEVICE_ID)))
            print('    Type: 0x{:04x}'.format(self.system.device_get_type(DEVICE_ID)))
            print('    Firmware Version#: {}'.format(self.system.device_get_firmware_version_str(DEVICE_ID)))
            print('    Serial#: {}'.format(self.system.device_get_module_serial_number_str(DEVICE_ID)))
            try:
                print('    PCB Serial#: {}'.format(self.system.device_get_pcb_serial_number_str(DEVICE_ID)))
            except NKTError:
                print('    PCB Serial#: Not Available')
            try:
                print('    PCB Version#: {}'.format(self.system.device_get_pcb_version(DEVICE_ID)))
            except NKTError:
                print('    PCB Version#: Not Available')
            print('    Is Live?: {}'.format(self.system.device_get_live(DEVICE_ID)))
    
    @property
    def emission(self):
        read = self.system.register_read_u8(self.ID, 0x30)
        return read
    
    @emission.setter
    def emission(self, emission):
        if(emission):
            read = self.system.register_write_read_u8(self.ID, 0x30, 2)
        if(not emission):
            read = self.system.register_write_read_u8(self.ID, 0x30, 0)
        return read

    def setup(self, val):
        read = self.system.register_write_read_u16(self.ID, 0x31, val)
        return read
    
    @property
    def interlock(self):
        read = self.system.register_read_u16(self.ID, 0x32)
        return read
    
    @interlock.setter
    def interlock(self, val):
        read = self.system.register_write_read_u16(self.ID, 0x32, val)

    def interlock_reset(self):
        interlock = self.interlock

        if(interlock==1):
            self.interlock(1)
            interlock = self.interlock
        if(not interlock):
            print("Interlock Reset")
        return interlock