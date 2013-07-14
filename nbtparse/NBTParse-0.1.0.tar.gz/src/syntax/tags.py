#!/usr/bin/python
"""Types for the various NBT tags.

Every tag type has a corresponding Pythonic class.  Most of these are
subclasses of various built-in classes with additional NBT encoding and
decoding functionality.  Generally speaking, TAG_Foo's counterpart will be
called FooTag.  Most tags are immutable and hashable, and use a values-based
definition of equality; this is usually inherited from the corresponding
built-in class.

The tags all inherit from TagMixin, an abstract mixin class.  TagMixin
provides some method implementations and a great deal of high-level
documentation; if a particular tag's documentation is unclear, consult
TagMixin as well.

TagMixin's implementation of decode_named_tag needs a way to transform tag ids
into subclasses; this system is provided by an instance of TagManager; it is
also used by ListTag for a similar purpose.  Subclasses may replace or
subclass this instance if they wish to alter this behavior.

TagMixin.decode_named_tag is also exposed at the module level for convenience.

This module will also log the encoding and decoding process via tags.logger.
Since encoding and decoding are generally very low-level processes, nearly
everything is logged at the DEBUG level; some irregularities when decoding
are logged at WARNING, and irregularities while encoding will instead generate
ordinary warnings (i.e. warnings.warn()).  See the logging documentation for
instructions on how to access this data or ignore it.
"""
import abc
import struct
import warnings
from functools import total_ordering
import logging
logger = logging.getLogger(__name__)

from . import ids
from .. import exceptions


class TagManager(object):
    """Class to track different types of tags.
    
    Used by TagMixin and friends to decode named tags.

    Intentionally very simple.
    """
    def get_tag_class(self, tag_id):
        """Returns the class corresponding to tag_id."""
        tag_ids = {
                ids.TAG_End: EndTag,
                ids.TAG_Byte: ByteTag,
                ids.TAG_Short: ShortTag,
                ids.TAG_Int: IntTag,
                ids.TAG_Long: LongTag,
                ids.TAG_Float: FloatTag,
                ids.TAG_Double: DoubleTag,
                ids.TAG_Byte_Array: ByteArrayTag,
                ids.TAG_String: StringTag,
                ids.TAG_List: ListTag,
                ids.TAG_Compound: CompoundTag,
                ids.TAG_Int_Array: IntArrayTag,
                }
        try:
            return tag_ids[tag_id]
        except KeyError:
            raise exceptions.NoSuchTagTypeError("{} is not a valid tag type.".
                                                format(tag_id))


