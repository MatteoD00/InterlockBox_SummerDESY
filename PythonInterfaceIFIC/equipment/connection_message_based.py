"""
Base class for equipment that use message-based communication.
"""
import socket
import sys
import time
import traceback

from .connection import Connection
from .constants import CR
from .constants import LF
from .exceptions import MSLTimeoutError
from .utils import from_bytes
from .utils import to_bytes


class ConnectionMessageBased(Connection):

    CR = CR
    """:class:`bytes`: The carriage-return character (hex: 0x0D, decimal: 13)."""

    LF = LF
    """:class:`bytes`: The line-feed character (hex: 0x0A, decimal: 10)."""

    def __init__(self, record):
        """Base class for equipment that use message-based communication.

        The :data:`~msl.equipment.record_types.ConnectionRecord.backend`
        value must be equal to :data:`~msl.equipment.constants.Backend.MSL`
        to use this class for the communication system. This is achieved by
        setting the value in the **Backend** field for a connection record
        in the :ref:`connections-database` to be ``MSL``.

        Do not instantiate this class directly. Use the
        :meth:`~.EquipmentRecord.connect` method to connect to the equipment.

        Parameters
        ----------
        record : :class:`.EquipmentRecord`
            A record from an :ref:`equipment-database`.
        """

        self._encoding = 'utf-8'
        p = record.connection.properties

        try:
            termination = p['termination']
        except KeyError:
            self.read_termination = p.get('read_termination', ConnectionMessageBased.LF)
            self.write_termination = p.get('write_termination', ConnectionMessageBased.CR + ConnectionMessageBased.LF)
        else:
            self.read_termination = termination
            self.write_termination = termination

        self.max_read_size = p.get('max_read_size', 1 << 20)  # 1 MB

        self.timeout = p.get('timeout', None)

        self.encoding = p.get('encoding', self._encoding)

        self.encoding_errors = p.get('encoding_errors', 'strict')

        self.rstrip = p.get('rstrip', False)

    @property
    def encoding(self):
        """:class:`str`: The encoding that is used for :meth:`.read` and :meth:`.write` operations."""
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """Set the encoding to use for :meth:`.read` and :meth:`.write` operations."""
        if self._read_termination is None and self._write_termination is None:
            _ = 'test encoding'.encode(encoding).decode(encoding)
        self._encoding = encoding
        if self._read_termination is not None:
            self.read_termination = self._read_termination.decode(encoding)
        if self._write_termination is not None:
            self.write_termination = self._write_termination.decode(encoding)

    @property
    def encoding_errors(self):
        """:class:`str`: The error handling scheme to use when encoding and decoding messages.

        For example: `strict`, `ignore`, `replace`, `xmlcharrefreplace`, `backslashreplace`
        """
        return self._encoding_errors

    @encoding_errors.setter
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

    @property
    def read_termination(self):
        """:class:`bytes` or :data:`None`: The termination character sequence
        that is used for the :meth:`.read` method.

        Reading stops when the equipment stops sending data or the `read_termination`
        character sequence is detected. If you set the `read_termination` to be equal
        to a variable of type :class:`str` it will automatically be encoded.
        """
        return self._read_termination

    @read_termination.setter
    def read_termination(self, termination):
        self._read_termination = self._encode_termination(termination)

    @property
    def write_termination(self):
        """:class:`bytes` or :data:`None`: The termination character sequence that
        is appended to :meth:`.write` messages.

        If you set the `write_termination` to be equal to a variable of type
        :class:`str` it will automatically be encoded.
        """
        return self._write_termination

    @write_termination.setter
    def write_termination(self, termination):
        self._write_termination = self._encode_termination(termination)

    @property
    def max_read_size(self):
        """:class:`int`: The maximum number of bytes that can be :meth:`.read`."""
        return self._max_read_size

    @max_read_size.setter
    def max_read_size(self, size):
        """The maximum number of bytes that can be :meth:`.read`."""
        max_size = int(size)
        if max_size < 1:
            raise ValueError('The maximum number of bytes to read must be > 0, got {}'.format(size))
        self._max_read_size = max_size

    @property
    def timeout(self):
        r""":class:`float` or :data:`None`: The timeout, in seconds, for
        :meth:`.read` and :meth:`.write` operations.

        A value :math:`\lt` 0 will set the timeout to be :data:`None` (blocking mode).
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if value is not None:
            self._timeout = float(value)
            if self._timeout < 0:
                self._timeout = None
        else:
            self._timeout = None
        self._set_backend_timeout()

    def _set_backend_timeout(self):
        # Some connections (e.g. pyserial, socket) need to be notified of the timeout change.
        # The connection subclass must override this method to notify the backend.
        pass

    @property
    def rstrip(self):
        """:class:`bool`: Whether to remove trailing whitespace from :meth:`.read` messages."""
        return self._rstrip

    @rstrip.setter
    def rstrip(self, value):
        self._rstrip = bool(value)

    def raise_timeout(self, append_msg=''):
        """Raise a :exc:`~.exceptions.MSLTimeoutError`.

        Parameters
        ----------
        append_msg : :class:`str`, optional
            A message to append to the generic timeout message.
        """
        msg = 'Timeout occurred after {} seconds. {}'.format(self._timeout, append_msg)
        self.log_error('%r %s', self, msg)
        raise MSLTimeoutError('{!r}\n{}'.format(self, msg))

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
        if size is not None and size > self._max_read_size:
            self.raise_exception('max_read_size is {} bytes, requesting {} bytes'.format(
                self._max_read_size, size))

        message = self._process(self._read, size)

        if size is None:
            self.log_debug('%s.read() -> %r', self, message)
        else:
            if len(message) != size:
                self.raise_exception('received {} bytes, requested {} bytes'.format(
                    len(message), size))
            self.log_debug('%s.read(%s) -> %r', self, size, message)

        if self._rstrip:
            message = message.rstrip()

        if dtype:
            return from_bytes(message, fmt=fmt, dtype=dtype)

        if decode:
            return message.decode(encoding=self._encoding, errors=self.encoding_errors)

        return message

    def _read(self, size):
        """The subclass must override this method."""
        raise NotImplementedError

    def write(self, message, data=None, fmt='ieee', dtype='<f'):
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
            message = message.encode(encoding=self._encoding, errors=self._encoding_errors)

        if data is not None:
            message += to_bytes(data, fmt=fmt, dtype=dtype)

        if self._write_termination and not message.endswith(self._write_termination):
            message += self._write_termination

        self.log_debug('%s.write(%r)', self, message)
        return self._process(self._write, message)

    def _process(self, method, arg):
        """Want to always raise a subclass of MSLConnectionError for a write/read."""
        error, timeout_error = None, None
        try:
            return method(arg)
        except socket.timeout:
            # TODO in 3.10 socket.timeout became a deprecated alias of TimeoutError
            #  Want to raise MSLTimeoutError not socket.timeout
            timeout_error = True
        except MSLTimeoutError:
            raise
        except:
            error = '\n' + ''.join(traceback.format_exception(*sys.exc_info()))

        if timeout_error:
            self.raise_timeout()

        self.raise_exception(error)

    def _write(self, message):
        """The subclass must override this method."""
        raise NotImplementedError

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
        self.write(message)
        if delay > 0:
            time.sleep(delay)
        return self.read(**kwargs)

    def _encode_termination(self, termination):
        # convenience method for setting a termination encoding
        if termination is not None:
            try:
                return termination.encode(self._encoding)
            except AttributeError:
                return termination  # `termination` is already encoded
