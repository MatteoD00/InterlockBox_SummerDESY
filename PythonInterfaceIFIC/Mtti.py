# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 20:18:00 2023

@author: oielsu
"""

import serial
import time
from equipment.utils import from_bytes
from equipment.utils import to_bytes

class Mtti:
    
 running=True
 _encoding = 'utf-8'
 
 EXECUTION_ERROR_CODES = {
    0: ('OK',
        'No error has occurred since this register was last read.'),
    100: ('NumericError',
          'The parameter value sent was outside the permitted range for the command in the present circumstances.'),
    102: ('RecallError',
          'A recall of set up data has been requested but the store specified does not contain any data.'),
    103: ('CommandInvalid',
          'The command is recognised but is not valid in the current circumstances. '
          'Typical examples would be trying to change V2 directly while the outputs are '
          'in voltage tracking mode with V1 as the master.'),
    104: ('RangeChangeError',
          'An operation requiring a range change was requested but could not be completed. '
          'Typically this occurs because >0.5V was still present on output 1 and/or output 2 '
          'terminals at the time the command was executed.'),
    200: ('AccessDenied',
          'An attempt was made to change the instrument\'s settings from an interface which is '
          'locked out of write privileges by a lock held by another interface.')
}
    
 def __init__(self):
        pass
    
 def connect(self):
     self.mtti=serial.Serial('/dev/serial/by-id/usb-TTi_MX_Series_PSU_519890-if00',9800)
     return self.mtti
 
 def close(self):
      self.mtti.close()
      self.running=False

 def encoding_errors(self, value):
        name = str(value).lower()

        if name not in ('strict', 'ignore', 'replace', 'xmlcharrefreplace', 'backslashreplace'):
            err = None
            try:
                u'\u03B2'.encode('ascii', errors=name)
            except LookupError:
                # TODO This avoids nested exceptions. When dropping Python 2.7 support
                #  we can use "raise Exception() from None"
                err = 'unknown encoding error handler {!r}'.format(value)

            if err is not None:
                self.raise_exception(err)

        self._encoding_errors = name
        
 def write_termination(self, termination):
        self._write_termination = self._encode_termination(termination)
 def _encode_termination(self, termination):
        # convenience method for setting a termination encoding
        if termination is not None:
            try:
                return termination.encode(self._encoding)
            except AttributeError:
                return termination  # `termination` is already encoded

 def _read(self):
     

        msg = bytearray()
        now = time.time
        self.mtti.timeout=60
        read = self.mtti.readline()
        r_term="0AH"
        return read
        
                
 def writeMessage(self, message, data=None, fmt='ieee', dtype='<f'):
        """Write a message to the equipment.

        Parameters
        ----------
        message : :class:`str` or :class:`bytes`
            The message to write to the equipment.
        data : :class:`list`, :class:`tuple` or :class:`numpy.ndarray`, optional
            The data to append to `message`.
            See :func:`~msl.equipment.utils.to_bytes` for more details.
        fmt : :class:`str` or :data:`None`, optional
            The format to use to convert `data` to bytes. Ignored if `data` is
            :data:`None`. See :func:`~msl.equipment.utils.to_bytes` for more
            details.
        dtype
            The data type to use to convert each element in `data` to bytes. Ignored
            if `data` is :data:`None`. See :func:`~msl.equipment.utils.to_bytes`
            for more details.

        Returns
        -------
        :class:`int`
            The number of bytes written.
        """
        if isinstance(message, str):
            message = message.encode(encoding=self._encoding)

        if data is not None:
            message += to_bytes(data, fmt=fmt, dtype=dtype)

        if self.write_termination and not message.endswith(self._write_termination):
            message += self._write_termination

        return self.mtti.write(message)
    
    
 def read(self, size=None, fmt='ascii', dtype=None, decode=True):
     """Read a message from the equipment.

     This method will block until one of the following conditions is fulfilled:

     1. the :obj:`.read_termination` byte(s) is(are) received -- only if
        :obj:`.read_termination` is not :data:`None`.
     2. `size` bytes have been received -- only if `size` is not :data:`None`.
     3. a timeout occurs -- only if :obj:`.timeout` is not :data:`None`. An
        :exc:`~msl.equipment.exceptions.MSLTimeoutError` is raised.
     4. :obj:`.max_read_size` bytes have been received. An
        :exc:`~msl.equipment.exceptions.MSLConnectionError` is raised.

     Parameters
     ----------
     size : :class:`int`, optional
         The number of bytes to read. Ignored if it is :data:`None`.
     fmt : :class:`str` or :data:`None`, optional
         The format that the message data is in. Ignored if `dtype` is
         not specified. See :func:`~msl.equipment.utils.from_bytes`
         for more details.
     dtype
         The data type of the elements in the message data. Can be any object
         that :class:`numpy.dtype` supports. See
         :func:`~msl.equipment.utils.from_bytes` for more details. For messages
         that are of scalar type (i.e., a single number) it is more efficient
         to not specify `dtype` but to pass the message to the :class:`int` or
         :class:`float` class to convert the message to the appropriate numeric
         type.
     decode : :class:`bool`, optional
         Whether to decode the message (i.e., convert the message to a
         :class:`str`) or keep the message as :class:`bytes`. Ignored if
         `dtype` is specified.

     Returns
     -------
     :class:`str`, :class:`bytes` or :class:`~numpy.ndarray`
         The message from the equipment. If `dtype` is specified, then the
         message is returned as an :class:`~numpy.ndarray`, if `decode` is
         :data:`True` then the message is returned as a :class:`str`,
         otherwise the message is returned as :class:`bytes`.

     See Also
     --------
     :attr:`.rstrip`
     """

     message = self._read()

     #if self._rstrip:
         #message = message.rstrip()

     if dtype:
         return from_bytes(message, fmt=fmt, dtype=dtype)

     if decode:
         return message.decode(encoding=self._encoding)

     return message
    
 def query(self, message, delay=0.0, **kwargs):
        """Convenience method for performing a :meth:`.write` followed by a :meth:`.read`.

        Parameters
        ----------
        message : :class:`str`
            The message to write to the equipment.
        delay : :class:`float`, optional
            The time delay, in seconds, to wait between :meth:`.write` and
            :meth:`.read` operations.
        **kwargs
            All additional keyword arguments are passed to :meth:`.read`

        Returns
        -------
        :class:`str`, :class:`bytes` or :class:`~numpy.ndarray`
            The message from the equipment. If `dtype` is specified, then the
            message is returned as an :class:`~numpy.ndarray`, if `decode` is
            :data:`True` then the message is returned as a :class:`str`,
            otherwise the message is returned as :class:`bytes`.
        """
        self.writeMessage(message)
        if delay > 0:
            time.sleep(delay)
        return self.read(**kwargs)

 def _check_event_status_register(self, command):
        """Check the value of the standard event status register for an error.
        Parameters
        ----------
        command : :class:`str`
            The command that was sent prior to checking for an error.
        """
        status = self.event_status_register(as_integer=False)
        # Bit 7 - Power On. Set when power is first applied to the instrument.
        # Bit 1 and 6 - Not used, permanently 0.
        # Bit 0 - Operation Complete. Set in response to the *OPC command.
        bit5, bit4, bit3, bit2 = status[2:-2]
        if bit5 == '1':  # Bit 5 - Command Error
            err_type = 'CommandError'
            err_msg = 'A syntax error is detected in a command or parameter'
        elif bit4 == '1':  # Bit 4 - Execution Error
            error_code = int(self.query('EER?').rstrip())
            try:
                err_type, err_msg = self.EXECUTION_ERROR_CODES[error_code]
            except KeyError:
                err_type = 'UndefinedError'
                err_msg = 'The error code {} has not been defined in the Python dict'.format(error_code)
        elif bit3 == '1':  # Bit 3 - Verify Timeout Error
            err_type = 'VerifyTimeoutError'
            err_msg = 'A parameter has been set with "verify" specified ' \
                      'and the value has not been reached within 5 seconds, ' \
                      'e.g. the output voltage is slowed by a load with a large capacitance'
        elif bit2 == '1':  # Bit 2 - Query Error
            err_type = 'QueryError'
            err_msg = 'The controller has not issued commands and read ' \
                      'response messages in the correct sequence'
        else:
            return

        self.raise_exception('{}: {} -> command={!r}'.format(err_type, err_msg, command))
        
 def get_current(self, channel):
        """Get the output current of the output channel.
        Parameters
        ----------
        channel : :class:`int`
            The output channel. The first output channel is 1 (not 0).
        Returns
        -------
        :class:`float`
            The output current, in Amps.
        """
        reply = self.query('I{}O?'.format(channel)).rstrip()
        return float(reply[:-1])
    
 def get_voltage(self, channel):
       """Get the output voltage of the output channel.
       Parameters
       ----------
       channel : :class:`int`
           The output channel. The first output channel is 1 (not 0).
       Returns
       -------
       :class:`float`
           The output voltage, in Volts.
       """
       reply = self.query('V{}O?'.format(channel)).rstrip()
       return float(reply[:-1])
   
 def get_current_limit(self, channel):
    """Get the current limit of the output channel.
    Parameters
    ----------
    channel : :class:`int`
        The output channel. The first output channel is 1 (not 0).
    Returns
    -------
    :class:`float`
        The current limit, in Amps.
    """
    reply = self.query('I{}?'.format(channel)).rstrip()
    return float(reply[2:])
 def get_voltage_setpoint(self, channel):
        """Get the set-point voltage of the output channel.
        Parameters
        ----------
        channel : :class:`int`
            The output channel. The first output channel is 1 (not 0).
        Returns
        -------
        :class:`float`
            The set-point voltage, in Volts.
        """
        reply = self.query('V{}?'.format(channel)).rstrip()
        return float(reply[2:])
 def set_voltage(self, channel, value, verify=True):
        """Set the output voltage of the output channel.
        Parameters
        ----------
        channel : :class:`int`
            The output channel. The first output channel is 1 (not 0).
        value : :class:`float`
            The value, in Volts.
        verify : :class:`bool`, optional
            Whether to verify that the output voltage has stabilized at
            `value` before returning to the calling program.
        """
        #no verificado
        if verify:
            command = 'V{}V {}'.format(channel, value)
        else:
            command = 'V{} {}'.format(channel, value)
        self.writeMessage(command)

 def turn_on(self, channel):
        """Turn the output channel on.
        Parameters
        ----------
        channel : :class:`int`
            The output channel. The first output channel is 1 (not 0).
        """
        #self._write_and_check('OP{} 1'.format(channel))
        command='OP{} 1'.format(channel)
        self.writeMessage(command)
        
 def turn_off(self, channel):
        """Turn the output channel off.
        Parameters
        ----------
        channel : :class:`int`
            The output channel. The first output channel is 1 (not 0).
        """
        #self._write_and_check('OP{} 0'.format(channel))
        command='OP{} 0'.format(channel)
        self.writeMessage(command)
        
        
 def is_output_on(self, channel):
        """Check if the output channel is on or off.
        Parameters
        ----------
        channel : :class:`int`
            The output channel. The first output channel is 1 (not 0).
        Returns
        -------
        :class:`bool`
            Whether the output channel is on (:data:`True`) or off (:data:`False`).
        """
        reply = self._query_and_check('OP{}?'.format(channel))
        """command='OP{}?'.format(channel)
        reply= self.writeMessage(command)"""
        return reply == '1'

 def _query_and_check(self, command):
        """
        Query the command. If there is an error when querying then
        check the event status register for an error.
        """
        try:
            return self.query(command).rstrip()
        except:
            self._check_event_status_register(command)
            # if checking the event status register does not raise an exception
            # then raise the query exception
            raise