class TagMixin(object):
    """Abstract mixin class for tags.

    All NBT tags inherit from TagMixin.
    """
    __metaclass__ = abc.ABCMeta
    manager = TagManager()
    @abc.abstractmethod
    def encode_payload(self, output, errors='strict'):
        """Encode the payload of this tag.

        Writes to output and returns number of bytes written.  Output should
        provide a write() method but is otherwise unconstrained in type.  Note
        that write() must perform any buffering that may be necessary to the
        underlying I/O; write() should write its entire argument, unless
        something has gone wrong.  The built-in file type conforms to these
        requirements when in blocking mode, but other forms of I/O may not.
        If you want to use non-blocking I/O here, look into event-driven
        frameworks; many provide monkey-patched non-blocking file and socket
        implementations.

        If a string needs to be encoded, pass errors to the unicode encoder;
        ignored on tags which don't need to encode strings.  Note that most
        possible values of errors cannot be round-tripped.

        If a value is out of range, an OverflowError may result.
        """
        raise NotImplementedError("TagMixin does not implement encode_payload.")
    @abc.abstractproperty
    def tag_id(self):
        """The ID of this tag (e.g. 1 for a TAG_Byte)."""
        raise NotImplementedError("TagMixin does not implement tag_id.")
    def encode_named(self, name, output, errors='strict'):
        """Encodes this tag with a name (e.g. in a TAG_Compound).

        Writes to output and returns bytes written; see encode_payload for
        some caveats related to this.

        Name should be a unicode object, not a string.

        Errors will be used in encoding the name and payload of this tag.
        """
        total_length = ByteTag(self.tag_id).encode_payload(output)
        total_length += StringTag(name).encode_payload(output, errors)
        total_length += self.encode_payload(output, errors)
        logger.debug("Encoded named tag '%s' to output: %i bytes.", name,
                     total_length)
        return total_length
    warnings.warnpy3k("TagMixin.decode_payload will be abstract in Py3k.",
                      FutureWarning)
    @classmethod
    def decode_payload(cls, input, errors='strict'):
        """Decodes a payload from input.
        
        Reads from input and returns an instance of this tag.  Input should
        provide a read() method but is otherwise unconstrained in type.  Note
        that read() must perform any buffering that may be necessary to the
        underlying I/O; if read() returns less data than was requested, that
        will be interpreted as EOF.  The built-in file type conforms to these
        requirements when in blocking mode, but other forms of I/O may not.
        If you want to use non-blocking I/O here, look into event-driven 
        frameworks; many provide monkey-patched non-blocking file and socket 
        implementations.
        
        If a string needs to be decoded, pass errors to the unicode decoder;
        ignored on tags which don't need to encode strings.
        
        In Python 2.7, abstract class methods are moderately annoying to set
        up, so this method is not abstract.  However, it should always be
        implemented by subclasses, and will become abstract in Python 3.x.
        Importing this module generates a Py3k warning to that effect.  Unless
        you have subclassed TagMixin without implementing this method, you
        can safely ignore that warning.
        """
        raise NotImplementedError("TagMixin does not implement decode_payload.")
    @classmethod
    def decode_named(cls, input, errors='strict'):
        """Decodes a named tag from input and returns (name, tag).

        Reads from input; see decode_payload for some caveats related to this.

        Errors will be passed to the unicode decoder when decoding the name
        and payload.

        Uses a TagManager instance to get the appropriate subclass for
        decoding the payload.
        """
        logger.debug("Decoding named tag...")
        tag_id = ByteTag.decode_payload(input, errors)
        new_cls = cls.manager.get_tag_class(tag_id)
        if tag_id == ids.TAG_End: # TAG_End has no name and no payload
            result = new_cls() # XXX: Special cases are ugly.
            logger.debug("Decoded tag %s.", repr(result))
            return (None, result)
        name = StringTag.decode_payload(input, errors)
        tag = new_cls.decode_payload(input, errors)
        logger.debug("Decoded tag %s named %s.", repr(tag), name)
        return (name, tag)


def _decode_payload_closure(formatstr, length):
    def decode_payload(cls, input, errors='strict'):
        """Decode a fixed-width value from input."""
        raw = input.read(length)
        if len(raw) < length:
            raise exceptions.IncompleteSequenceError("Needed {} bytes, got {}.".
                                                     format(length, len(raw)))
        (value,) = struct.unpack(formatstr, raw)
        result = cls(value)
        logger.debug("Decoded fixed-width tag: %s.", repr(result))
        return result
    return decode_payload

def _encode_payload_closure(formatstr):
    def encode_payload(self, output, errors='strict'):
        """Encode a fixed-width value to output.
		
        If the value is too large to fit into the appropriate representation,
        an OverflowError will result.
        """
        try:
            raw = struct.pack(formatstr, self)
        except struct.error:
            raise OverflowError("%d is too far from zero to encode.", self)
        output.write(raw)
        total_length = len(raw)
        logger.debug("Encoded %s: %i bytes.", repr(self), total_length)
        return total_length
    return encode_payload


@total_ordering
class EndTag(TagMixin):
    """Represents a TAG_End.
    
    EndTags always compare equal to one another, are immutable and hashable, 
    and are considered False by bool().  Subclassing it is probably not
    a great idea.

    For all practical purposes, you can think of EndTag() as the tag
    equivalent of None.

    You probably won't need this very often; TAG_End mostly only shows up as
    the terminating sentinel value for TAG_Compound, and CompoundTag handles
    that automatically.  It's here if you need it, though.
    """
    def __repr__(self):
        return "EndTag()"
    def __hash__(self):
        return hash(None) ^ hash(EndTag) # Always the same value
    def __eq__(self, other):
        return isinstance(other, EndTag) # All EndTags are equal to each other
    def __ne__(self, other):
        return not self == other
    def __lt__(self, other):
        if self == other:
            return False
        else:
            return NotImplemented
    def __nonzero__(self):
        return False
    def encode_payload(self, output, errors='strict'):
        """Does nothing, since TAG_End has no payload."""
        return 0
    @property
    def tag_id(self):
        """Equal to ids.TAG_End."""
        return ids.TAG_End
    def encode_named(self, name, output, errors='strict'):
        """Writes a single null byte to output."""
        output.write(chr(0))
        return 1
    @classmethod
    def decode_payload(cls, input, errors='strict'):
        """Returns an EndTag, without interacting with input at all."""
        return cls()


class ByteTag(TagMixin, int):
    """Represents a TAG_Byte.

    Derives from int, and can be used anywhere an int is valid.
    """
    def __repr__(self):
        return "ByteTag({})".format(super(ByteTag, self).__repr__())
    def __str__(self):
        return super(ByteTag, self).__repr__()
    encode_payload = _encode_payload_closure(">b")
    @property
    def tag_id(self):
        """Equal to ids.TAG_Byte."""
        return ids.TAG_Byte
    decode_payload = _decode_payload_closure(">b", 1)
    decode_payload = classmethod(decode_payload)


class ShortTag(TagMixin, int):
    """Represents a TAG_Short.

    Derives from int, and can be used anywhere an int is valid.
    """
    def __repr__(self):
        return "ShortTag({})".format(super(ShortTag, self).__repr__())
    def __str__(self):
        return super(ShortTag, self).__repr__()
    encode_payload = _encode_payload_closure(">h")
    @property
    def tag_id(self):
        """Equal to ids.TAG_Short."""
        return ids.TAG_Short
    decode_payload = _decode_payload_closure(">h", 2)
    decode_payload = classmethod(decode_payload)


class IntTag(TagMixin, int):
    """Represents a TAG_Int.

    Derives from int, and can be used anywhere an int is valid.
    """
    def __repr__(self):
        return "IntTag({})".format(super(IntTag, self).__repr__())
    def __str__(self):
        return super(IntTag, self).__repr__()
    encode_payload = _encode_payload_closure(">i")
    @property
    def tag_id(self):
        """Equal to ids.TAG_Int."""
        return ids.TAG_Int
    decode_payload = _decode_payload_closure(">i", 4)
    decode_payload = classmethod(decode_payload)


class LongTag(TagMixin, long):
    """Represents a TAG_Long.

    Derives from long, and can be used anywhere a long is valid.
    """
    def __repr__(self):
        return "LongTag({})".format(super(LongTag, self).__repr__())
    def __str__(self):
        return super(LongTag, self).__repr__()
    encode_payload = _encode_payload_closure(">q")
    @property
    def tag_id(self):
        """Equal to ids.TAG_Long."""
        return ids.TAG_Long
    decode_payload = _decode_payload_closure(">q", 8)
    decode_payload = classmethod(decode_payload)


class FloatTag(TagMixin, float):
    """Represents a TAG_Float.

    Derives from float, and can be used anywhere a float is valid.
    """
    def __repr__(self):
        return "FloatTag({})".format(super(FloatTag, self).__repr__())
    def __str__(self):
        return super(FloatTag, self).__repr__()
    encode_payload = _encode_payload_closure(">f")
    @property
    def tag_id(self):
        """Equal to ids.TAG_Float."""
        return ids.TAG_Float
    decode_payload = _decode_payload_closure(">f", 4)
    decode_payload = classmethod(decode_payload)


class DoubleTag(TagMixin, float):
    """Represents a TAG_Double.

    Derives from float, and can be used anywhere a float is valid.
    """
    def __repr__(self):
        return "DoubleTag({})".format(super(DoubleTag, self).__repr__())
    def __str__(self):
        return super(DoubleTag, self).__repr__()
    encode_payload = _encode_payload_closure(">d")
    @property
    def tag_id(self):
        """Equal to ids.TAG_Double."""
        return ids.TAG_Double
    decode_payload = _decode_payload_closure(">d", 8)
    decode_payload = classmethod(decode_payload)


class ByteArrayTag(TagMixin, bytes):
    """Represents a TAG_Byte_Array.
    
    Derives from bytes (which is another name for str), and can be used
    anywhere that bytes would be valid.

    Note that this is generally not used to represent text because it lacks
    encoding information; see StringTag for that.
    """
    def __repr__(self):
        return "ByteArrayTag({})".format(super(ByteArrayTag, self).__repr__())
    def __str__(self):
        return super(ByteArrayTag, self).__str__()
    def encode_payload(self, output, errors='strict'):
        """Writes this tag as a sequence of raw bytes to output.

        Returns the total number of bytes written, including the length.
        """
        logger.debug("Encoding TAG_Byte_Array: %s.", repr(self))
        total_length = IntTag(len(self)).encode_payload(output, errors)
        total_length += len(self)
        output.write(self)
        logger.debug("Encoded TAG_Byte_Array: %i bytes.", total_length)
        return total_length
    @property
    def tag_id(self):
        """Equal to ids.TAG_Byte_Array."""
        return ids.TAG_Byte_Array
    @classmethod
    def decode_payload(cls, input, errors='strict'):
        """Reads a TAG_Byte_Array payload into a new ByteArrayTag."""
        logger.debug("Decoding TAG_Byte_Array...")
        array_len = IntTag.decode_payload(input, errors)
        raw = input.read(array_len)
        if len(raw) < array_len:
            raise exceptions.IncompleteSequenceError(("Expected {} bytes, got"+
                                                      " {}").format(len(raw),
                                                                    array_len))
        result = cls(raw)
        logger.debug("Decoded TAG_Byte_Array: %s.", repr(result))
        return result


class StringTag(TagMixin, unicode):
    """Represents a TAG_String.

    Derives from unicode and can be used anywhere that unicode is valid.
    """
    def __repr__(self):
        return "StringTag({})".format(super(StringTag, self).__repr__())
    def __str__(self):
        return super(StringTag, self).__str__()
    def encode_payload(self, output, errors='strict'):
        """Writes this tag as UTF-8 to output.

        Returns total bytes written, including length.

        Errors is passed to the Unicode encoder.  The default value of
        'strict' will cause any problems (e.g. invalid surrogates) to raise 
        a UnicodeError.
        """
        logger.debug("Encoding TAG_String: %s.", repr(self))
        raw = self.encode('utf_8', errors)
        total_length = ShortTag(len(raw)).encode_payload(output, errors)
        total_length += len(raw)
        output.write(raw)
        logger.debug("Encoded TAG_String: %i bytes.", total_length)
        return total_length
    @property
    def tag_id(self):
        """Equal to ids.TAG_String."""
        return ids.TAG_String
    @classmethod
    def decode_payload(cls, input, errors='strict'):
        """Reads a TAG_String payload into a new StringTag.

        TAG_String is always in UTF-8.

        Errors is passed to the Unicode encoder.  The default value of
        'strict' will cause any problems (e.g. invalid UTF-8) to raise a
        UnicodeError.
        """
        logger.debug("Decoding TAG_String...")
        length = ShortTag.decode_payload(input, errors)
        raw = input.read(length)
        if len(raw) < length:
            raise exceptions.IncompleteSequenceError(("Expected {} bytes, got"+
                                                      " {}").format(len(raw),
                                                                    length))
        result = cls(raw, 'utf_8', errors)
        logger.debug("Decoded TAG_String: %s.", repr(result))
        return result


class ListTag(TagMixin, list):
    """Represents a TAG_List.
    
    Unlike most other tags, this tag is mutable and unhashable.

    instance.content_id identifies the type of the tags listed in this tag.
    During initialization, ListTag will attempt to guess content_id if it is
    not provided.  If the list is empty, it defaults to None and the list
    will not be encodable.
    """
    def __init__(self, iterable=None, content_id=None):
        if iterable is None:
            self._content_id = content_id
            super(ListTag, self).__init__()
            return
        super(ListTag, self).__init__(iterable)
        for tag in self:
            if content_id is None:
                content_id = tag.tag_id
            elif tag.tag_id != content_id:
                raise TypeError("{} has id {}, not {}.".format(repr(tag),
                                                                tag.tag_id,
                                                                content_id))
        self._content_id = content_id # Bypass property since we just checked.
    @property
    def content_id(self):
        """Identifies the tag id of the tags listed in this TAG_List.
        
        Starts at None if the list was initially empty and a content_id was
        not provided.  While this is None, the tag cannot be encoded.

        Can be modified, but doing so will check the id against all tags
        in the list.  foo.content_id = foo.content_id is a quick way to verify
        that all tags are of the correct type.
        """
        return self._content_id
    @content_id.setter
    def content_id(self, value):
        for tag in self:
            if tag.tag_id != value:
                raise TypeError("{} has id {}, not {}.".format(repr(tag),
                                                               tag.tag_id,
                                                               value))
        self._content_id = value
    def __repr__(self):
        return 'ListTag({}, {})'.format(super(ListTag, self).__repr__(),
                                        repr(self.content_id))
    def __str__(self):
        return super(ListTag, self).__str__()
    def __eq__(self, other):
        return (super(ListTag, self).__eq__(other) and
                hasattr(other, "content_id") and
                self.content_id == other.content_id)
    def __ne__(self, other):
        return not self == other
    def __lt__(self, other):
        if super(ListTag, self).__lt__(other):
            return True
        elif super(ListTag, self).__eq__(other):
            if hasattr(other, "content_id"):
                return self.content_id < other.content_id
            else:
                return NotImplemented
        else:
            return False
    # functools.total_ordering won't override list.__gt__ etc.
    # so do it by hand:
    def __gt__(self, other):
        return not self == other and not self < other
    def __ge__(self, other):
        return self > other or self == other
    def __le__(self, other):
        return self < other or self == other
    def encode_payload(self, output, errors='strict'):
        """Encodes a series of tag payloads to output.
        
        Returns the total number of bytes written, including metadata.
        """
        logger.debug("Encoding TAG_List: %s.", repr(self))
        if self.content_id is None:
            raise ValueError("No content_id specified.")
        self.content_id = ByteTag(self.content_id)
        total_length = self.content_id.encode_payload(output, errors)
        total_length += IntTag(len(self)).encode_payload(output, errors)
        for tag in self:
            if tag.tag_id != self.content_id:
                raise TypeError("{} has id {}, not {}.".format(repr(tag),
                                                               tag.tag_id,
                                                               self.content_id))
            total_length += tag.encode_payload(output, errors)
        logger.debug("Encoded TAG_List: %i bytes.", total_length)
        return total_length
    @property
    def tag_id(self):
        """Equal to ids.TAG_List."""
        return ids.TAG_List
    @classmethod
    def decode_payload(cls, input, errors):
        """Decode a list of tags.

        Like TagMixin.decode_named, this method uses cls.manager to determine
        tag class.
        """
        logger.debug("Decoding TAG_List...")
        content_id = ByteTag.decode_payload(input, errors)
        length = IntTag.decode_payload(input, errors)
        result = cls(content_id=content_id)
        item_cls = cls.manager.get_tag_class(content_id)
        for _ in xrange(length):
            next_item = item_cls.decode_payload(input, errors)
            result.append(next_item)
        logger.debug("Decoded TAG_List: %s.", repr(result))
        return result


class CompoundTag(TagMixin, dict):
    """Represents a TAG_Compound.
    
    Unlike most other tags, this tag is mutable and unhashable.

    Derives from dict and may be used in place of one.

    Keys are names, values are tags.

    The terminating TAG_End is handled automatically; you do not need to worry
    about it.

    This implementation does not preserve the order of the tags; this is
    explicitly permitted under the NBT standard.
    """
    def __repr__(self):
        return 'CompoundTag({})'.format(super(CompoundTag, self).__repr__())
    def __str__(self):
        return super(CompoundTag, self).__str__()
    def encode_payload(self, output, errors='strict'):
        """Encodes contents as a series of named tags.
        
        Tags are fully formed, including ids and names.

        Errors is passed to the unicode encoder for encoding names, and to the
        individual tag encoders.
        """
        logger.debug("Encoding TAG_Compound: %s.", repr(self))
        total_length = 0
        for name, tag in self.iteritems():
            if tag == EndTag():
                warnings.warn("Skipping EndTag() in %s." % repr(self))
                continue
            total_length += tag.encode_named(name, output, errors)
        total_length += EndTag().encode_named(None, output, errors)
        logger.debug("Encoded TAG_Compound: %i bytes.", total_length)
        return total_length
    @property
    def tag_id(self):
        """Equal to ids.TAG_Compound."""
        return ids.TAG_Compound
    @classmethod
    def decode_payload(cls, input, errors='strict'):
        """Decodes a series of named tags into a new CompoundTag."""
        logger.debug("Decoding TAG_Compound...")
        result = cls()
        sentinel = EndTag()
        new_name, new_tag = cls.decode_named(input, errors)
        while new_tag != sentinel:
            if new_name in result:
                logger.warn("Found duplicate %s in TAG_Compound, ignoring." %
                            new_name)
                continue
            result[new_name] = new_tag
            new_name, new_tag = cls.decode_named(input, errors)
        logger.debug("Decoded TAG_Compound: %s.", repr(result))
        return result


class IntArrayTag(TagMixin, list):
    """Represents a TAG_Int_Array.

    Unlike most other tags, this tag is mutable and unhashable.

    Derives from list and may be used in place of one.
    """
    def __repr__(self):
        return 'IntArrayTag({})'.format(super(IntArrayTag, self).__repr__())
    def __str__(self):
        return super(IntArrayTag, self).__str__()
    def encode_payload(self, output, errors='strict'):
        """Encodes contents as a series of integers."""
        logger.debug("Encoding TAG_Int_Array: %s.", repr(self))
        cooked = [IntTag(x) for x in self]
        length = IntTag(len(cooked))
        total_length = length.encode_payload(output, errors)
        for tag in cooked:
            total_length += tag.encode_payload(output, errors)
        logger.debug("Encoded TAG_Int_Array: %i bytes.", total_length)
        return total_length
    @property
    def tag_id(self):
        """Equal to ids.TAG_Int_Array."""
        return ids.TAG_Int_Array
    @classmethod
    def decode_payload(cls, input, errors='strict'):
        """Decodes a series of integers into a new IntArrayTag."""
        logger.debug("Decoding TAG_Int_Array...")
        result = cls()
        length = IntTag.decode_payload(input, errors)
        for _ in xrange(length):
            item = IntTag.decode_payload(input, errors)
            result.append(item)
        logger.debug("Decoded TAG_Int_Array: %s.", repr(result))
        return result

decode_named = TagMixin.decode_named
